__all__ = ['Storage', 'ObjectInfo', 'S3', 'EMPTY_FILE', 'Local', 'get_storage']

from podmaker.config import LocalConfig, S3Config, StorageConfig
from podmaker.storage.core import EMPTY_FILE, ObjectInfo, Storage
from podmaker.storage.local import Local
from podmaker.storage.s3 import S3


def get_storage(config: StorageConfig) -> Storage:
    if isinstance(config, S3Config):
        return S3(config)
    elif isinstance(config, LocalConfig):
        return Local(config)
    else:
        raise ValueError(f'unknown storage destination: {config.dest}')
