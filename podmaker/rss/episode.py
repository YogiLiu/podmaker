import math
from dataclasses import dataclass
from datetime import timedelta, datetime
from xml.etree.ElementTree import Element

from podmaker.rss.core import Resource, RSSGenerator

from podmaker.rss.enclosure import Enclosure


@dataclass
class Episode(RSSGenerator):
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

    def render(self) -> Element:
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

    @property
    def enclosure_element(self) -> Element:
        return self.enclosure.ensure().render()

    @property
    def title_element(self) -> Element:
        return Element('title', text=self.title)

    @property
    def description_element(self) -> Element:
        return Element('description', text=self.description)

    @property
    def summary_element(self) -> Element:
        return Element('itunes:summary', text=self.description)

    @property
    def explicit_element(self) -> Element:
        return Element('itunes:explicit', text='yes' if self.explicit else 'no')

    @property
    def guid_element(self) -> Element:
        return Element('guid', {'isPermaLink': 'false'}, text=self.guid)

    @property
    def duration_element(self) -> Element:
        dur = math.ceil(self.duration.total_seconds())
        return Element('itunes:duration', text=str(dur))

    @property
    def pub_date_element(self) -> Element:
        return Element('pubDate', text=self.pub_date.strftime('%A, %d %b %Y %H:%M:%S %z'))
