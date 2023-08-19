from __future__ import annotations

import math
import unittest
from pathlib import Path
from typing import Any, Callable
from xml.etree.ElementTree import Element, fromstring

from dateutil.parser import parse

from podmaker.rss import Podcast
from podmaker.rss.core import itunes


def convert_to_seconds(duration: str) -> int:
    if ':' in duration:
        secs = 0
        for c in duration.split(':'):
            secs = secs * 60 + int(c)
    else:
        secs = int(duration)
    return secs


class TestRSS(unittest.TestCase):
    def setUp(self) -> None:
        self.rss = Path('data/rss.test.xml').read_text()
        self.element = fromstring(self.rss)

    def test_from_rss(self) -> None:  # noqa: PLR0912, C901, PLR0915
        podcast = Podcast.from_rss(self.rss)
        self.assertEqual(self.element.findtext('.channel/link'), podcast.link.geturl())
        self.assertEqual(self.element.findtext('.channel/title'), podcast.title)
        self.assertEqual(
            self.element.find(
                f'.channel/{itunes("image")}', namespaces=itunes.namespace
            ).get('href'),  # type: ignore[union-attr]
            podcast.image.ensure().geturl()
        )
        self.assertEqual(self.element.findtext('.channel/description'), podcast.description)
        owner_name = self.element.findtext(f'.channel/{itunes("owner")}/{itunes("name")}', namespaces=itunes.namespace)
        if owner_name:
            self.assertEqual(owner_name, podcast.owner.name)
        else:
            self.assertIsNone(podcast.owner.name)
        self.assertEqual(
            self.element.findtext(
                f'.channel/{itunes("owner")}/{itunes("email")}', namespaces=itunes.namespace),
            podcast.owner.email
        )
        self.assertEqual(
            self.element.findtext(f'.channel/{itunes("author")}', namespaces=itunes.namespace),
            podcast.author
        )
        c_els = self.element.findall(f'.channel/{itunes("category")}', namespaces=itunes.namespace)
        self.assertEqual(
            [c_el.text for c_el in c_els],
            podcast.categories
        )
        explicit = self.element.findtext(f'.channel/{itunes("explicit")}', namespaces=itunes.namespace)
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
            self.assertEqual(el.findtext('.title'), item.title)
            desc = el.findtext('.description')
            if desc:
                self.assertEqual(desc, item.description)
            summary = el.findtext(f'.{itunes("summary")}')
            if summary:
                self.assertEqual(summary, item.description)
            explicit = el.findtext(f'.{itunes("explicit")}', namespaces=itunes.namespace)
            if explicit == 'yes':
                self.assertTrue(item.explicit)
            elif explicit == 'no':
                self.assertFalse(item.explicit)
            else:
                self.assertIsNone(item.explicit)
            self.assertEqual(el.find('.guid').text, item.guid)  # type: ignore[union-attr]
            duration = el.findtext(f'.{itunes("duration")}', namespaces=itunes.namespace)
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

    def test_xml(self) -> None:
        cases: list[str | list[str] | dict[str, Any]] = [
            '.',
            '.channel',
            '.channel/title',
            f'.channel/{itunes("owner")}/{itunes("email")}',
            f'.channel/{itunes("author")}',
            '.channel/description',
            [
                '.channel/description',
                f'.channel/{itunes("summary")}'
            ],
            f'.channel/{itunes("image")}',
            [
                '.channel/title',
                '.channel/image/title'
            ],
            [
                '.channel/link',
                '.channel/image/link'
            ],
            {
                'a': f'.channel/{itunes("image")}',
                'b': '.channel/image/url',
                'action': lambda el: el.get('text') if el.tag == 'url' else el.get('href')
            },
            '.channel/language',
            '.channel/link',
            '.channel/item/[1]/title',
            '.channel/item/[1]/description',
            '.channel/item/[1]/pubDate',
            '.channel/item/[1]/enclosure',
            f'.channel/item/[1]/{itunes("duration")}',
            '.channel/item/[1]/guid',
            '.channel/item/[2]/title',
            '.channel/item/[2]/description',
            '.channel/item/[2]/pubDate',
            '.channel/item/[2]/enclosure',
            f'.channel/item/[2]/{itunes("duration")}',
            '.channel/item/[2]/guid',
        ]
        podcast = Podcast.from_rss(self.rss)
        xml = podcast.xml
        for case in cases:
            if isinstance(case, dict):
                a = self.element.find(case['a'])
                b = xml.find(case['b'])
                action: Callable[[Element], Any] = case['action']
                self.assertEqual(action(a), action(b))  # type: ignore[arg-type]
            else:
                if isinstance(case, list):
                    a = self.element.find(case[0])
                    b = xml.find(case[1])
                else:
                    a = self.element.find(case)
                    b = xml.find(case)
                if a.text:  # type: ignore[union-attr]
                    a.text = a.text.strip()  # type: ignore[union-attr]
                if b.text:  # type: ignore[union-attr]
                    b.text = b.text.strip()  # type: ignore[union-attr]
                a_t = a.text or a.attrib.pop('text', '')  # type: ignore[union-attr]
                b_t = b.text or b.attrib.pop('text', '')  # type: ignore[union-attr]
                if 'pubDate' in case:
                    self.assertEqual(parse(a_t), parse(b_t))  # type: ignore[arg-type]
                elif 'duration' in case:
                    self.assertEqual(convert_to_seconds(a_t), convert_to_seconds(b_t))  # type: ignore[arg-type]
                else:
                    self.assertEqual(a_t, b_t)
                self.assertEqual(a.attrib, b.attrib)  # type: ignore[union-attr]
