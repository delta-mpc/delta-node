__all__ = [
    "TaskError",
    "NoSuchTaskError",
    "MemberNotJoinedError",
    "TaskNotReadyError",
    "TaskNoMemberError",
    "TaskUnfinishedRoundError",
    "TaskNoSuchRoundError",
    "TaskUnknownFileTypeError",
    "TaskFileNotExistedError",
    "TaskFinishedError"
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


class TaskUnknownFileTypeError(TaskError):
    def __init__(self, task_id: int, file_type: str) -> None:
        super().__init__(task_id)
        self.file_type = file_type

    def __str__(self) -> str:
        return f"task {self.task_id} unknown file type {self.file_type}"


class TaskFileNotExistedError(TaskError):
    def __init__(self, task_id: int, filename: str) -> None:
        super().__init__(task_id)
        self.filename = filename

    def __str__(self) -> str:
        return f"task {self.task_id} {self.filename} is not existed"


class TaskFinishedError(TaskError):
    def __init__(self, task_id: int) -> None:
        super().__init__(task_id)

    def __str__(self) -> str:
        return f"task {self.task_id} already finished"