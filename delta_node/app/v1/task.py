import asyncio
import logging
import math
import os
import shutil
from typing import IO, List, Optional

import sqlalchemy as sa
from delta_node import chain, coord, db, entity, pool, registry
from delta_node.serialize import bytes_to_hex, hex_to_bytes
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    BackgroundTasks,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

_logger = logging.getLogger(__name__)

router = APIRouter()


class CommonResp(BaseModel):
    success: bool = True


class CreateTaskResp(BaseModel):
    task_id: str


async def dump_task(task_id: str, task_file: IO[bytes]):
    task_file.seek(0)
    with open(coord.task_config_file(task_id), mode="wb") as f:
        shutil.copyfileobj(task_file, f)


@router.post("/task", response_model=CreateTaskResp)
async def create_task(
    *,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(db.get_session),
    background: BackgroundTasks,
):
    loop = asyncio.get_running_loop()
    task_item = await loop.run_in_executor(pool.IO_POOL, coord.create_task, file.file)
    node_address = await registry.get_node_address()
    task_id = await chain.get_client().create_task(
        node_address, task_item.dataset, task_item.commitment
    )
    task_item.creator = node_address
    task_item.task_id = task_id
    task_item.status = entity.TaskStatus.RUNNING
    session.add(task_item)
    await session.commit()

    await loop.run_in_executor(pool.IO_POOL, dump_task, task_id, file.file)

    background.add_task(coord.run_task, task_id)
    return CreateTaskResp(task_id=task_id)


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
    q = (
        sa.select(entity.TaskRound)
        .where(entity.TaskRound.task_id == shares.task_id)
        .where(entity.TaskRound.round == shares.round)
    )
    round: Optional[entity.TaskRound] = (
        (await session.execute(q)).scalars().one_or_none()
    )
    if not round:
        raise HTTPException(400, "task round does not exist")
    if round.status != entity.RoundStatus.RUNNING:
        raise HTTPException(400, "round is not in running phase")

    # get members in running phase
    q = (
        sa.select(entity.RoundMember)
        .where(entity.RoundMember.status == entity.RoundStatus.RUNNING)
        .where(entity.RoundMember.round_id == round.id)
    )
    members = (await session.execute(q)).scalars().all()
    member_addrs = [member.address for member in members]
    if shares.address not in member_addrs:
        raise HTTPException(400, f"member ${shares.address} is not allowed")

    if len(shares.shares) != len(member_addrs):
        raise HTTPException(400, "should share to all members in RUNNING phase")

    if not all(share.sender == shares.address for share in shares.shares):
        raise HTTPException(400, "all share senders should be equal to member address")
    # check if all shares has upload commitment to chain
    futs: List[asyncio.Task[entity.SecretShareData]] = []
    for addr in member_addrs:
        fut = asyncio.create_task(
            chain.get_client().get_secret_share_data(
                shares.task_id, shares.round, shares.address, addr
            )
        )
        futs.append(fut)
    try:
        ss_datas = await asyncio.gather(*futs)
        for ss_data in ss_datas:
            if (
                len(ss_data.seed_commitment) == 0
                or len(ss_data.secret_key_commitment) == 0
            ):
                raise HTTPException(400, "should upload secret share commitment first")
    except Exception:
        raise HTTPException(400, "should upload secret share commitment first")

    member_dict = {member.address: member for member in members}
    sender = member_dict[shares.address]

    for share in shares.shares:
        receiver = member_dict[share.receiver]
        ss = entity.SecretShare(
            sender.id,
            receiver.id,
            hex_to_bytes(share.seed_share),
            hex_to_bytes(share.sk_share),
        )
        session.add(ss)
    await session.commit()

    return CommonResp()


@router.get("/secret_shares", response_model=SecretShares)
async def get_secret_shares(
    task_round: TaskRound, session: AsyncSession = Depends(db.get_session)
):
    q = (
        sa.select(entity.TaskRound)
        .where(entity.TaskRound.task_id == task_round.task_id)
        .where(entity.TaskRound.round == task_round.round)
    )
    round: Optional[entity.TaskRound] = (
        (await session.execute(q)).scalars().one_or_none()
    )
    if not round:
        raise HTTPException(400, "task round does not exist")
    if round.status != entity.RoundStatus.CALCULATING:
        raise HTTPException(400, "round is not in calculating phase")

    q = (
        sa.select(entity.RoundMember)
        .where(entity.RoundMember.round_id == round.id)
        .where(entity.RoundMember.address == task_round.address)
        .options(selectinload(entity.RoundMember.received_shares))
    )
    member: Optional[entity.RoundMember] = (
        (await session.execute(q)).scalars().one_or_none()
    )
    if not member:
        raise HTTPException(400, f"member ${task_round.address} does not exists")
    if member.status != entity.RoundStatus.CALCULATING:
        raise HTTPException(400, f"member ${task_round.address} is not allowed")

    sender_ids = [share.sender_id for share in member.received_shares]
    q = sa.select(entity.RoundMember).where(entity.RoundMember.id.in_(sender_ids))  # type: ignore
    senders: List[entity.RoundMember] = (await session.execute(q)).scalars().all()

    sender_dict = {sender.id: sender for sender in senders}
    shares = []
    for share in member.received_shares:
        sender = sender_dict[share.sender_id]
        shares.append(
            SecretShare(
                sender=sender.address,
                receiver=task_round.address,
                seed_share=bytes_to_hex(share.seed_share),
                sk_share=bytes_to_hex(share.sk_share),
            )
        )
    resp = SecretShares(
        address=task_round.address,
        task_id=task_round.task_id,
        round=task_round.round,
        shares=shares,
    )
    return resp


