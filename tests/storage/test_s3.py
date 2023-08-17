import random
import unittest
from dataclasses import dataclass
from io import BytesIO
from unittest.mock import patch
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

from podmaker.storage import S3


file_size = 10


@dataclass
class MockedObject:
    content_length: int
    content_type: str


# noinspection PyPep8Naming
class MockedBucket:
    @staticmethod
    def put_object(*, Key, ContentMD5, Body, ContentType):
        return urlparse(f'http://localhost:9000/{Key}')

    @staticmethod
    def Object(*, key):
        if key == 'empty.bin':
            raise ClientError(error_response={}, operation_name='GetObject')
        return MockedObject(content_type='application/octet-stream', content_length=file_size)


# noinspection PyPep8Naming
class MockedServiceResource:
    @staticmethod
    def Bucket(*args, **kwargs):
        return MockedBucket()


def mock_resource(*args, **kwargs):
    return MockedServiceResource


class TestS3(unittest.TestCase):
    @patch.object(boto3, 'resource', mock_resource)
    def setUp(self) -> None:
        self.s3 = S3(
            endpoint='http://localhost:9000',
            cdn_prefix='http://localhost:9000',
            bucket='podmaker',
            access_key='123',
            access_secret='456',
        )
        self.file = BytesIO()
        self.file.write(random.randbytes(file_size))
        self.file.seek(0)

    def test_s3(self):
        for _ in range(2):
            r = self.s3.put(self.file, key='/test.bin', content_type='application/octet-stream')
            self.assertEqual(r.geturl(), 'http://localhost:9000/test.bin')
            r = self.s3.check(key='/test.bin')
            self.assertEqual(r.uri.geturl(), 'http://localhost:9000/test.bin')
            self.assertEqual(r.size, self.file.getbuffer().nbytes)
            self.assertEqual(r.type, 'application/octet-stream')

    def test_check_empty(self):
        r = self.s3.check(key='/empty.bin')
        self.assertIsNone(r)
