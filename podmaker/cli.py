import argparse
import logging
import sys
from pathlib import Path

from podmaker.config import ConfigError, PMConfig
from podmaker.processor import Processor, ScheduleProcessor
from podmaker.storage import S3
from podmaker.util import exit_signal

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
    if config.storage.dest == 's3':
        storage = S3(config.storage)
        storage.start()
    else:
        raise ValueError(f'unknown storage destination: {config.storage.dest}')
    logger.info(f'running in {config.app.mode} mode')
    processor: Processor
    if config.app.mode == 'watch':
        processor = ScheduleProcessor(config=config, storage=storage)
    else:
        processor = Processor(config=config, storage=storage)
    exit_signal.listen()
    try:
        processor.run()
    except BaseException:
        storage.stop()
        raise
