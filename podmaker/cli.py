import argparse
import logging
import sys
from pathlib import Path
from typing import Type

from podmaker.config import ConfigError, PMConfig
from podmaker.processor import Processor, ScheduleProcessor
from podmaker.storage import S3

logger = logging.getLogger(__name__)


def run() -> None:
    parser = argparse.ArgumentParser(prog='podmaker', description='Podcast generator.')
    parser.add_argument('-c', '--conf', help='Path to config file (default: config.toml).', type=Path,
                        default=Path('config.toml'))
    args = parser.parse_args()
    config_path = args.conf
    config: PMConfig
    try:
        config = PMConfig.from_file(config_path)
    except ConfigError as e:
        logger.error(e)
        sys.exit(1)

    logging.basicConfig(
        level=config.app.loglevel,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
    )
    storage = S3(config.s3)
    processor_class: Type[Processor]
    if config.app.mode == 'watch':
        processor_class = ScheduleProcessor
    else:
        processor_class = Processor
    logger.info(f'running in {config.app.mode} mode')
    processor = processor_class(config=config, storage=storage)
    try:
        processor.run()
    except KeyboardInterrupt:
        logger.warning('interrupted by user')
