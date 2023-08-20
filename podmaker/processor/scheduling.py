from typing import Any

from rocketry import Rocketry

from podmaker.processor.core import Processor


class ScheduleProcessor(Processor):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._scheduler = Rocketry(excution='thread')

    def run(self) -> None:
        for source in self._config.sources:
            self._scheduler.task('hourly', func_name=lambda: self._execute(source))
        self._scheduler.run()
