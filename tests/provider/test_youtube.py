from __future__ import annotations

import sys
import unittest
from datetime import date
from typing import IO, Any, AnyStr
from urllib.parse import ParseResult, urlparse

from podmaker.config import OwnerConfig, SourceConfig
from podmaker.fetcher import YouTube
from podmaker.storage import ObjectInfo, Storage
from tests.helper import network_available

if sys.version_info >= (3, 11):
    pass
else:
    pass


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

    def get(self, key: str) -> Any:
        pass


@unittest.skipUnless(network_available('https://www.youtube.com'), 'network is not available')
class TestYoutube(unittest.TestCase):
    cases = [
        {
            'source': SourceConfig(
                id='youtube',
                url='https://www.youtube.com/playlist?list=PLOU2XLYxmsILHvpAkROp2dXz-jQi4S4_y',
                regex=r'Introduction to ARCore Augmented Faces, \w+'
            ),
            'attr': (
                'Introduction to ARCore Augmented Faces',
                'Learn how to use ARCore’s Augmented Faces APIs to create face effects with Unity, Android, and iOS.',
                'Google for Developers',
            ),
            'items': [
                ('8ih7eHwPoxM', 'Introduction to ARCore Augmented Faces, Unity', date.fromisoformat('2019-09-12')),
                ('-4EvaCQpVEQ', 'Introduction to ARCore Augmented Faces, Android', date.fromisoformat('2019-09-12')),
                ('QAqOTaCCD9M', 'Introduction to ARCore Augmented Faces, iOS', date.fromisoformat('2019-09-12')),
            ]
        },
        {
            'source': SourceConfig(
                id='youtube',
                url='https://www.youtube.com/@PyCon2015/videos'
            ),
            'attr': (
                'PyCon 2015 - Videos',
                '',
                'PyCon 2015',
            ),
            'items': [
                ('G-uKNd5TSBw', 'Keynote - Guido van Rossum - PyCon 2015', date.fromisoformat('2015-04-16')),
                ('lNqtyi3sM-k', 'Keynote  - Gabriella Coleman - PyCon 2015', date.fromisoformat('2015-04-16')),
                ('2wDvzy6Hgxg', 'Type Hints  - Guido van Rossum - PyCon 2015', date.fromisoformat('2015-04-12')),
            ]
        },
    ]

    def setUp(self) -> None:
        storage = MockStorage()
        self.youtube = YouTube(
            storage,
            OwnerConfig(name='Podmaker', email='test@podmaker.dev')
        )

    def test_fetch(self) -> None:
        for case in self.cases:
            source = case['source']
            attr = case['attr']
            podcast = self.youtube.fetch(source)  # type: ignore[arg-type]
            self.assertEqual(urlparse(str(source.url)), podcast.link)  # type: ignore[attr-defined]
            self.assertEqual(attr[0], podcast.title)  # type: ignore[index]
            self.assertIsNotNone(podcast.image.ensure())
            self.assertEqual(attr[1], podcast.description)  # type: ignore[index]
            self.assertEqual('Podmaker', podcast.owner.name)  # type: ignore[union-attr]
            self.assertEqual('test@podmaker.dev', podcast.owner.email)  # type: ignore[union-attr]
            self.assertEqual(attr[2], podcast.author)  # type: ignore[index]
            self.assertEqual([], podcast.categories)
            self.assertFalse(podcast.explicit)
            self.assertEqual('en', podcast.language)
            items = case['items']
            for (idx, episode) in enumerate(podcast.items.ensure()):
                if idx >= len(items):  # type: ignore[arg-type]
                    break
                current = items[idx]  # type: ignore[index]
                self.assertEqual(current[0], episode.guid)
                self.assertEqual(current[1], episode.title)
                self.assertIsNotNone(episode.pub_date)
                if episode.pub_date is not None:
                    self.assertEqual(current[2], episode.pub_date.date())
                self.assertIsNotNone(episode.link)
                self.assertIsNotNone(episode.image.ensure())  # type: ignore[union-attr]
                self.assertEqual(urlparse('https://example.com'), episode.enclosure.ensure().url)
