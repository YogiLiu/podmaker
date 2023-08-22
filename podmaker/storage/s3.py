from __future__ import annotations

import base64
import hashlib
import logging
from contextlib import contextmanager
from tempfile import SpooledTemporaryFile
from typing import IO, AnyStr, Iterator
from urllib.parse import ParseResult, urljoin, urlparse

import boto3
from botocore.exceptions import ClientError

from podmaker.config import S3Config
from podmaker.storage import ObjectInfo, Storage
from podmaker.storage.core import EMPTY_FILE

logger = logging.getLogger(__name__)


class S3(Storage):
    _md5_chunk_size = 10 * 1024 * 1024  # 10MB
    _file_buffering = 10 * 1024 * 1024  # 10MB

    def __init__(self, config: S3Config):
        self.s3 = boto3.resource(
            's3', endpoint_url=str(config.endpoint), aws_access_key_id=config.access_key,
            aws_secret_access_key=config.access_secret)
        self.bucket = self.s3.Bucket(config.bucket)
        self.public_endpoint = str(config.public_endpoint)

    def _calculate_md5(self, data: IO[AnyStr]) -> str:
        logger.debug('calculate md5')
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
        logger.info(f'upload: {key} (md5: {md5})')
        self.bucket.put_object(Key=key, ContentMD5=md5, Body=data, ContentType=content_type)
        logger.info(f'uploaded: {key}')
        data.seek(0)
        return self.get_uri(key)

    def check(self, key: str) -> ObjectInfo | None:
        logger.debug(f'check: {key}')
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
        url = urljoin(self.public_endpoint, key)
        return urlparse(url)

    @contextmanager
    def get(self, key: str) -> Iterator[IO[bytes]]:
        logger.info(f'get: {key}')
        if key.startswith('/'):
            key = key[1:]
        with SpooledTemporaryFile(buffering=self._file_buffering) as f:
            try:
                obj = self.bucket.Object(key=key).get()
                while True:
                    chunk = obj['Body'].read(self._file_buffering)
                    if not chunk:
                        break
                    f.write(chunk)
                f.seek(0)
                yield f
            except ClientError:
                logger.debug(f'not found: {key}')
                yield EMPTY_FILE
