import asyncio
import json
import logging
import os
import shutil
from asyncio.futures import Future
from tempfile import TemporaryFile
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)

import delta.serialize
import numpy as np
from delta.algorithm.horizontal import HorizontalAlgorithm
from delta.node import Node
from delta.task import HorizontalTask
from delta_node import chain, commu, config, entity, pool, registry, serialize, utils
from delta_node.crypto import aes, ecdhe, shamir

from .dataset import new_train_val_dataloader
from .loc import (
    task_config_file,
    task_dir,
    task_metrics_file,
    task_result_file,
    task_state_file,
    task_weight_file,
)
from .runner import TaskRunner

if TYPE_CHECKING:
    from multiprocessing.synchronize import Condition as mCondition
    from threading import Condition as tCondition

    CondtionType = Union[mCondition, tCondition]


_logger = logging.getLogger(__name__)


class HFLNode(Node):
    def __init__(self, task_id: str, round: int) -> None:
        self.task_id = task_id
        self._round = round

    @property
    def round(self) -> int:
        return self._round

    def new_dataloader(
        self,
        dataset: str,
        validate_frac: float,
        cfg: Dict[str, Any],
        preprocess: Callable,
    ) -> Tuple[Iterable, Iterable]:
        dataset_loc = os.path.join(config.data_dir, dataset)
        return new_train_val_dataloader(dataset_loc, validate_frac, cfg, preprocess)

    def download(self, type: str, dst: IO[bytes]) -> bool:
        if type == "state":
            return self.download_state(dst)
        elif type == "weight":
            return self.download_weight(dst)
        else:
            raise ValueError(f"unknown download type {type}")

    def upload(self, type: str, src: IO[bytes]):
        if type == "state":
            self.upload_state(src)
        elif type == "result":
            self.upload_result(src)
        elif type == "metrics":
            self.upload_metrics(src)
        else:
            raise ValueError(f"unknown upload type {type}")

    def upload_state(self, src: IO[bytes]):
        with open(task_state_file(self.task_id), mode="wb") as dst:
            shutil.copyfileobj(src, dst)

    def upload_result(self, src: IO[bytes]):
        with open(task_result_file(self.task_id, self.round), mode="wb") as dst:
            shutil.copyfileobj(src, dst)

    def upload_metrics(self, src: IO[bytes]):
        with open(task_metrics_file(self.task_id, self.round), mode="wb") as dst:
            shutil.copyfileobj(src, dst)

    def download_state(self, dst: IO[bytes]) -> bool:
        filename = task_state_file(self.task_id)
        if os.path.exists(filename):
            with open(task_state_file(self.task_id), mode="rb") as src:
                shutil.copyfileobj(src, dst)
                return True
        else:
            return False

    def download_weight(self, dst: IO[bytes]) -> bool:
        filename = task_weight_file(self.task_id, self.round - 1)
        if os.path.exists(filename):
            with open(filename, mode="rb") as src:
                shutil.copyfileobj(src, dst)
            return True
        return False


def run_task(task_id: str, round: int):
    with open(task_config_file(task_id), mode="rb") as file:
        task = delta.serialize.load_task(file)
        node = HFLNode(task_id, round)
        task.run(node)
    _logger.info(
        f"task {task_id} round {round} calculation finished", extra={"task_id": task_id}
    )


