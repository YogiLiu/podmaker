from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


# use to convert environment variables to python types or validate them
_Validator = Callable[[str], Any]


class _EnvFactory:
    def __init__(self, key: str, *, required: bool = True, validators: _Validator | list[_Validator] = str):
        self.key = key
        self.required = required
        self.validators = validators

    @staticmethod
    def optional_env(key: str) -> str:
        return os.getenv(key, '')

    @staticmethod
    def required_env(key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f'environment variable {key} is required')
        return value

    def validate(self, value: str) -> Any:
        if isinstance(self.validators, list):
            for validator in self.validators:
                validator: _Validator
                v = validator(value)
                if v is not None:
                    value = v
        else:
            v = self.validators(value)
            if v is not None:
                value = v
        return value

    def __call__(self) -> Any:
        if self.required:
            value = self.required_env(self.key)
        else:
            value = self.optional_env(self.key)
        return self.validate(value)


@dataclass(frozen=True)
class OwnerEnv:
    name: str = field(default_factory=_EnvFactory('PM_OWNER_NAME'))
    email: str = field(default_factory=_EnvFactory('PM_OWNER_EMAIL'))


@dataclass(frozen=True)
class S3Env:
    access_key: str = field(default_factory=_EnvFactory('S3_ACCESS_KEY'))
    access_secret: str = field(default_factory=_EnvFactory('S3_ACCESS_SECRET'))
    bucket: str = field(default_factory=_EnvFactory('S3_BUCKET'))
    endpoint: str = field(default_factory=_EnvFactory('S3_ENDPOINT'))
    cdn_prefix: str = field(default_factory=_EnvFactory('S3_CDN_PREFIX'))


@dataclass(frozen=True)
class PMEnv:
    owner: OwnerEnv = field(default_factory=OwnerEnv)
    s3: S3Env = field(default_factory=S3Env)


def load_from_dotenv() -> PMEnv:
    from dotenv import load_dotenv
    load_dotenv()
    return PMEnv()
