import random
import unittest
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Type
from unittest.mock import patch
from urllib.parse import ParseResult, urlparse

import boto3
from botocore.exceptions import ClientError

from podmaker.config import S3Config
from podmaker.storage.s3 import S3

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
            S3Config(
                dest='s3',
                access_key='123',
                access_secret='456',
                bucket='podmaker',
                endpoint='http://localhost:9000',
                public_endpoint='http://localhost:9000'
            )
        )
        self.file = BytesIO()
        self.file.write(random.randbytes(file_size))
        self.file.seek(0)

    def test_s3(self) -> None:
        for _ in range(2):
            result = self.s3.put(self.file, key='/test.bin', content_type='application/octet-stream')
            self.assertEqual('http://localhost:9000/test.bin', result.geturl())
            info = self.s3.check(key='/test.bin')
            self.assertIsNotNone(info)
            if info is not None:
                self.assertEqual('http://localhost:9000/test.bin', info.uri.geturl())
                self.assertEqual(self.file.getbuffer().nbytes, info.size)
                self.assertEqual('application/octet-stream', info.type)

    def test_check_empty(self) -> None:
        r = self.s3.check(key='/empty.bin')
        self.assertIsNone(r)
