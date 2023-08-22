from __future__ import annotations

import logging
from io import BytesIO
from typing import Any, Callable
from uuid import uuid4

from podmaker.config import OwnerConfig, SourceConfig
from podmaker.fetcher import Fetcher, YouTube
from podmaker.rss import Podcast
from podmaker.storage import EMPTY_FILE, Storage
from podmaker.util import ExitSignalError

logger = logging.getLogger(__name__)

_fetcher_instances: dict[str, Fetcher] = {}

Hook = Callable[[str], None]


def _do_nothing(*_: Any) -> None:
    pass


class Task:
    def __init__(self, source: SourceConfig, storage: Storage, owner: OwnerConfig | None):
        self._id = uuid4().hex
        logger.info(f'create task {self._id} for {source.id}')
        self._source = source
        self._storage = storage
        self._owner = owner
        self._fetcher = self._get_fetcher()
        self.before: Hook = _do_nothing
        self.after: Hook = _do_nothing

    @property
    def id(self) -> str:
        return self._id

    def _get_fetcher(self) -> Fetcher:
        if self._source.url.host not in _fetcher_instances:
            if self._source.url.host == 'www.youtube.com':
                _fetcher_instances[self._source.url.host] = YouTube(self._storage, self._owner)
            else:
                raise ValueError(f'unsupported url: {self._source.url}')
        return _fetcher_instances[self._source.url.host]

    def _fetch_original(self, key: str) -> Podcast | None:
        with self._storage.get(key) as xml_file:
            if xml_file == EMPTY_FILE:
                logger.info(f'no original file: {key}')
                return None
            xml = xml_file.read()
        return Podcast.from_rss(xml.decode('utf-8'))

    def _execute(self) -> None:
        logger.info(f'execute task: {self.id}')
        try:
            key = self._source.get_storage_key('feed.rss')
            original_pod = self._fetch_original(key)
            source_pod = self._fetcher.fetch(self._source)
            if original_pod:
                has_changed = original_pod.merge(source_pod)
            else:
                has_changed = True
                original_pod = source_pod
            if has_changed:
                logger.info(f'update: {self._source.id}')
                buf = BytesIO(original_pod.bytes)
                self._storage.put(buf, key, content_type='text/xml; charset=utf-8')
            else:
                logger.info(f'no change: {self._source.id}')
        except ExitSignalError as e:
            logger.warning(f'task ({self.id}) cancelled due to {e}')
        except BaseException as e:
            logger.error(f'task execute failed: {e} task: {self.id}')

    def execute(self) -> None:
        logger.debug(f'task running: {self._source.id}')
        self.before(self.id)
        self._execute()
        logger.debug(f'task finished: {self.id}')
        self.after(self.id)
