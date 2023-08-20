import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from podmaker.processor.core import Processor

logger = logging.getLogger(__name__)


class ScheduleProcessor(Processor):
    def run(self) -> None:
        scheduler = BlockingScheduler()
        try:
            for source in self._config.sources:
                logger.info(f'Schedule job: {source.name}')
                scheduler.add_job(
                    func=self._execute,
                    args=[source],
                    trigger=IntervalTrigger(hours=1),
                    name=f'Job-{source.name}',
                )
            scheduler.start()
        except Exception as e:
            logger.error(f'scheduler exited: {e}')
            scheduler.shutdown(wait=True)
            raise

