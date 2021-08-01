from dataclasses import dataclass


@dataclass
class Message(object):
    type: str
    content: bytes
