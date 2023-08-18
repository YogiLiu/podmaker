import unittest
from datetime import date
from typing import IO, AnyStr
from urllib.parse import ParseResult, urlparse

from podmaker.config import OwnerConfig, PMConfig, S3Config
from podmaker.parser import YouTube
from podmaker.storage import ObjectInfo, Storage
from tests.util import network_available


class MockStorage(Storage):
    cnt = 0

    def put(self, data: IO[AnyStr], key: str, *, content_type: str = '') -> ParseResult:
        assert data.name.endswith('.mp3'), 'only mp3 is supported'
        assert self.cnt % 2 == 1, 'file already exists'
        return urlparse('https://example.com')

    def check(self, key: str) -> ObjectInfo:
        self.cnt += 1
        return ObjectInfo(
            uri=urlparse('https://example.com'),
            size=0,
            type='audio/mp3'
        )


@unittest.skipUnless(network_available('https://www.youtube.com'), 'network is not available')
class TestYoutube(unittest.TestCase):
    uri = urlparse('https://www.youtube.com/playlist?list=PLOU2XLYxmsILHvpAkROp2dXz-jQi4S4_y')

    test_cases = [
        ('8ih7eHwPoxM', 'Introduction to ARCore Augmented Faces, Unity', date.fromisoformat('2019-09-12')),
        ('-4EvaCQpVEQ', 'Introduction to ARCore Augmented Faces, Android', date.fromisoformat('2019-09-12')),
        ('QAqOTaCCD9M', 'Introduction to ARCore Augmented Faces, iOS', date.fromisoformat('2019-09-12')),
    ]

    def setUp(self) -> None:
        storage = MockStorage()
        self.youtube = YouTube(
            storage,
            PMConfig(
                owner=OwnerConfig(name='Podmaker', email='test@podmaker.dev'),
                s3=S3Config(
                    access_key='123',
                    access_secret='456',
                    bucket='podmaker',
                    endpoint='http://localhost:9000',
                    cdn_prefix='http://localhost:9000'
                )
            )
        )

    def test_fetch(self) -> None:
        podcast = self.youtube.fetch(self.uri)
        self.assertEqual(podcast.link, self.uri.geturl())
        self.assertEqual(podcast.title, 'Introduction to ARCore Augmented Faces')
        self.assertIsNotNone(podcast.image.ensure())
        self.assertEqual(
            podcast.description,
            'Learn how to use ARCore’s Augmented Faces APIs to create face effects with Unity, Android, and iOS.'
        )
        self.assertEqual(podcast.owner.name, 'Podmaker')
        self.assertEqual(podcast.owner.email, 'test@podmaker.dev')
        self.assertEqual(podcast.author, 'Google for Developers')
        self.assertEqual(podcast.categories, [])
        self.assertFalse(podcast.explicit)
        self.assertIsNone(podcast.language)
        for (idx, episode) in enumerate(podcast.items):
            if idx >= len(self.test_cases):
                break
            test_case = self.test_cases[idx]
            self.assertEqual(episode.guid, test_case[0])
            self.assertEqual(episode.title, test_case[1])
            self.assertIsNotNone(episode.pub_date)
            if episode.pub_date is not None:
                self.assertEqual(episode.pub_date.date(), test_case[2])
            self.assertIsNotNone(podcast.image.ensure())
            self.assertEqual(episode.enclosure.ensure().url, urlparse('https://example.com'))
