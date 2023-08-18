import random
import unittest
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Type
from unittest.mock import patch
from urllib.parse import ParseResult, urlparse

import boto3
from botocore.exceptions import ClientError

from podmaker.env import OwnerEnv, PMEnv, S3Env
from podmaker.storage import S3

file_size = 10


@dataclass
class MockedObject:
    content_length: int
    content_type: str


# noinspection PyPep8Naming
class MockedBucket:
    @staticmethod
    def put_object(*, Key: str, **__: Any) -> ParseResult:
        return urlparse(f'http://localhost:9000/{Key}')

    @staticmethod
    def Object(*, key: str) -> MockedObject:
        if key == 'empty.bin':
            raise ClientError(error_response={}, operation_name='GetObject')
        return MockedObject(content_type='application/octet-stream', content_length=file_size)


# noinspection PyPep8Naming
class MockedServiceResource:
    @staticmethod
    def Bucket(*_: Any, **__: Any) -> MockedBucket:
        return MockedBucket()


def mock_resource(*_: Any, **__: Any) -> Type[MockedServiceResource]:
    return MockedServiceResource


class TestS3(unittest.TestCase):
    @patch.object(boto3, 'resource', mock_resource)
    def setUp(self) -> None:
        self.s3 = S3(
            PMEnv(
                s3=S3Env(
                    access_key='123',
                    access_secret='456',
                    bucket='podmaker',
                    endpoint='http://localhost:9000',
                    cdn_prefix='http://localhost:9000'
                ),
                owner=OwnerEnv(name='test', email='test@test')
            )
        )
        self.file = BytesIO()
        self.file.write(random.randbytes(file_size))
        self.file.seek(0)

    def test_s3(self) -> None:
        for _ in range(2):
            result = self.s3.put(self.file, key='/test.bin', content_type='application/octet-stream')
            self.assertEqual(result.geturl(), 'http://localhost:9000/test.bin')
            info = self.s3.check(key='/test.bin')
            self.assertIsNotNone(info)
            if info is not None:
                self.assertEqual(info.uri.geturl(), 'http://localhost:9000/test.bin')
                self.assertEqual(info.size, self.file.getbuffer().nbytes)
                self.assertEqual(info.type, 'application/octet-stream')

    def test_check_empty(self) -> None:
        r = self.s3.check(key='/empty.bin')
        self.assertIsNone(r)