class HFLTaskRunner(TaskRunner):
    def __init__(self, task: entity.RunnerTask) -> None:
        self.task_id = task.task_id
        self.dataset = task.dataset
        self.commitment = task.commitment
        self.url = task.url

        self.client = commu.get_client(self.url)

        self.algorithm: Optional[HorizontalAlgorithm] = None

        self.round_runner: Optional["HFLRoundRunner"] = None
        self.current_task: Optional[Future] = None

    async def dispatch(self, event: entity.Event):
        if event.type == "task_created":
            await self.start()
        elif event.type == "round_started":
            assert isinstance(event, entity.RoundStartedEvent)
            await self.start_round(event)
        elif event.type == "partner_selected":
            assert isinstance(event, entity.PartnerSelectedEvent)
            await self.partner_selected(event)
        elif event.type == "calculation_started":
            assert isinstance(event, entity.CalculationStartedEvent)
            await self.start_calculating(event)
        elif event.type == "aggregation_started":
            assert isinstance(event, entity.AggregationStartedEvent)
            await self.start_aggregating(event)
        elif event.type == "round_ended":
            assert isinstance(event, entity.RoundEndedEvent)
            await self.end_round(event)

    async def start(self):
        def download_task():
            with open(task_config_file(self.task_id), mode="w+b") as file:
                self.client.download_task_config(self.task_id, file)
                file.seek(0)
                task = delta.serialize.load_task(file)
                return task

        loop = asyncio.get_running_loop()
        task = await loop.run_in_executor(pool.IO_POOL, download_task)
        assert isinstance(task, HorizontalTask)
        self.algorithm = task.algorithm()
        _logger.info(
            f"task {self.task_id} download task config", extra={"task_id": self.task_id}
        )

    async def start_round(self, event: entity.RoundStartedEvent):
        if self.round_runner is None:
            self.round = event.round
            self.round_runner = HFLRoundRunner(self, event.round)
            self.current_task = asyncio.create_task(self.round_runner.start())
            await self.current_task
            self.current_task = None
        else:
            await self.finish_round()

    async def partner_selected(self, event: entity.PartnerSelectedEvent):
        if (
            self.round_runner
            and self.round_runner.round == event.round
            and self.current_task is None
        ):
            try:
                self.current_task = asyncio.create_task(
                    self.round_runner.partner_selected(event)
                )
                await self.current_task
            except:
                self.round_runner = None
            finally:
                self.current_task = None

    async def start_calculating(self, event: entity.CalculationStartedEvent):
        if (
            self.round_runner
            and self.round_runner.round == event.round
            and self.current_task is None
        ):
            try:
                self.current_task = asyncio.create_task(
                    self.round_runner.start_calculating(event)
                )
                await self.current_task
            except:
                self.round_runner = None
            finally:
                self.current_task = None

    async def start_aggregating(self, event: entity.AggregationStartedEvent):
        if (
            self.round_runner
            and self.round_runner.round == event.round
            and self.current_task is None
        ):
            try:
                self.current_task = asyncio.create_task(
                    self.round_runner.start_aggregating(event)
                )
                await self.current_task
            except:
                self.round_runner = None
            finally:
                self.current_task = None

    async def end_round(self, event: entity.RoundEndedEvent):
        if self.round_runner and self.round_runner.round == event.round:
            await self.finish_round()

    async def finish_round(self):
        if self.current_task:
            self.current_task.cancel()
            self.current_task = None
        if self.round_runner:
            await self.round_runner.finish()
            self.round_runner = None

    async def finish(self):
        await self.finish_round()

        def rm_dir():
            dirname = task_dir(self.task_id)
            if os.path.exists(dirname):
                shutil.rmtree(dirname)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(pool.IO_POOL, rm_dir)
        _logger.info(f"task {self.task_id} finish", extra={"task_id": self.task_id})


