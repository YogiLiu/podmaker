"""
Config should forbid any changes after initialization,
so it is a tuple.
"""

import os
from typing import NamedTuple


class OwnerConfig(NamedTuple):
    name: str = os.getenv('PM_OWNER_NAME')
    email: str = os.getenv('PM_OWNER_EMAIL')


class S3Config(NamedTuple):
    access_key: str = os.getenv('S3_ACCESS_KEY')
    access_secret: str = os.getenv('S3_ACCESS_SECRET')
    bucket: str = os.getenv('S3_BUCKET')
    endpoint: str = os.getenv('S3_ENDPOINT')
    cdn_prefix: str = os.getenv('S3_CDN_PREFIX')


class PMConfig(NamedTuple):
    owner: OwnerConfig = OwnerConfig()
    s3: S3Config = S3Config()


def load_from_dotenv() -> PMConfig:
    from dotenv import load_dotenv
    load_dotenv()
    return PMConfig()
