from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator

from podmaker.config import PMConfig
from podmaker.processor.task import Task
from podmaker.storage import Storage

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, config: PMConfig, storage: Storage):
        self._config = config
        self._storage = storage

    @property
    def _tasks(self) -> Iterator[Task]:
        for source in self._config.sources:
            yield Task(source, self._storage, self._config.owner)

    def run(self) -> None:
        with ThreadPoolExecutor() as executor:
            for task in self._tasks:
                executor.submit(task.execute)