@router.post("/result", response_model=CommonResp)
def upload_result(task_round: TaskRound = Form(...), file: UploadFile = File(...)):
    dst = coord.task_member_result_file(
        task_round.task_id, task_round.round, task_round.address
    )
    with open(dst, mode="wb") as f:
        shutil.copyfileobj(file.file, f)


class Task(BaseModel):
    id: str
    created_at: int
    name: str
    type: str
    creator: str
    status: str


class TasksPage(BaseModel):
    tasks: List[Task]
    total_pages: int


@router.get("/tasks", response_model=TasksPage)
async def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, gt=0),
    session: AsyncSession = Depends(db.get_session),
):
    q = (
        sa.select(entity.Task)
        .order_by(entity.Task.id)
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    tasks: List[entity.Task] = (await session.execute(q)).scalars().all()

    q = sa.select(sa.func(entity.Task.id))
    task_count = (await session.execute(q)).scalar_one()

    total_pages = math.ceil(task_count / page_size)

    task_items = [
        Task(
            id=task.task_id,
            created_at=task.created_at,
            name=task.name,
            type=task.type,
            creator=task.creator,
            stauts=task.status.name,
        )
        for task in tasks
    ]
    tasks_page = TasksPage(tasks=task_items, total_pages=total_pages)
    return tasks_page


@router.get("/task/list", response_model=List[Task])
async def get_task_list(
    task_ids: List[str] = Query(...),
    session: AsyncSession = Depends(db.get_session),
):
    q = sa.select(entity.Task).where(entity.Task.task_id.in_(task_ids))  # type: ignore
    tasks: List[entity.Task] = (await session.execute(q)).scalars().all()
    task_dict = {task.task_id: task for task in tasks}
    task_items = []
    for task_id in task_ids:
        task = task_dict[task_id]
        task_items.append(
            Task(
                id=task.task_id,
                created_at=task.created_at,
                name=task.name,
                type=task.type,
                creator=task.creator,
                stauts=task.status.name,
            )
        )
    return task_items


@router.get("/task/metadata", response_model=Task)
async def get_task_metadata(
    task_id: str = Query(..., regex=r"0x[0-9a-fA-F]+"),
    session: AsyncSession = Depends(db.get_session),
):
    q = (
        sa.select(entity.Task)
        .where(entity.Task.task_id == task_id)
        .where(entity.Task.url.is_(None))  # type: ignore
    )
    task: Optional[entity.Task] = (await session.execute(q)).scalar_one_or_none()
    if task is None:
        raise HTTPException(400, f"task {task_id} does not exist")

    return Task(
        id=task.task_id,
        created_at=task.created_at,
        name=task.name,
        type=task.type,
        creator=task.creator,
        stauts=task.status.name,
    )


@router.get("/task/result")
def get_task_result(task_id: str = Query(..., regex=r"0x[0-9a-fA-F]+")):
    result_filename = coord.task_result_file(task_id)
    if not os.path.exists(result_filename):
        raise HTTPException(400, f"task {task_id} does not exist")

    def file_iter():
        chunk_size = 4096
        with open(result_filename, mode="rb") as f:
            while True:
                content = f.read(chunk_size)
                if len(content) < chunk_size:
                    break
                yield content

    return StreamingResponse(
        file_iter(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={task_id}.result"},
    )


# @router.get("/task/logs", response_model=List[utils.TaskLog])
# def get_task_logs(
#     task_id: int,
#     page: int = Query(1, ge=1),
#     page_size: int = Query(20, gt=0),
#     *,
#     session: Session = Depends(db.get_session),
# ):
#     logs = (
#         session.query(model.Log)
#         .filter(model.Log.task_id == task_id)
#         .order_by(model.Log.id)
#         .limit(page_size)
#         .offset((page - 1) * page_size)
#         .all()
#     )
#     res = [
#         utils.TaskLog(created_at=log.created_at, message=log.message) for log in logs
#     ]
#     return res
