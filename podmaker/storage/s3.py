from __future__ import annotations

import base64
import hashlib
import logging
from typing import IO, AnyStr
from urllib.parse import ParseResult, urlparse

import boto3
from botocore.exceptions import ClientError

from podmaker.env import PMEnv
from podmaker.storage import ObjectInfo, Storage

logger = logging.getLogger(__name__)


class S3(Storage):
    _md5_chunk_size = 1024 * 1024

    def __init__(self, env: PMEnv):
        s3_env = env.s3
        self.s3 = boto3.resource(
            's3', endpoint_url=s3_env.endpoint, aws_access_key_id=s3_env.access_key,
            aws_secret_access_key=s3_env.access_secret)
        self.bucket = self.s3.Bucket(s3_env.bucket)
        self.cdn_prefix = s3_env.cdn_prefix

    def _calculate_md5(self, data: IO[AnyStr]) -> str:
        md5 = hashlib.md5()
        while True:
            chunk = data.read(self._md5_chunk_size)
            if not chunk:
                break
            if isinstance(chunk, str):
                md5.update(chunk.encode())
            elif isinstance(chunk, bytes):
                md5.update(chunk)
            else:
                raise TypeError(f'chunk must be str or bytes, not {type(chunk)}')
        data.seek(0)
        return base64.b64encode(md5.digest()).decode()

    def put(self, data: IO[AnyStr], key: str, *, content_type: str = '') -> ParseResult:
        if key.startswith('/'):
            key = key[1:]
        md5 = self._calculate_md5(data)
        logger.info(f'upload: {key} ({md5})')
        self.bucket.put_object(Key=key, ContentMD5=md5, Body=data, ContentType=content_type)
        data.seek(0)
        return self.get_uri(key)

    def check(self, key: str) -> ObjectInfo | None:
        if key.startswith('/'):
            key = key[1:]
        try:
            info = self.bucket.Object(key=key)
            return ObjectInfo(
                uri=self.get_uri(key),
                size=info.content_length,
                type=info.content_type
            )
        except ClientError:
            return None

    def get_uri(self, key: str) -> ParseResult:
        prefix = self.cdn_prefix.removesuffix('/')
        return urlparse(f'{prefix}/{key}')
