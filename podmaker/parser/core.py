from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from urllib.parse import ParseResult


class Resource(ABC):
    @abstractmethod
    def get(self) -> ParseResult | None:
        raise NotImplementedError


@dataclass
class Item:
    id: str
    title: str
    description: str
    thumbnail: Resource
    audio: Resource
    upload_at: date


@dataclass
class Info:
    author: str
    description: str
    thumbnail: Resource
    items: Iterable[Item]


class Parser(ABC):
    @abstractmethod
    def fetch(self, uri: ParseResult) -> Info:
        raise NotImplementedError
