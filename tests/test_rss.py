import math
import unittest
from pathlib import Path
from xml.etree.ElementTree import fromstring

from dateutil.parser import parse

from podmaker.rss import Podcast
from podmaker.rss.core import namespace


class TestRSS(unittest.TestCase):
    def setUp(self) -> None:
        self.rss = Path('./data/example.rss').read_text()
        self.element = fromstring(self.rss)

    def test_from_rss(self) -> None:  # noqa: PLR0912, C901, PLR0915
        podcast = Podcast.from_rss(self.rss)
        self.assertEqual(self.element.findtext('.channel/link'), podcast.link.geturl())
        self.assertEqual(self.element.findtext('.channel/title'), podcast.title)
        self.assertEqual(
            self.element.find('.channel/itunes:image', namespaces=namespace).get('href'),  # type: ignore[union-attr]
            podcast.image.ensure().geturl()
        )
        self.assertEqual(self.element.findtext('.channel/description'), podcast.description)
        owner_name = self.element.findtext('.channel/itunes:owner/itunes:name', namespaces=namespace)
        if owner_name:
            self.assertEqual(owner_name, podcast.owner.name)
        else:
            self.assertIsNone(podcast.owner.name)
        self.assertEqual(
            self.element.findtext(
                '.channel/itunes:owner/itunes:email', namespaces=namespace),
            podcast.owner.email
        )
        self.assertEqual(
            self.element.findtext('.channel/itunes:author', namespaces=namespace),
            podcast.author
        )
        c_els = self.element.findall('.channel/itunes:category', namespaces=namespace)
        self.assertEqual(
            [c_el.text for c_el in c_els],
            podcast.categories
        )
        explicit = self.element.findtext('.channel/itunes:explicit', namespaces=namespace)
        if explicit == 'yes':
            self.assertTrue(podcast.explicit)
        else:
            self.assertFalse(podcast.explicit)
        language = self.element.findtext('.channel/language')
        if language:
            self.assertEqual(language, podcast.language)
        else:
            self.assertIsNone(podcast.explicit)
        item_els = self.element.findall('.channel/item')
        for idx, item in enumerate(podcast.items):
            el = item_els[idx]
            enclosure_el = el.find('.enclosure')
            self.assertEqual(
                enclosure_el.get('url'),  # type: ignore[union-attr]
                item.enclosure.ensure().url.geturl()
            )
            self.assertEqual(
                enclosure_el.get('type'),  # type: ignore[union-attr]
                item.enclosure.ensure().type
            )
            self.assertEqual(
                enclosure_el.get('length'),  # type: ignore[union-attr]
                str(item.enclosure.ensure().length)
            )
            self.assertEqual(el.findtext('title'), item.title)
            desc = el.findtext('description')
            if desc:
                self.assertEqual(desc, item.description)
            summary = el.findtext('itunes:summary')
            if summary:
                self.assertEqual(summary, item.description)
            explicit = el.findtext('itunes:explicit', namespaces=namespace)
            if explicit == 'yes':
                self.assertTrue(item.explicit)
            elif explicit == 'no':
                self.assertFalse(item.explicit)
            else:
                self.assertIsNone(item.explicit)
            self.assertEqual(el.findtext('guid'), item.guid)
            duration = el.findtext('itunes:duration', namespaces=namespace)
            if duration:
                if ':' in duration:
                    secs = 0
                    for c in duration.split(':'):
                        secs = secs * 60 + int(c)
                else:
                    secs = int(duration)
                self.assertEqual(secs, math.ceil(item.duration.total_seconds()))  # type: ignore[union-attr]
            else:
                self.assertIsNone(item.duration)
            pub_date = el.findtext('pubDate')
            if pub_date:
                self.assertEqual(parse(pub_date), item.pub_date)
            else:
                self.assertIsNone(item.pub_date)
