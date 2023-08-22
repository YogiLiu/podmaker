from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterator

from podmaker.config import PMConfig
from podmaker.processor.task import Task
from podmaker.storage import Storage
from podmaker.util import exit_signal

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, config: PMConfig, storage: Storage):
        self._config = config
        self._storage = storage
        exit_signal.register(self._exit_handler)

    @property
    def _tasks(self) -> Iterator[Task]:
        for source in self._config.sources:
            yield Task(source, self._storage, self._config.owner)

    def _exit_handler(self, *_: Any) -> None:
        logger.warning('received exit signal')
        self.exit_handler()

    def exit_handler(self, *_: Any) -> None:
        pass

    def run(self) -> None:
        with ThreadPoolExecutor(max_workers=5) as executor:
            for task in self._tasks:
                logger.info(f'submit task: {task.id}')
                executor.submit(task.execute)
        logger.info('processor exited')
