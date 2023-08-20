from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from xml.etree.ElementTree import Element

from dateutil.parser import parse

from podmaker.rss import Enclosure, Resource
from podmaker.rss.core import PlainResource, RSSComponent, itunes
from podmaker.rss.util.parse import XMLParser

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@dataclass
class Episode(RSSComponent, XMLParser):
    # Fully-qualified URL of the episode audio file, including the format extension (for example, .wav, .mp3).
    enclosure: Resource[Enclosure]
    # Title of the podcast episode.
    title: str
    # A plaintext description of the podcast.
    description: str | None = None
    # Indicates whether this episode contains explicit language or adult content.
    explicit: bool | None = False
    # A permanently-assigned, case-sensitive Globally Unique Identifier for a podcast episode.
    guid: str | None = None
    # Duration of the episode.
    duration: timedelta | None = None
    # Publication date of the episode, in RFC 822 (section 5.1) format.
    # https://www.rfc-editor.org/rfc/rfc822#section-5.1
    pub_date: datetime | None = None

    @property
    def xml(self) -> Element:
        el = Element('item')
        el.append(self._enclosure_el)
        el.append(self._title_el)
        if self.description:
            el.append(self._description_el)
            el.append(self._summary_e)
        if self.explicit is not None:
            el.append(self._explicit_el)
        if self.guid:
            el.append(self._guid_el)
        if self.duration:
            el.append(self._duration_el)
        if self.pub_date:
            el.append(self._pub_date_el)
        return el

    @classmethod
    def from_xml(cls, el: Element) -> Self:
        enclosure = cls._parse_enclosure(el)
        title = cls._parse_required(el, '.title')
        description = el.findtext('.description')
        if description is None:
            description = el.findtext(f'.{itunes("summary")}', namespaces=itunes.namespace)
        explicit_str = cls._parse_optional(el, f'.{itunes("explicit")}')
        explicit = explicit_str == 'yes' if explicit_str is not None else None
        guid = cls._parse_optional(el, '.guid')
        duration = cls._parse_duration(el)
        pub_date_str = cls._parse_optional(el, '.pubDate')
        pub_date = parse(pub_date_str) if pub_date_str is not None else None
        return cls(enclosure, title, description, explicit, guid, duration, pub_date)

    def merge(self, other: Self) -> bool:
        has_changed = False
        enclosure = self.enclosure.ensure()
        if enclosure.merge(other.enclosure.ensure()):
            has_changed = True
            self.enclosure = PlainResource(enclosure)
        return any([
            has_changed,
            self._common_merge(
                other,
                ('title', 'description', 'explicit', 'guid', 'duration', 'pub_date')
            )
        ])

    @property
    def unique_id(self) -> str:
        if self.guid is None:
            return self.enclosure.ensure().url.geturl()
        return self.guid

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Episode):
            return False
        return self.unique_id == other.unique_id

    @staticmethod
    def _parse_enclosure(el: Element) -> PlainResource[Enclosure]:
        enclosure_el = el.find('.enclosure')
        if enclosure_el is None:
            raise ValueError('enclosure is required')
        return PlainResource(Enclosure.from_xml(enclosure_el))

    @staticmethod
    def _parse_duration(el: Element) -> timedelta | None:
        duration_str = el.findtext(f'.{itunes("duration")}', namespaces=itunes.namespace)
        if duration_str is None:
            return None
        if ':' in duration_str:
            secs = 0
            for c in duration_str.split(':'):
                secs = secs * 60 + int(c)
            return timedelta(seconds=int(secs))
        return timedelta(seconds=int(duration_str))

    @property
    def _enclosure_el(self) -> Element:
        return self.enclosure.ensure().xml

    @property
    def _title_el(self) -> Element:
        return self._el_creator('title', self.title)

    @property
    def _description_el(self) -> Element:
        if self.description is None:
            raise ValueError('description is required')
        return self._el_creator('description', self.description)

    @property
    def _summary_e(self) -> Element:
        if self.description is None:
            raise ValueError('description is required')
        return itunes.el('summary', text=self.description)

    @property
    def _explicit_el(self) -> Element:
        return itunes.el('explicit', text='yes' if self.explicit else 'no')

    @property
    def _guid_el(self) -> Element:
        if self.guid is None:
            raise ValueError('empty guid field')
        return self._el_creator('guid', self.guid, {'isPermaLink': 'false'})

    @property
    def _duration_el(self) -> Element:
        if self.duration is None:
            raise ValueError('empty duration field')
        dur = math.ceil(self.duration.total_seconds())
        return itunes.el('duration', text=str(dur))

    @property
    def _pub_date_el(self) -> Element:
        if self.pub_date is None:
            raise ValueError('empty pub_date field')
        return self._el_creator('pubDate', self.pub_date.strftime('%a, %d %b %Y %H:%M:%S %z'))
