__all__ = [
    "TaskError",
    "NoSuchTaskError",
    "MemberNotJoinedError",
    "TaskNotReadyError",
    "TaskNoMemberError",
    "TaskUnfinishedRoundError",
    "TaskNoSuchRoundError",
]


class TaskError(Exception):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id


class NoSuchTaskError(TaskError):
    def __init__(self, task_id: int) -> None:
        super().__init__(task_id)

    def __str__(self) -> str:
        return f"no such task {self.task_id}"


class TaskNotReadyError(TaskError):
    def __init__(self, task_id: int) -> None:
        super().__init__(task_id)

    def __str__(self) -> str:
        return f"task {self.task_id} is not ready"


class MemberNotJoinedError(TaskError):
    def __init__(self, task_id: int, member_id: str) -> None:
        super().__init__(task_id)
        self.member_id = member_id

    def __str__(self) -> str:
        return f"member {self.member_id} has not joined task {self.task_id}"

class TaskNoMemberError(TaskError):
    def __init__(self, task_id: int, member_id: str) -> None:
        super().__init__(task_id)
        self.member_id = member_id

    def __str__(self) -> str:
        return f"task {self.task_id} has no member {self.member_id}"


class TaskUnfinishedRoundError(TaskError):
    def __init__(self, task_id: int, round_id: int) -> None:
        super().__init__(task_id)
        self.round_id = round_id

    def __str__(self) -> str:
        return f"task {self.task_id} round {self.round_id} is not finished"


class TaskNoSuchRoundError(TaskError):
    def __init__(self, task_id: int, member_id: str, round_id: int) -> None:
        super().__init__(task_id)
        self.member_id = member_id
        self.round_id = round_id

    def __str__(self) -> str:
        return f"task {self.task_id} has no such round {self.round_id} for member {self.member_id}"
