from __future__ import annotations

import logging
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime, parsedate_to_datetime
from typing import Any
from urllib.parse import ParseResult, urlparse
from xml.etree.ElementTree import Element

from podmaker.rss import Enclosure, Resource
from podmaker.rss.core import PlainResource, RSSComponent, itunes

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

logger = logging.getLogger(__name__)


@dataclass
class Episode(RSSComponent):
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
    # An episode link URL.
    link: ParseResult | None = None
    # The episode artwork.
    image: Resource[ParseResult] | None = None

    @property
    def xml(self) -> Element:
        el = Element('item')
        el.append(self._enclosure_el)
        el.append(self._title_el)
        el.append(self._itunes_title_el)
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
        if self.link:
            el.append(self._link_el)
        if self.image:
            el.append(self._image_el)
        return el

    @classmethod
    def from_xml(cls, el: Element) -> Self:
        enclosure = cls._parse_enclosure(el)
        itunes_title = cls._parse_optional_text(el, f'.{itunes("title")}')
        if itunes_title is None:
            title = cls._parse_required_text(el, '.title')
        else:
            title = itunes_title
        description = cls._parse_optional_text(el, '.description')
        if description is None:
            description = cls._parse_optional_text(el, f'.{itunes("summary")}')
        explicit_str = cls._parse_optional_text(el, f'.{itunes("explicit")}')
        explicit = explicit_str == 'yes' if explicit_str is not None else None
        guid = cls._parse_optional_text(el, '.guid')
        duration = cls._parse_duration(el)
        pub_date = cls._parse_pub_date(el)
        link_str = cls._parse_optional_text(el, '.link')
        if link_str is not None:
            link = urlparse(link_str)
        else:
            link = None
        image_url = cls._parse_optional_attrib(el, f'.{itunes("image")}', 'href')
        if image_url is not None:
            image = PlainResource(urlparse(image_url))
        else:
            image = None
        return cls(enclosure, title, description, explicit, guid, duration, pub_date, link, image)

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

    def __hash__(self) -> int:
        return hash(self.unique_id)

    @classmethod
    def _parse_pub_date(cls, el: Element) -> datetime | None:
        pub_date_str = cls._parse_optional_text(el, '.pubDate')
        if pub_date_str is None:
            return None
        try:
            dt = parsedate_to_datetime(pub_date_str)
        except (TypeError, ValueError):
            try:
                if pub_date_str.endswith('Z'):
                    pub_date_str = pub_date_str[:-1] + '+00:00'
                dt = datetime.fromisoformat(pub_date_str)
            except ValueError:
                logger.warning(f'invalid pubDate: {pub_date_str}')
                return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @classmethod
    def _parse_enclosure(cls, el: Element) -> PlainResource[Enclosure]:
        enclosure_el = cls._parse_required_el(el, '.enclosure')
        return PlainResource(Enclosure.from_xml(enclosure_el))

    @classmethod
    def _parse_duration(cls, el: Element) -> timedelta | None:
        duration_str = cls._parse_optional_text(el, f'.{itunes("duration")}')
        if duration_str is None:
            return None
        try:
            if ':' in duration_str:
                secs = 0
                for c in duration_str.split(':'):
                    secs = secs * 60 + int(c)
            else:
                secs = int(duration_str)
            return timedelta(seconds=secs)
        except ValueError:
            logger.warning(f'invalid duration: {duration_str}')
            return None

    @property
    def _enclosure_el(self) -> Element:
        return self.enclosure.ensure().xml

    @property
    def _title_el(self) -> Element:
        return self._el_creator('title', self.title)

    @property
    def _itunes_title_el(self) -> Element:
        return itunes.el('title', text=self.title)

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
        is_perma_link = 'false'
        if self.guid.startswith('http'):
            is_perma_link = 'true'
        return self._el_creator('guid', self.guid, {'isPermaLink': is_perma_link})

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
        return self._el_creator('pubDate', format_datetime(self.pub_date))

    @property
    def _link_el(self) -> Element:
        if self.link is None:
            raise ValueError('empty link field')
        return self._el_creator('link', self.link.geturl())

    @property
    def _image_el(self) -> Element:
        if self.image is None:
            raise ValueError('empty image field')
        return itunes.el('image', attrib={'href': self.image.ensure().geturl()})
