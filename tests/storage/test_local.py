import random
import unittest
from io import BytesIO
from pathlib import Path

from podmaker.config import LocalConfig
from podmaker.storage import Local

file_size = 10


class TestS3(unittest.TestCase):
    base_dir = Path('/tmp/podmaker')
    data_dir = base_dir / 'data'

    def setUp(self) -> None:
        self.storage = Local(
            LocalConfig(dest='local', base_dir='/tmp/podmaker', public_endpoint='http://localhost:9000')
        )
        self.storage.start()
        self.file = BytesIO()
        self.file.write(random.randbytes(file_size))
        self.file.seek(0)

    def tearDown(self) -> None:
        self.storage.stop()

    # noinspection DuplicatedCode
    def test_s3(self) -> None:
        for _ in range(2):
            result = self.storage.put(self.file, key='/test.bin', content_type='application/octet-stream')
            self.assertEqual('http://localhost:9000/test.bin', result.geturl())
            self.assertTrue((self.data_dir / 'test.bin').exists())
            info = self.storage.check(key='/test.bin')
            self.assertIsNotNone(info)
            if info is not None:
                self.assertEqual('http://localhost:9000/test.bin', info.uri.geturl())
                self.assertEqual(self.file.getbuffer().nbytes, info.size)
                self.assertEqual('application/octet-stream', info.type)
            with self.storage.get(key='/test.bin') as f:
                self.assertEqual(self.file.read(), f.read())
                self.file.seek(0)

    def test_check_empty(self) -> None:
        r = self.storage.check(key='/empty.bin')
        self.assertIsNone(r)
