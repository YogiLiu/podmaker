import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from podmaker.processor.core import Processor

logger = logging.getLogger(__name__)


class ScheduleProcessor(Processor):
    def run(self) -> None:
        scheduler = BlockingScheduler()
        try:
            for task in self._tasks:
                logger.info(f'Schedule job: {task.id}, it well be run after 1 minute and every 1 hour')
                task.before = lambda: scheduler.pause_job(task.id)
                task.after = lambda: scheduler.resume_job(task.id)
                scheduler.add_job(
                    func=task.execute,
                    trigger=IntervalTrigger(hours=1),
                    next_run_time=datetime.now() + timedelta(minutes=1),
                    id=task.id,
                    name=f'Job-{task.id}',
                )
            scheduler.start()
        except Exception as e:
            logger.error(f'scheduler exited: {e}')
            scheduler.shutdown(wait=False)
            raise

