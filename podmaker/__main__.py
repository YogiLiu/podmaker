import argparse
import logging
import sys
from pathlib import Path
from typing import Type

from podmaker.config import ConfigError, PMConfig
from podmaker.processor import Processor, ScheduleProcessor
from podmaker.storage import S3

logger = logging.getLogger('podmaker')


def run() -> None:
    parser = argparse.ArgumentParser(prog='podmaker', description='Podcast generator.')
    parser.add_argument('-w', '--watch', help='Watch for changes.', type=bool, default=False)
    parser.add_argument('-c', '--conf', help='Path to config file.', type=Path, default=Path('config.toml'))
    args = parser.parse_args()
    config_path = args.conf
    try:
        config = PMConfig.from_file(config_path)
    except ConfigError as e:
        logger.error(e)
        sys.exit(1)

    logging.basicConfig(
        level=config.logging.level,
        format='%(asctime)s\t%(levelname)s\t%(name)s\t%(message)s',
    )
    storage = S3(config.s3)
    processor_class: Type[Processor]
    if args.watch:
        processor_class = ScheduleProcessor
    else:
        processor_class = Processor
    processor = processor_class(config=config, storage=storage)
    try:
        processor.run()
    except KeyboardInterrupt:
        logger.warning('interrupted by user')


if __name__ == '__main__':
    run()
