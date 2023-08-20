import logging
from urllib.parse import urlparse

from podmaker.config import OwnerConfig, SourceConfig
from podmaker.fetcher import Fetcher, YouTube
from podmaker.rss import Podcast
from podmaker.storage import Storage

logger = logging.getLogger(__name__)

_fetcher_instances: dict[str, Fetcher] = {}


class Task:
    def __init__(self, source: SourceConfig, storage: Storage, owner: OwnerConfig):
        self._source = source
        self._storage = storage
        self._owner = owner
        self._fetcher = self._get_fetcher()

    def _get_fetcher(self) -> Fetcher:
        if self._source.url.host not in _fetcher_instances:
            if self._source.url.host == 'www.youtube.com':
                _fetcher_instances[self._source.url.host] = YouTube(self._storage, self._owner)
            else:
                raise ValueError(f'unsupported url: {self._source.url}')
        return _fetcher_instances[self._source.url.host]

    def start(self) -> Podcast:
        url = urlparse(str(self._source.url))
        logger.debug(f'task running: {self._source.id}')
        return self._fetcher.fetch(url)
