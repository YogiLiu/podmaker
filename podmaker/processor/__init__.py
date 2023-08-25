__all__ = ['Processor', 'ScheduleProcessor', 'get_processor']

from podmaker.config import PMConfig
from podmaker.processor.core import Processor
from podmaker.processor.scheduling import ScheduleProcessor
from podmaker.storage import Storage


def get_processor(config: PMConfig, storage: Storage) -> Processor:
    if config.app.mode == 'watch':
        return ScheduleProcessor(config=config, storage=storage)
    else:
        return Processor(config=config, storage=storage)
