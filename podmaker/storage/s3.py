import base64
import hashlib
import logging
from typing import IO
from urllib.parse import urlparse, ParseResult

import boto3
from botocore.exceptions import ClientError

from podmaker.storage.core import Storage, ObjectInfo

logger = logging.getLogger(__name__)


class S3(Storage):
    _md5_chunk_size = 1024 * 1024

    def __init__(self, endpoint: str, cdn_prefix: str, bucket: str, access_key: str, access_secret: str):
        self.s3 = boto3.resource(
            's3', endpoint_url=endpoint, aws_access_key_id=access_key, aws_secret_access_key=access_secret)
        self.bucket = self.s3.Bucket(bucket)
        self.cdn_prefix = cdn_prefix

    def _calculate_md5(self, data: IO) -> str:
        md5 = hashlib.md5()
        while True:
            chunk = data.read(self._md5_chunk_size)
            if not chunk:
                break
            md5.update(chunk)
        data.seek(0)
        return base64.b64encode(md5.digest()).decode()

    def put(self, data: IO, key, *, content_type: str = '') -> ParseResult:
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
