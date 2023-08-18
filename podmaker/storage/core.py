from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import IO
from urllib.parse import ParseResult


@dataclass
class ObjectInfo:
    # Fully-qualified URL of the object.
    uri: ParseResult
    # Size of the object in bytes.
    size: int
    # The standard MIME type of the object.
    type: str


class Storage(ABC):
    @abstractmethod
    def put(self, data: IO, key: str, *, content_type: str = '') -> ParseResult:
        """
        :return: data uri
        """
        raise NotImplementedError

    @abstractmethod
    def check(self, key: str) -> ObjectInfo | None:
        raise NotImplementedError
