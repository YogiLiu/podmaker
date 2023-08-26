from pathlib import PurePath
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

SupportedStorage = Literal['s3', 'local']


class StorageConfig(BaseModel):
    dest: SupportedStorage = Field(min_length=1, frozen=True)


class S3Config(StorageConfig):
    dest: Literal['s3'] = Field(frozen=True)
    access_key: str = Field(min_length=1, frozen=True)
    access_secret: str = Field(min_length=1, frozen=True)
    bucket: str = Field(min_length=1, frozen=True)
    endpoint: HttpUrl = Field(frozen=True)
    public_endpoint: HttpUrl = Field(frozen=True)


class LocalConfig(StorageConfig):
    dest: Literal['local'] = Field(frozen=True)
    base_dir: PurePath = Field(min_length=1, frozen=True)
    public_endpoint: HttpUrl = Field(frozen=True)
