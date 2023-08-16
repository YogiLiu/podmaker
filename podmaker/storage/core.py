from abc import ABC, abstractmethod
from typing import IO


class Storage(ABC):
    @abstractmethod
    def put(self, data: IO, key: str, *, content_type: str = '') -> str:
        """
        :return: data uri
        """
        raise NotImplementedError

    @abstractmethod
    def check(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_uri(self, key: str) -> str:
        raise NotImplementedError
