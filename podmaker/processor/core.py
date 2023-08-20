from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from podmaker.config import PMConfig, SourceConfig
from podmaker.processor.task import Task
from podmaker.rss import Podcast
from podmaker.storage import Storage


class Processor:
    def __init__(self, config: PMConfig, storage: Storage):
        self._config = config
        self._storage = storage

    def _get_task(self, source: SourceConfig) -> Task:
        return Task(source, self._storage, self._config.owner)

    def _fetch_original(self, key: str) -> Podcast | None:
        with self._storage.get(key) as xml_file:
            xml = xml_file.read()
        if xml is None:
            return None
        return Podcast.from_rss(xml.decode('utf-8'))

    def _execute(self, source: SourceConfig) -> None:
        key = f'{source.name}.xml'
        task = self._get_task(source)
        with ThreadPoolExecutor() as executor:
            original_f = executor.submit(self._fetch_original, key)
            new_f = executor.submit(task.start)
            original = original_f.result()  # type: Podcast | None
            new = new_f.result()
        if original:
            has_changed = original.merge(new)
        else:
            has_changed = True
            original = new
        if has_changed:
            buf = BytesIO(original.bytes)
            self._storage.put(buf, key, content_type='application/rss+xml')

    def run(self) -> None:
        with ThreadPoolExecutor() as executor:
            for source in self._config.sources:
                executor.submit(self._execute, source)
            executor.shutdown(wait=True)
