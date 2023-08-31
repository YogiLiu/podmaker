from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Any, Iterator

from podmaker.config import PMConfig, SourceConfig
from podmaker.fetcher import Fetcher
from podmaker.processor.task import Task
from podmaker.storage import Storage
from podmaker.util import exit_signal

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, config: PMConfig, storage: Storage):
        self._config = config
        self._storage = storage
        exit_signal.register(self._exit_handler)
        self._fetcher_instances: dict[str, Fetcher] = {}

    @contextmanager
    def _context(self) -> Iterator[None]:
        for fetcher in self._fetcher_instances.values():
            fetcher.start()
        try:
            yield
        finally:
            for fetcher in self._fetcher_instances.values():
                fetcher.stop()

    def _get_fetcher(self, source: SourceConfig) -> Fetcher:
        if source.url.host not in self._fetcher_instances:
            if source.url.host == 'www.youtube.com':
                from podmaker.fetcher.youtube import YouTube
                self._fetcher_instances[source.url.host] = YouTube(self._storage, self._config.owner)
            else:
                raise ValueError(f'unsupported host: {source.url.host}')
        return self._fetcher_instances[source.url.host]

    @property
    def _tasks(self) -> Iterator[Task]:
        for source in self._config.sources:
            fetcher = self._get_fetcher(source)
            yield Task(fetcher, source, self._storage, self._config.owner)

    def _exit_handler(self, *_: Any) -> None:
        logger.warning('received exit signal')
        self.exit_handler()

    def exit_handler(self, *_: Any) -> None:
        pass

    def run(self) -> None:
        with self._context():
            with ThreadPoolExecutor(max_workers=5) as executor:
                for task in self._tasks:
                    logger.info(f'submit task: {task.id}')
                    executor.submit(task.execute)
            logger.info('processor exited')
