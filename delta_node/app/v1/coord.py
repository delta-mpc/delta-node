from __future__ import annotations

import json
import logging
import os
import shutil
import time
from io import BytesIO
from tempfile import gettempdir
from typing import Dict, List

import sqlalchemy as sa
from delta.core.task import DataLocation, DataNode
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget

from delta_node import coord, db, entity
from delta_node.utils import random_str
from delta_node.serialize import bytes_to_hex, dump_obj, hex_to_bytes

_logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coord")


class CommonResp(BaseModel):
    success: bool = True


@router.get("/config")
def get_task_config(task_id: str = Query(..., regex=r"0x[0-9a-fA-F]+")):
    config_filename = coord.loc.task_config_file(task_id)
    retry = 3
    if not os.path.exists(config_filename):
        retry -= 1
        if retry == 0:
            raise HTTPException(400, f"task {task_id} does not exist")
        else:
            time.sleep(2)

    def file_iter():
        chunk_size = 1024 * 1024
        with open(config_filename, mode="rb") as f:
            while True:
                content = f.read(chunk_size)
                if len(content) == 0:
                    break
                yield content

    return StreamingResponse(
        file_iter(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={task_id}.config"},
    )


@router.get("/context")
def get_task_context(
    task_id: str = Query(..., regex=r"0x[0-9a-fA-F]+"), name: str = Query(...)
):
    manager = coord.get_task_manager(task_id)
    if manager is None:
        raise HTTPException(400, f"task {task_id} has not started or has finished")
    datanode = DataNode(name=name, location=DataLocation.SERVER)
    value = manager.ctx.get(datanode)[0]

    def value_iter():
        chunk_size = 1024 * 1024
        with BytesIO() as f:
            dump_obj(f, value)
            f.seek(0)
            while True:
                content = f.read(chunk_size)
                if len(content) == 0:
                    break
                yield content

    return StreamingResponse(
        value_iter(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={task_id}_{name}.ctx"},
    )


class TaskRound(BaseModel):
    address: str
    task_id: str
    round: int


class SecretShare(BaseModel):
    sender: str
    receiver: str
    seed_share: str = Field(..., regex=r"0x[0-9a-fA-F]+")
    sk_share: str = Field(..., regex=r"0x[0-9a-fA-F]+")


class SecretShares(TaskRound):
    shares: List[SecretShare]


@router.post("/secret_shares", response_model=CommonResp)
async def upload_secret_share(
    shares: SecretShares, session: AsyncSession = Depends(db.get_session)
):
    q = sa.select(entity.Task).where(entity.Task.task_id == shares.task_id)
    task: entity.Task | None = (await session.execute(q)).scalars().one_or_none()
    if task is None:
        raise HTTPException(400, "task does not exist")

    if task.type == "horizontal":
        te = entity.horizontal
    elif task.type == "hlr":
        te = entity.hlr
    else:
        raise HTTPException(400, f"unknown task type {task.type}")

    q = (
        sa.select(te.TaskRound)
        .where(te.TaskRound.task_id == shares.task_id)
        .where(te.TaskRound.round == shares.round)
    )
    round = (await session.execute(q)).scalars().one_or_none()
    if not round:
        raise HTTPException(400, "task round does not exist")
    if round.status != te.RoundStatus.RUNNING:
        raise HTTPException(400, "round is not in running phase")

    # get members in running phase
    q = (
        sa.select(te.RoundMember)
        .where(te.RoundMember.status == te.RoundStatus.RUNNING)
        .where(te.RoundMember.round_id == round.id)
    )
    members = (await session.execute(q)).scalars().all()
    member_addrs = [member.address for member in members]
    if shares.address not in member_addrs:
        raise HTTPException(400, f"member ${shares.address} is not allowed")

    if len(shares.shares) != len(member_addrs):
        raise HTTPException(400, "should share to all members in RUNNING phase")

    if not all(share.sender == shares.address for share in shares.shares):
        raise HTTPException(400, "all share senders should be equal to member address")

    member_dict = {member.address: member for member in members}
    sender = member_dict[shares.address]

    for share in shares.shares:
        receiver = member_dict[share.receiver]
        ss = te.SecretShare(
            sender.id,
            receiver.id,
            hex_to_bytes(share.seed_share),
            hex_to_bytes(share.sk_share),
        )
        ss.sender = sender
        ss.receiver = receiver
        session.add(ss)
    await session.commit()

    _logger.info(
        f"task {shares.task_id} round {shares.round} {shares.address} upload secret shares",
        extra={"task_id": shares.task_id},
    )
    return CommonResp()


@router.get("/secret_shares", response_model=SecretShares)
async def get_secret_shares(
    address: str,
    task_id: str,
    round: int,
    session: AsyncSession = Depends(db.get_session),
):
    q = sa.select(entity.Task).where(entity.Task.task_id == task_id)
    task: entity.Task | None = (await session.execute(q)).scalars().one_or_none()
    if task is None:
        raise HTTPException(400, "task does not exist")

    if task.type == "horizontal":
        te = entity.horizontal
    elif task.type == "hlr":
        te = entity.hlr
    else:
        raise HTTPException(400, f"unknown task type {task.type}")

    q = (
        sa.select(te.TaskRound)
        .where(te.TaskRound.task_id == task_id)
        .where(te.TaskRound.round == round)
    )
    round_entity = (await session.execute(q)).scalars().one_or_none()
    if not round_entity:
        raise HTTPException(400, "task round does not exist")
    if round_entity.status != te.RoundStatus.CALCULATING:
        raise HTTPException(400, "round is not in calculating phase")

    q = (
        sa.select(te.RoundMember)
        .where(te.RoundMember.round_id == round_entity.id)
        .where(te.RoundMember.address == address)
        .options(selectinload(te.RoundMember.received_shares))
    )
    member = (await session.execute(q)).scalars().one_or_none()
    if not member:
        raise HTTPException(400, f"member {address} does not exists")
    if member.status != te.RoundStatus.CALCULATING:
        raise HTTPException(400, f"member {address} is not allowed")

    sender_ids = [share.sender_id for share in member.received_shares]
    q = sa.select(te.RoundMember).where(te.RoundMember.id.in_(sender_ids))  # type: ignore
    senders = (await session.execute(q)).scalars().all()

    sender_dict = {sender.id: sender for sender in senders}
    shares = []
    for share in member.received_shares:
        sender = sender_dict[share.sender_id]
        shares.append(
            SecretShare(
                sender=sender.address,
                receiver=address,
                seed_share=bytes_to_hex(share.seed_share),
                sk_share=bytes_to_hex(share.sk_share),
            )
        )
    resp = SecretShares(
        address=address,
        task_id=task_id,
        round=round,
        shares=shares,
    )
    _logger.info(
        f"task {task_id} round {round} {address} get secret shares",
        extra={"task_id": task_id},
    )
    return resp


async def parse_upload_result_request(req: Request):
    result_filename = os.path.join(gettempdir(), "delta_" + random_str(10) + ".result")

    address_target = ValueTarget()
    task_id_target = ValueTarget()
    round_target = ValueTarget()
    file_target = FileTarget(result_filename)

    parser = StreamingFormDataParser(req.headers)
    parser.register("file", file_target)
    parser.register("address", address_target)
    parser.register("task_id", task_id_target)
    parser.register("round", round_target)

    async for chunk in req.stream():
        await run_in_threadpool(parser.data_received, chunk)

    if not os.path.isfile(result_filename):
        raise ValueError("result file is missing")

    address = address_target.value.decode()
    task_id = task_id_target.value.decode()
    round = int(round_target.value.decode())

    return address, task_id, round, result_filename


@router.post("/result", response_model=CommonResp)
async def upload_result(req: Request):
    address, task_id, round, src = await parse_upload_result_request(req)

    dst = coord.loc.task_member_result_file(task_id, round, address)
    await run_in_threadpool(shutil.move, src, dst)

    _logger.info(
        f"task {task_id} round {round} {address} upload result",
        extra={"task_id": task_id},
    )
    return CommonResp()


class Metrics(TaskRound):
    metrics: Dict[str, int]


@router.post("/metrics", response_model=CommonResp)
def upload_metrics(metrics: Metrics):
    with open(
        coord.loc.task_member_metrics_file(
            metrics.task_id, metrics.round, metrics.address
        ),
        mode="w",
        encoding="utf-8",
    ) as f:
        json.dump(metrics.metrics, f, ensure_ascii=False)
    return CommonResp()


@router.get("/weight")
def get_task_weight(
    task_id: str = Query(..., regex=r"0x[0-9a-fA-F]+"), round: int = Query(...)
):
    weight_filename = coord.loc.task_weight_file(task_id, round)
    if not os.path.exists(weight_filename):
        raise HTTPException(400, f"task {task_id} does not exist")

    def file_iter():
        chunk_size = 1024 * 1024
        with open(weight_filename, mode="rb") as f:
            while True:
                content = f.read(chunk_size)
                if len(content) == 0:
                    break
                yield content

    return StreamingResponse(
        file_iter(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={task_id}.weight"},
    )
