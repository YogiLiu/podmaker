from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
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
        el.append(self.enclosure_element)
        el.append(self.title_element)
        if self.description:
            el.append(self.description_element)
            el.append(self.summary_element)
        if self.explicit is not None:
            el.append(self.explicit_element)
        if self.guid:
            el.append(self.guid_element)
        if self.duration:
            el.append(self.duration_element)
        if self.pub_date:
            el.append(self.pub_date_element)
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
    def enclosure_element(self) -> Element:
        return self.enclosure.ensure().xml

    @property
    def title_element(self) -> Element:
        return Element('title', text=self.title)

    @property
    def description_element(self) -> Element:
        if self.description is None:
            raise ValueError('description is required')
        return Element('description', text=self.description)

    @property
    def summary_element(self) -> Element:
        if self.description is None:
            raise ValueError('description is required')
        return itunes.el('summary', text=self.description)

    @property
    def explicit_element(self) -> Element:
        return itunes.el('explicit', text='yes' if self.explicit else 'no')

    @property
    def guid_element(self) -> Element:
        if self.guid is None:
            raise ValueError('empty guid field')
        return Element('guid', {'isPermaLink': 'false'}, text=self.guid)

    @property
    def duration_element(self) -> Element:
        if self.duration is None:
            raise ValueError('empty duration field')
        dur = math.ceil(self.duration.total_seconds())
        return itunes.el('duration', text=str(dur))

    @property
    def pub_date_element(self) -> Element:
        if self.pub_date is None:
            raise ValueError('empty pub_date field')
        return Element('pubDate', text=self.pub_date.strftime('%a, %d %b %Y %H:%M:%S %z'))
