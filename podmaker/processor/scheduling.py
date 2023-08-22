import logging
from datetime import datetime
from typing import Any

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from podmaker.config import PMConfig
from podmaker.processor.core import Processor
from podmaker.storage import Storage

logger = logging.getLogger(__name__)


class ScheduleProcessor(Processor):
    def __init__(self, config: PMConfig, storage: Storage):
        super().__init__(config, storage)
        self._scheduler = BlockingScheduler()

    def exit_handler(self, *_: Any) -> None:
        self._scheduler.shutdown(wait=False)

    def _before_hook(self, task_id: str) -> None:
        try:
            self._scheduler.pause_job(task_id)
        except JobLookupError:
            logger.warning(f'task({task_id}) not found, maybe it was removed')

    def _after_hook(self, task_id: str) -> None:
        try:
            self._scheduler.resume_job(task_id)
        except JobLookupError:
            logger.warning(f'task({task_id}) not found, maybe it was removed')

    def run(self) -> None:
        for task in self._tasks:
            logger.info(f'schedule task: {task.id}, it well be run after 1 minute and every 1 hour')
            task.before = self._before_hook
            task.after = self._after_hook
            self._scheduler.add_job(
                func=task.execute,
                trigger=IntervalTrigger(hours=1),
                next_run_time=datetime.now(),
                id=task.id,
                name=f'Job-{task.id}',
            )
        self._scheduler.start()
        logger.info('processor exited')

