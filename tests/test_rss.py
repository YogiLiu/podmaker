from __future__ import annotations

import math
import unittest
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse
from xml.etree.ElementTree import Element, fromstring

from podmaker.rss import Episode, Podcast
from podmaker.rss.core import PlainResource, Resource, itunes


def convert_to_seconds(duration: str) -> int:
    if ':' in duration:
        secs = 0
        for c in duration.split(':'):
            secs = secs * 60 + int(c)
    else:
        secs = int(duration)
    return secs


def find_strip_text(el: Element, path: str, namespaces: dict[str, str] | None = None) -> str | None:
    text = el.findtext(path, namespaces=namespaces)
    if text:
        return text.strip()
    return None


class TestRSS(unittest.TestCase):
    def setUp(self) -> None:
        self.rss_docs = [
            Path('data/apple.rss.test.xml').read_text(),
            Path('data/google.rss.test.xml').read_text(),
        ]
        self.elements = [
            fromstring(r)
            for r in self.rss_docs
        ]

    def test_from_rss(self) -> None:  # noqa: PLR0912, C901, PLR0915
        for i, element in enumerate(self.elements):
            doc = self.rss_docs[i]
            podcast = Podcast.from_rss(doc)
            self.assertEqual(find_strip_text(element, '.channel/link'), podcast.link.geturl())
            self.assertEqual(find_strip_text(element, '.channel/title'), podcast.title)
            self.assertEqual(
                element.find(
                    f'.channel/{itunes("image")}', namespaces=itunes.namespace
                ).get('href'),  # type: ignore[union-attr]
                podcast.image.ensure().geturl()
            )
            self.assertEqual(find_strip_text(element, '.channel/description'), podcast.description)
            owner_el = element.find(f'.channel/{itunes("owner")}', namespaces=itunes.namespace)
            if owner_el is not None:
                owner_name = find_strip_text(owner_el, f'.{itunes("name")}')
                if owner_name:
                    self.assertEqual(owner_name, podcast.owner.name)  # type: ignore[union-attr]
                else:
                    self.assertIsNone(podcast.owner.name)  # type: ignore[union-attr]
                self.assertEqual(
                    find_strip_text(owner_el, f'.{itunes("email")}'),
                    podcast.owner.email  # type: ignore[union-attr]
                )
            self.assertEqual(
                find_strip_text(element, f'.channel/{itunes("author")}', namespaces=itunes.namespace),
                podcast.author
            )
            c_els = element.findall(f'.channel/{itunes("category")}', namespaces=itunes.namespace)
            self.assertEqual(
                [c_el.text.strip() for c_el in c_els],  # type: ignore[union-attr]
                podcast.categories
            )
            explicit = find_strip_text(element, f'.channel/{itunes("explicit")}', namespaces=itunes.namespace)
            if explicit == 'yes':
                self.assertTrue(podcast.explicit)
            else:
                self.assertFalse(podcast.explicit)
            language = find_strip_text(element, '.channel/language')
            if language:
                self.assertEqual(language, podcast.language)
            else:
                self.assertIsNone(podcast.explicit)
            item_els = element.findall('.channel/item')
            for j, item in enumerate(podcast.items.ensure()):
                el = item_els[j]
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
                if find_strip_text(el, '.title'):
                    self.assertEqual(find_strip_text(el, '.title'), item.title)
                else:
                    self.assertEqual(find_strip_text(el, f'.{itunes("title")}', namespaces=itunes.namespace),
                                     item.title)
                desc = find_strip_text(el, '.description')
                if desc:
                    self.assertEqual(desc, item.description)
                summary = find_strip_text(el, f'.{itunes("summary")}')
                if summary:
                    self.assertEqual(summary, item.description)
                explicit = find_strip_text(el, f'.{itunes("explicit")}', namespaces=itunes.namespace)
                if explicit == 'yes':
                    self.assertTrue(item.explicit)
                elif explicit == 'no':
                    self.assertFalse(item.explicit)
                else:
                    self.assertFalse(item.explicit)
                self.assertEqual(el.find('.guid').text, item.guid)  # type: ignore[union-attr]
                duration = find_strip_text(el, f'.{itunes("duration")}', namespaces=itunes.namespace)
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
                pub_date = find_strip_text(el, 'pubDate')
                if pub_date:
                    try:
                        dt = parsedate_to_datetime(pub_date)
                    except (TypeError, ValueError):
                        dt = datetime.fromisoformat(pub_date)
                    self.assertEqual(dt.date(), item.pub_date.date())  # type: ignore[union-attr]
                    self.assertEqual(dt.time(), item.pub_date.time())  # type: ignore[union-attr]
                else:
                    self.assertIsNone(item.pub_date)

    def test_xml(self) -> None:  # noqa: PLR0912, C901
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
                'action': lambda el: el.text if el.tag == 'url' else el.get('href')
            },
            '.channel/language',
            '.channel/link',
            '.channel/item/[1]/title',
            '.channel/item/[1]/description',
            '.channel/item/[1]/pubDate',
            '.channel/item/[1]/enclosure',
            f'.channel/item/[1]/{itunes("duration")}',
            '.channel/item/[1]/guid',
            '.channel/item/[1]/link',
            {
                'a': f'.channel/item/[1]/{itunes("image")}',
                'b': f'.channel/item/[1]/{itunes("image")}',
                'action': lambda el: el.text if el.tag == 'url' else el.get('href')
            },
            '.channel/item/[2]/title',
            '.channel/item/[2]/description',
            '.channel/item/[2]/pubDate',
            '.channel/item/[2]/enclosure',
            f'.channel/item/[2]/{itunes("duration")}',
            '.channel/item/[2]/guid',
            '.channel/item/[2]/link',
            {
                'a': f'.channel/item/[2]/{itunes("image")}',
                'b': f'.channel/item/[3]/{itunes("image")}',
                'action': lambda el: el.text if el.tag == 'url' else el.get('href')
            },
        ]
        for idx, element in enumerate(self.elements):
            doc = self.rss_docs[idx]
            podcast = Podcast.from_rss(doc)
            xml = podcast.xml
            for case in cases:
                if isinstance(case, dict):
                    a = element.find(case['a'])
                    if a is None:
                        continue
                    b = xml.find(case['b'])
                    action: Callable[[Element], Any] = case['action']
                    self.assertEqual(action(a), action(b), case)  # type: ignore[arg-type]
                else:
                    if isinstance(case, list):
                        a = element.find(case[0])
                        b = xml.find(case[1])
                    else:
                        a = element.find(case)
                        b = xml.find(case)
                    if a is None:
                        continue
                    if a.text:
                        a.text = a.text.strip()
                    if b.text:  # type: ignore[union-attr]
                        b.text = b.text.strip()  # type: ignore[union-attr]
                    a_t = a.text or a.attrib.pop('text', '')
                    b_t = b.text or b.attrib.pop('text', '')  # type: ignore[union-attr]
                    if 'pubDate' in case:
                        self.assertEqual(
                            parsedate_to_datetime(a_t), parsedate_to_datetime(b_t), case)  # type: ignore[arg-type]
                    elif 'duration' in case:
                        self.assertEqual(convert_to_seconds(a_t), convert_to_seconds(b_t),  # type: ignore[arg-type]
                                         case)
                    else:
                        self.assertEqual(a_t, b_t, case)
                    b_attr = b.attrib.copy()  # type: ignore[union-attr]
                    if 'isPermaLink' not in a.attrib:
                        b_attr.pop('isPermaLink', None)
                    self.assertEqual(a.attrib, b_attr, case)

    def test_merge(self) -> None:
        for doc in self.rss_docs:
            ap = Podcast.from_rss(doc)
            bp = Podcast.from_rss(doc)
            self.assertFalse(ap.merge(bp))
            items = list(bp.items.ensure())
            items.insert(
                0,
                Episode(
                    enclosure=items[0].enclosure,
                    title='foo',
                    description='bar',
                    guid='baz',
                    duration=items[0].duration,
                    explicit=False,
                    pub_date=datetime.now(timezone.utc),
                )
            )
            cases = [
                ('items', PlainResource(items)),
                ('link', urlparse('https://example.com')),
                ('title', 'foo'),
                ('image', PlainResource(urlparse('https://example.com/image.png'))),
                ('description', 'bar'),
                ('author', 'baz'),
                ('categories', ['foo', 'bar']),
                ('explicit', True),
                ('language', 'ja'),
            ]
            for field, value in cases:
                setattr(bp, field, value)
                self.assertTrue(ap.merge(bp), f'{field} is not merged')
                if isinstance(value, Resource):
                    ar = getattr(ap, field).get()
                    br = getattr(bp, field).get()
                    if isinstance(ar, list):
                        ar = set(ar)
                        br = set(br)
                    self.assertEqual(ar, br, f'{field} is not merged: {value}')
                else:
                    self.assertEqual(getattr(ap, field), value, f'{field} is not merged: {value}')
