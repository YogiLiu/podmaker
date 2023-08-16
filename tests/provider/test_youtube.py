import unittest
from datetime import date
from typing import IO
from urllib.parse import urlparse

from podmaker.parser import YouTube
from podmaker.storage import Storage


class MockStorage(Storage):
    cnt = 0

    def put(self, data: IO, key: str, *, content_type: str = '') -> str:
        assert data.name.endswith('.mp3'), 'only mp3 is supported'
        assert self.cnt % 2 == 1, 'file already exists'
        return self.get_uri(key)

    def check(self, key: str) -> bool:
        self.cnt += 1
        return self.cnt % 2 == 0

    def get_uri(self, key: str) -> str:
        return 'https://example.com'


class TestYoutube(unittest.TestCase):
    uri = urlparse('https://www.youtube.com/playlist?list=PLOU2XLYxmsILHvpAkROp2dXz-jQi4S4_y')

    test_cases = [
        ('8ih7eHwPoxM', 'Introduction to ARCore Augmented Faces, Unity', date.fromisoformat('2019-09-12')),
        ('-4EvaCQpVEQ', 'Introduction to ARCore Augmented Faces, Android', date.fromisoformat('2019-09-12')),
        ('QAqOTaCCD9M', 'Introduction to ARCore Augmented Faces, iOS', date.fromisoformat('2019-09-12')),
    ]

    def setUp(self) -> None:
        storage = MockStorage()
        self.youtube = YouTube(storage)

    def test_fetch(self):
        info = self.youtube.fetch(self.uri)
        self.assertEqual(info.author, 'Google for Developers')
        self.assertIsNotNone(info.thumbnail.get())
        for (idx, item) in enumerate(info.items):
            if idx >= len(self.test_cases):
                break
            test_case = self.test_cases[idx]
            self.assertEqual(item.id, test_case[0])
            self.assertEqual(item.title, test_case[1])
            self.assertEqual(item.upload_at, test_case[2])
            self.assertIsNotNone(info.thumbnail.get())
            self.assertEqual(item.audio.get(), urlparse('https://example.com'))
