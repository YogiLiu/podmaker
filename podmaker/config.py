from __future__ import annotations

import sys
from pathlib import PurePath
from typing import AnyStr, Literal, Optional
from urllib.parse import quote

from pydantic import BaseModel, EmailStr, Field, HttpUrl, ValidationError, field_validator

if sys.version_info >= (3, 11):
    import tomllib as toml
else:
    import tomlkit as toml


class OwnerConfig(BaseModel):
    name: Optional[str] = Field(None, min_length=1, frozen=True)
    email: EmailStr = Field(frozen=True)


# noinspection PyNestedDecorators
class AppConfig(BaseModel):
    mode: Literal['oneshot', 'watch'] = Field('oneshot', frozen=True)
    loglevel: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = Field('INFO', frozen=True)

    @field_validator('mode', mode='before')
    @classmethod
    def mode_value(cls, v: AnyStr) -> str:
        """for tomlkit"""
        return str(v)

    @field_validator('loglevel', mode='before')
    @classmethod
    def loglevel_value(cls, v: AnyStr) -> str:
        """for tomlkit"""
        return str(v)


class S3Config(BaseModel):
    access_key: str = Field(min_length=1, frozen=True)
    access_secret: str = Field(min_length=1, frozen=True)
    bucket: str = Field(min_length=1, frozen=True)
    endpoint: HttpUrl = Field(frozen=True)
    public_endpoint: HttpUrl = Field(frozen=True)


class SourceConfig(BaseModel):
    id: str = Field(min_length=1, frozen=True)
    url: HttpUrl = Field(frozen=True)

    def get_storage_key(self, key: str) -> str:
        return f'{quote(self.id)}/{key}'


class ConfigError(Exception):
    pass


class PMConfig(BaseModel):
    owner: Optional[OwnerConfig] = Field(None, frozen=True)
    s3: S3Config = Field(frozen=True)
    sources: tuple[SourceConfig, ...] = Field(frozen=True)
    app: AppConfig = Field(default_factory=AppConfig, frozen=True)

    @classmethod
    def from_file(cls, path: PurePath) -> PMConfig:
        try:
            with open(path, 'rb') as f:
                data = toml.load(f)
        except FileNotFoundError as e:
            raise ConfigError(f'config file not found: {path}') from e
        try:
            return cls(**data)
        except ValidationError as e:
            raise ConfigError(f'can not initial config: {e}')
