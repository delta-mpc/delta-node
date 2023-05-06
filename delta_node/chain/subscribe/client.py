import asyncio
from contextlib import suppress
from logging import getLogger
from typing import AsyncGenerator

from grpc.aio import Channel

from delta_node import entity, serialize

from . import subscribe_pb2 as pb
from .subscribe_pb2_grpc import SubscribeStub

_logger = getLogger(__name__)


class Client(object):
    def __init__(self, ch: Channel) -> None:
        self.stub = SubscribeStub(ch)

    async def _subscribe(
        self, address: str, timeout: int = 0
    ) -> AsyncGenerator[entity.Event, None]:
        req = pb.EventReq(address=address, timeout=timeout)
        stream = self.stub.Subscribe(req)
        async for event in stream:
            event_type = event.WhichOneof("event")
            if event_type == "task_created":
                yield entity.TaskCreateEvent(
                    address=event.task_created.address,
                    task_id=event.task_created.task_id,
                    dataset=event.task_created.dataset,
                    url=event.task_created.url,
                    commitment=serialize.hex_to_bytes(
                        event.task_created.commitment
                    ),
                    task_type=event.task_created.task_type,
                    enable_verify=event.task_created.enable_verify,
                    tolerance=event.task_created.tolerance,
                )
            elif event_type == "round_started":
                yield entity.RoundStartedEvent(
                    task_id=event.round_started.task_id,
                    round=event.round_started.round,
                )
            elif event_type == "partner_selected":
                yield entity.PartnerSelectedEvent(
                    task_id=event.partner_selected.task_id,
                    round=event.partner_selected.round,
                    addrs=list(event.partner_selected.addrs),
                )
            elif event_type == "calculation_started":
                yield entity.CalculationStartedEvent(
                    task_id=event.calculation_started.task_id,
                    round=event.calculation_started.round,
                    addrs=list(event.calculation_started.addrs),
                )
            elif event_type == "aggregation_started":
                yield entity.AggregationStartedEvent(
                    task_id=event.aggregation_started.task_id,
                    round=event.aggregation_started.round,
                    addrs=list(event.aggregation_started.addrs),
                )
            elif event_type == "round_ended":
                yield entity.RoundEndedEvent(
                    task_id=event.round_ended.task_id,
                    round=event.round_ended.round,
                )
            elif event_type == "task_finished":
                yield entity.TaskFinishEvent(task_id=event.task_finished.task_id)
            elif event_type == "heartbeat":
                yield entity.HeartbeatEvent()
            elif event_type == "data_registered":
                yield entity.DataRegisteredEvent(
                    owner=event.data_registered.owner,
                    name=event.data_registered.name,
                    index=event.data_registered.index,
                    commitment=serialize.hex_to_bytes(
                        event.data_registered.commitment
                    ),
                )
            elif event_type == "task_member_verified":
                yield entity.TaskMemberVerifiedEvent(
                    task_id=event.task_member_verified.task_id,
                    address=event.task_member_verified.address,
                    verified=event.task_member_verified.verified,
                )
            elif event_type == "task_verification_confirmed":
                yield entity.TaskVerificationConfirmedEvent(
                    task_id=event.task_verification_confirmed.task_id,
                )

    async def subscribe(
        self,
        address: str,
        timeout: int = 0,
        retry_attemps: int = 0,
        yield_heartbeat: bool = False,
    ) -> AsyncGenerator[entity.Event, None]:
        origin_retry_attemps = retry_attemps
        while retry_attemps + 1 > 0:
            event_gen = self._subscribe(address=address, timeout=timeout)
            gen_finished = False
            try:
                while True:
                    t = None if timeout == 0 else timeout * 2
                    event = await asyncio.wait_for(event_gen.asend(None), t)
                    if isinstance(event, entity.HeartbeatEvent):
                        _logger.debug("receive heartbeat from connector")
                        if yield_heartbeat:
                            yield event
                    elif isinstance(event, entity.Event):
                        yield event
            except StopAsyncIteration:
                gen_finished = True
                return
            except asyncio.TimeoutError as e:
                if retry_attemps == 0:
                    _logger.error(
                        f"cannot connect to connector {origin_retry_attemps} times, exit"
                    )
                    raise e
                _logger.warning(
                    f"connector does not send heartbeat after {timeout * 2} seconds, reconnect"
                )
                await asyncio.sleep(2)
                retry_attemps -= 1
            except asyncio.CancelledError:
                raise
            except Exception as e:
                _logger.exception(e)
                raise e
            finally:
                if not gen_finished:
                    task = asyncio.ensure_future(event_gen.asend(None))
                    task.cancel()
                    with suppress(asyncio.CancelledError):
                        await task
                    await event_gen.aclose()
                    gen_finished = True
