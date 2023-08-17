from abc import ABC, abstractmethod
from urllib.parse import ParseResult

from podmaker.rss import Podcast


class Parser(ABC):
    @abstractmethod
    def fetch(self, uri: ParseResult) -> Podcast:
        raise NotImplementedError
