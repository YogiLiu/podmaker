from __future__ import annotations

import sys
from pathlib import PurePath

from pydantic import BaseModel, EmailStr, Field, HttpUrl

if sys.version_info >= (3, 11):
    import tomllib as toml
else:
    import tomlkit as toml


class OwnerConfig(BaseModel):
    name: str = Field(min_length=1, frozen=True)
    email: EmailStr = Field(frozen=True)


class S3Config(BaseModel):
    access_key: str = Field(min_length=1, frozen=True)
    access_secret: str = Field(min_length=1, frozen=True)
    bucket: str = Field(min_length=1, frozen=True)
    endpoint: HttpUrl = Field(frozen=True)
    cdn_prefix: HttpUrl = Field(frozen=True)


class PMConfig(BaseModel):
    owner: OwnerConfig = Field(frozen=True)
    s3: S3Config = Field(frozen=True)

    @classmethod
    def from_file(cls, path: PurePath) -> PMConfig:
        with open(path, 'rb') as f:
            data = toml.load(f)
        return cls(**data)
