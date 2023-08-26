from __future__ import annotations

import re
import sys
from pathlib import PurePath
from typing import Literal, Optional, Union
from urllib.parse import quote

from pydantic import BaseModel, EmailStr, Field, HttpUrl, ValidationError

from podmaker.config.storage import LocalConfig, S3Config

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


class SourceConfig(BaseModel):
    id: str = Field(min_length=1, frozen=True)
    name: Optional[str] = Field(None, min_length=1, frozen=True)
    regex: Optional[re.Pattern[str]] = Field(None, frozen=True)
    url: HttpUrl = Field(frozen=True)

    def get_storage_key(self, key: str) -> str:
        return f'{quote(self.id)}/{key}'


class ConfigError(Exception):
    pass


class PMConfig(BaseModel):
    owner: Optional[OwnerConfig] = Field(None, frozen=True)
    storage: Union[S3Config, LocalConfig] = Field(frozen=True)
    sources: tuple[SourceConfig, ...] = Field(frozen=True)
    app: AppConfig = Field(default_factory=AppConfig, frozen=True)

    @classmethod
    def from_file(cls, path: PurePath) -> PMConfig:
        try:
            with open(path, 'rb') as f:
                doc = toml.load(f)
                # https://github.com/sdispater/tomlkit/issues/275
                if getattr(doc, 'unwrap', None):
                    data = doc.unwrap()
                else:
                    data = doc
        except FileNotFoundError as e:
            raise ConfigError(f'config file not found: {path}') from e
        try:
            return cls(**data)
        except ValidationError as e:
            raise ConfigError(f'can not initial config: {e}')
