from abc import ABC, abstractmethod

from podmaker.config import SourceConfig
from podmaker.rss import Podcast


class Fetcher(ABC):
    @abstractmethod
    def fetch(self, source: SourceConfig) -> Podcast:
        raise NotImplementedError

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