class HFLRoundRunner(object):
    def __init__(self, task_runner: "HFLTaskRunner", round: int) -> None:
        self.task_id = task_runner.task_id
        assert task_runner.algorithm is not None
        self.algorithm = task_runner.algorithm
        self.round = round
        self.client = task_runner.client
        self.status: entity.RoundStatus = entity.RoundStatus.STARTED

        self.sk1: Optional[bytes] = None
        self.sk2: Optional[bytes] = None
        self.seed: Optional[bytes] = None

        self.pk1s: Dict[str, bytes] = {}
        self.pk2s: Dict[str, bytes] = {}

        self.share_key1s: Dict[str, bytes] = {}

        self.seed_shares: Dict[str, bytes] = {}
        self.sk_shares: Dict[str, bytes] = {}

        self.u1: List[str] = []
        self.u2: List[str] = []
        self.u3: List[str] = []

    @property
    def precision(self) -> int:
        return self.algorithm.precision

    @property
    def curve(self):
        return ecdhe.CURVES[self.algorithm.curve]

    async def start(self):
        self.status = entity.RoundStatus.STARTED
        sk1, pk1 = ecdhe.generate_key_pair(curve=self.curve)
        sk2, pk2 = ecdhe.generate_key_pair(curve=self.curve)

        node_adderss = await registry.get_node_address()

        tx_hash = await chain.get_client().join_round(
            node_adderss, self.task_id, self.round, pk1, pk2
        )
        _logger.info(
            f"try to join in task {self.task_id} round {self.round}",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

        self.sk1 = sk1
        self.sk2 = sk2

    async def partner_selected(self, event: entity.PartnerSelectedEvent):
        assert (
            self.status == entity.RoundStatus.STARTED
        ), "round is not in started phase"
        assert self.sk1 is not None and self.sk2 is not None, "haven't start round"

        node_address = await registry.get_node_address()
        if node_address not in event.addrs:
            self.status = entity.RoundStatus.FINISHED
            return
        self.u1 = event.addrs
        _logger.info(
            f"join in task {self.task_id} round {self.round}",
            extra={"task_id": self.task_id},
        )

        pks = await chain.get_client().get_client_public_keys(
            self.task_id, self.round, event.addrs
        )
        pk1s, pk2s = zip(*pks)
        _logger.debug("get client pks")

        share_key1s = []
        for addr, pk1, pk2 in zip(event.addrs, pk1s, pk2s):
            self.pk1s[addr] = pk1
            self.pk2s[addr] = pk2
            share_key1 = ecdhe.generate_shared_key(self.sk1, pk1, curve=self.curve)
            share_key1s.append(share_key1)
            self.share_key1s[addr] = share_key1
            _logger.debug(
                f"{node_address[:8]} -> {addr[:8]} share key {serialize.bytes_to_hex(share_key1)[:8]}"
            )
        _logger.debug("generate shared keys for communication")

        self.seed = os.urandom(32)
        _logger.debug(f"{node_address} seed {serialize.bytes_to_hex(self.seed)}")

        ss = shamir.SecretShare(self.algorithm.min_clients)

        seed_shares = ss.make_shares(self.seed, len(event.addrs))
        _logger.debug(
            f"{node_address} seed shares {[serialize.bytes_to_hex(share) for share in seed_shares]}"
        )
        for receiver, share in zip(event.addrs, seed_shares):
            _logger.debug(
                f"{node_address[:8]} -> {receiver[:8]} seed share {serialize.bytes_to_hex(share)[:8]}"
            )
        _logger.debug("make seed shares")
        sk_shares = ss.make_shares(self.sk2, len(event.addrs))
        for receiver, share in zip(event.addrs, sk_shares):
            _logger.debug(
                f"{node_address[:8]} -> {receiver[:8]} sk share {serialize.bytes_to_hex(share)[:8]}"
            )
        _logger.debug("make sk shares")

        seed_commitments = [utils.calc_commitment(share) for share in seed_shares]
        _logger.debug("generate seed share commitments")
        sk_commitments = [utils.calc_commitment(share) for share in sk_shares]
        _logger.debug("generate sk share commitments")

        enc_seed_shares = [
            aes.encrypt(key, share) for key, share in zip(share_key1s, seed_shares)
        ]
        for addr, share in zip(event.addrs, enc_seed_shares):
            _logger.debug(
                f"{node_address[:8]} -> {addr[:8]} enc seed share {serialize.bytes_to_hex(share)[:8]}"
            )
        _logger.debug("encrypt seed shares")
        enc_sk_shares = [
            aes.encrypt(key, share) for key, share in zip(share_key1s, sk_shares)
        ]
        for addr, share in zip(event.addrs, enc_sk_shares):
            _logger.debug(
                f"{node_address[:8]} -> {addr[:8]} enc sk share {serialize.bytes_to_hex(share)[:8]}"
            )
        _logger.debug("encrypt sk shares")

        tx_hash = await chain.get_client().upload_seed_commitment(
            node_address,
            self.task_id,
            self.round,
            event.addrs,
            seed_commitments,
        )
        _logger.debug("upload seed share commitments")
        _logger.info(
            f"task {self.task_id} round {self.round} upload seed secret share commitments",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )
        tx_hash = await chain.get_client().upload_secret_key_commitment(
            node_address,
            self.task_id,
            self.round,
            event.addrs,
            sk_commitments,
        )
        _logger.debug("upload sk share commitments")
        _logger.info(
            f"task {self.task_id} round {self.round} upload secret key secret share commitments",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

        ss_datas = [
            entity.SecretShareData(
                sender=node_address,
                receiver=receiver,
                seed=seed_share,
                secret_key=sk_share,
            )
            for receiver, seed_share, sk_share in zip(
                event.addrs, enc_seed_shares, enc_sk_shares
            )
        ]

        for data in ss_datas:
            _logger.debug(
                f"{data.sender[:8]} -> {data.receiver[:8]} seed share {serialize.bytes_to_hex(data.seed)[:8]}"
            )
            _logger.debug(
                f"{data.sender[:8]} -> {data.receiver[:8]} secret key share {serialize.bytes_to_hex(data.secret_key)[:8]}"
            )

        await self.client.upload_secret_shares(
            node_address, self.task_id, self.round, ss_datas
        )
        _logger.debug("upload secret shares to coordinator")
        _logger.info(
            f"task {self.task_id} round {self.round} upload secret shares",
            extra={"task_id": self.task_id},
        )
        self.status = entity.RoundStatus.RUNNING

    async def start_calculating(self, event: entity.CalculationStartedEvent):
        assert (
            self.status == entity.RoundStatus.RUNNING
        ), "round is not in running phase"
        assert len(self.share_key1s) > 0

        node_address = await registry.get_node_address()

        if node_address not in event.addrs:
            self.status = entity.RoundStatus.FINISHED
            return
        self.u2 = event.addrs

        # get and check secret shares
        ss_commitments = await chain.get_client().get_secret_share_datas(
            self.task_id, self.round, event.addrs, node_address
        )
        _logger.debug("get secret shares")
        ss_datas = await self.client.get_secret_shares(
            node_address, self.task_id, self.round
        )
        _logger.debug("get secret share commitments")
        for data in ss_datas:
            _logger.debug(
                f"{data.sender[:8]} -> {data.receiver[:8]} enc seed share {serialize.bytes_to_hex(data.seed)[:8]}"
            )
            _logger.debug(
                f"{data.sender[:8]} -> {data.receiver[:8]} enc secret key share {serialize.bytes_to_hex(data.secret_key)[:8]}"
            )

        try:
            seed_shares = {
                ss.sender: aes.decrypt(self.share_key1s[ss.sender], ss.seed)
                for ss in ss_datas
            }
            for sender, share in seed_shares.items():
                _logger.debug(
                    f"{sender[:8]} -> {node_address[:8]} seed share {serialize.bytes_to_hex(share)[:8]}"
                )
            sk_shares = {
                ss.sender: aes.decrypt(self.share_key1s[ss.sender], ss.secret_key)
                for ss in ss_datas
            }
            for sender, share in sk_shares.items():
                _logger.debug(
                    f"{sender[:8]} -> {node_address[:8]} secret key share {serialize.bytes_to_hex(share)[:8]}"
                )
            _logger.debug("decrypt secret share commitments")
        except Exception as e:
            _logger.exception(e)
            raise

        seed_commitments = {ss.sender: ss.seed_commitment for ss in ss_commitments}
        sk_commitments = {ss.sender: ss.secret_key_commitment for ss in ss_commitments}
        for sender in seed_shares:
            share = seed_shares[sender]
            commitment = seed_commitments.get(sender, None)
            if commitment and utils.calc_commitment(share) == commitment:
                self.seed_shares[sender] = share
        for sender in sk_shares:
            share = sk_shares[sender]
            commitment = sk_commitments.get(sender, None)
            if commitment and utils.calc_commitment(share) == commitment:
                self.sk_shares[sender] = share
        _logger.debug("check secret share commitments")
        _logger.info(
            f"task {self.task_id} round {self.round} get and validate other members' secret shares",
            extra={"task_id": self.task_id},
        )

        loop = asyncio.get_running_loop()

        def download_weight():
            filename = task_weight_file(self.task_id, self.round - 1)
            with open(filename, mode="wb") as dst:
                self.client.download_task_weight(self.task_id, self.round - 1, dst)
            _logger.info(
                f"task {self.task_id} round {self.round} download task weight",
                extra={"task_id": self.task_id},
            )

        def upload_result():
            filename = task_result_file(self.task_id, self.round)

            weight_arr = delta.serialize.load_arr(filename)
            _logger.debug(f"weight arr {weight_arr}")
            masked_weight_arr = self.mask_arr(weight_arr, node_address, event.addrs)
            _logger.debug(f"mask arr {masked_weight_arr}")
            with TemporaryFile(mode="w+b") as file:
                delta.serialize.dump_arr(file, masked_weight_arr)
                file.seek(0)
                self.client.upload_task_round_result(
                    node_address, self.task_id, self.round, file
                )
                _logger.info(
                    f"task {self.task_id} round {self.round} upload masked result",
                    extra={"task_id": self.task_id},
                )
                file.seek(0)
                commitment = utils.calc_commitment(file)
                _logger.debug(f"calculate commitment of task round {self.round} result")
                return commitment

        def upload_metrics():
            filename = task_metrics_file(self.task_id, self.round)

            if os.path.exists(filename):
                with open(filename, mode="r", encoding="utf-8") as f:
                    metrics: Dict[str, Any] = json.load(f)

                keys = sorted(metrics.keys())
                values = np.array([metrics[key] for key in keys])
                masked_values = self.mask_arr(values, node_address, event.addrs)

                masked_metrics = {
                    key: val for key, val in zip(keys, masked_values.tolist())
                }
                self.client.upload_task_round_metrics(
                    node_address,
                    self.task_id,
                    self.round,
                    masked_metrics,
                )
                _logger.info(
                    f"task {self.task_id} round {self.round} upload masked metrics",
                    extra={"task_id": self.task_id},
                )

        await loop.run_in_executor(pool.IO_POOL, download_weight)
        await loop.run_in_executor(pool.RUNNER_POOL, run_task, self.task_id, self.round)

        commitment = await loop.run_in_executor(pool.IO_POOL, upload_result)
        tx_hash = await chain.get_client().upload_result_commitment(
            node_address, self.task_id, self.round, commitment
        )
        _logger.info(
            f"task {self.task_id} round {self.round} upload result commitment",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )

        await loop.run_in_executor(pool.IO_POOL, upload_metrics)
        self.status = entity.RoundStatus.CALCULATING

    def mask_arr(
        self, arr: np.ndarray, node_address: str, addrs: List[str]
    ) -> np.ndarray:
        assert self.seed is not None
        assert self.sk2 is not None
        assert len(self.pk2s) > 0

        seed_mask = utils.make_mask(self.seed, arr.shape)
        sk_mask = np.zeros_like(arr, np.int64)

        for addr in addrs:
            if node_address != addr:
                pk2 = self.pk2s[addr]
                key = ecdhe.generate_shared_key(self.sk2, pk2, self.curve)
                mask = utils.make_mask(key, arr.shape)
                if node_address < addr:
                    sk_mask -= mask
                else:
                    sk_mask += mask

        _logger.debug(f"seed mask {seed_mask}")
        _logger.debug(f"sk mask {sk_mask}")
        res = utils.fix_precision(arr, self.precision) + seed_mask + sk_mask  # type: ignore
        return res

    async def start_aggregating(self, event: entity.AggregationStartedEvent):
        assert (
            self.status == entity.RoundStatus.CALCULATING
        ), "round is not in calculating phase"
        assert self.seed_shares is not None
        assert self.sk_shares is not None

        node_address = await registry.get_node_address()

        if node_address not in event.addrs:
            self.status = entity.RoundStatus.FINISHED
            return
        self.u3 = event.addrs

        dead_members = list(set(self.u2) - set(self.u3))
        alive_members = self.u3
        if len(dead_members) > 0:
            _logger.info(
                f"task {self.task_id} round {self.round} dead members {dead_members}",
                extra={"task_id": self.task_id},
            )
        _logger.info(
            f"task {self.task_id} round {self.round} alive members {alive_members}",
            extra={"task_id": self.task_id},
        )

        sk_shares: List[bytes] = []
        for addr in dead_members:
            sk_shares.append(self.sk_shares[addr])
        seed_shares: List[bytes] = []
        for addr in alive_members:
            seed_shares.append(self.seed_shares[addr])

        if len(sk_shares) > 0:
            tx_hash = await chain.get_client().upload_secret_key(
                node_address,
                self.task_id,
                self.round,
                dead_members,
                sk_shares,
            )
            _logger.info(
                f"task {self.task_id} round {self.round} upload dead members' secret key secret shares",
                extra={"task_id": self.task_id, "tx_hash": tx_hash},
            )
        tx_hash = await chain.get_client().upload_seed(
            node_address,
            self.task_id,
            self.round,
            alive_members,
            seed_shares,
        )
        _logger.info(
            f"task {self.task_id} round {self.round} upload alive members' seed secret shares",
            extra={"task_id": self.task_id, "tx_hash": tx_hash},
        )
        self.status = entity.RoundStatus.AGGREGATING

    async def finish(self):
        def _finish():
            weight_file = task_weight_file(self.task_id, self.round)
            result_file = task_result_file(self.task_id, self.round)
            metrics_file = task_metrics_file(self.task_id, self.round)

            for file in [weight_file, result_file, metrics_file]:
                if os.path.exists(file):
                    os.remove(file)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(pool.IO_POOL, _finish)
        _logger.info(
            f"task {self.task_id} round {self.round} finish",
            extra={"task_id": self.task_id},
        )
