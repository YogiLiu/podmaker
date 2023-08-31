__all__ = ['Storage', 'ObjectInfo', 'EMPTY_FILE', 'get_storage']

from podmaker.config import LocalConfig, S3Config, StorageConfig
from podmaker.storage.core import EMPTY_FILE, ObjectInfo, Storage


def get_storage(config: StorageConfig) -> Storage:
    if isinstance(config, S3Config):
        from podmaker.storage.s3 import S3
        return S3(config)
    elif isinstance(config, LocalConfig):
        from podmaker.storage.local import Local
        return Local(config)
    else:
        raise ValueError(f'unknown storage destination: {config.dest}')
