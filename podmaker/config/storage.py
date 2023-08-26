from pathlib import PurePath
from typing import AnyStr, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

SupportedStorage = Literal['s3', 'local']


class StorageConfig(BaseModel):
    dest: SupportedStorage = Field(min_length=1, frozen=True)

    # noinspection PyNestedDecorators
    @field_validator('dest', mode='before')
    @classmethod
    def dest_value(cls, v: AnyStr) -> str:
        """for tomlkit"""
        return str(v)


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

    # noinspection PyNestedDecorators
    @field_validator('base_dir', mode='before')
    @classmethod
    def dest_value(cls, v: str) -> PurePath:
        """for tomlkit"""
        return PurePath(v)
