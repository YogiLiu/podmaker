"""
Config should forbid any changes after initialization,
so it is a tuple.
"""

import os
from typing import NamedTuple


def _optional_env(key: str, default: str = '') -> str:
    return os.getenv(key, default)


def _required_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f'Environment variable {key} is required')
    return value


class OwnerConfig(NamedTuple):
    name: str = _required_env('PM_OWNER_NAME')
    email: str = _required_env('PM_OWNER_EMAIL')


class S3Config(NamedTuple):
    access_key: str = _required_env('S3_ACCESS_KEY')
    access_secret: str = _required_env('S3_ACCESS_SECRET')
    bucket: str = _required_env('S3_BUCKET')
    endpoint: str = _required_env('S3_ENDPOINT')
    cdn_prefix: str = _required_env('S3_CDN_PREFIX')


class PMConfig(NamedTuple):
    owner: OwnerConfig = OwnerConfig()
    s3: S3Config = S3Config()


def load_from_dotenv() -> PMConfig:
    from dotenv import load_dotenv
    load_dotenv()
    return PMConfig()
