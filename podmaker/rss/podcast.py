import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from urllib.parse import ParseResult
from xml.etree.ElementTree import Element

from podmaker.rss.episode import Episode
from podmaker.rss.core import Resource, RSSSerializer

category_pattern = re.compile(r'^[\w &]+$')


@dataclass
class Podcast(RSSSerializer):
    # Defines an episodes. At least one element in the items.
    items: Iterable[Episode]
    # Fully-qualified URL of the homepage of the podcast.
    link: str
    # Name of the podcast.
    title: str
    # An image to associate with the podcast.
    image: Resource[ParseResult]
    # A plaintext description of the podcast.
    description: str
    # Manager's email for the podcast.
    owner: str
    # Text name(s) of the author(s) of this podcast.
    # This need not be the same as the owner value.
    author: str
    # The general topic of the podcast.
    categories: list[str] = field(default_factory=list)
    # Indicates whether the podcast is explicit language or adult content.
    explicit: bool = False
    # The two-letter language code of the podcast as defined by ISO 639-1.
    # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    language: str | None = None

    def render(self) -> Element:
        el = Element(
            'rss',
            {'version': '2.0', 'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        )
        channel = Element('channel')
        el.append(channel)
        channel.append(self.link_element)
        channel.append(self.title_element)
        channel.append(self.itunes_image_element)
        channel.append(self.image_element)
        channel.append(self.description_element)
        channel.append(self.summary_element)
        channel.append(self.owner_element)
        channel.append(self.author_element)
        for category in self.category_elements:
            channel.append(category)
        channel.append(self.explicit_element)
        if self.language:
            channel.append(self.language_element)
        for item in self.items_element:
            channel.append(item)
        return el

    @property
    def items_element(self) -> Iterable[Element]:
        for item in self.items:
            yield item.render()

    @property
    def link_element(self) -> Element:
        return Element('link', text=self.link)

    @property
    def title_element(self) -> Element:
        return Element('title', text=self.title)

    @property
    def itunes_image_element(self) -> Element:
        return Element('itunes:image', href=self.image.ensure().geturl())

    @property
    def image_element(self) -> Element:
        el = Element('image', href=self.image.ensure().geturl())
        el.append(Element('link', text=self.link))
        el.append(Element('title', text=self.title))
        el.append(Element('url', text=self.image.ensure().geturl()))
        return el

    @property
    def description_element(self) -> Element:
        return Element('description', text=self.description)

    @property
    def summary_element(self) -> Element:
        return Element('itunes:summary', text=self.description)

    @property
    def owner_element(self) -> Element:
        el = Element('itunes:owner')
        el.append(Element('itunes:name', text=self.owner))
        el.append(Element('itunes:email', text=self.owner))
        return el

    @property
    def author_element(self) -> Element:
        return Element('itunes:author', text=self.author)

    @property
    def category_elements(self) -> Iterable[Element]:
        for category in self.categories:
            category = self.parse_category(category)
            if category is not None:
                yield Element('itunes:category', text=category)

    @staticmethod
    def parse_category(category: str) -> str | None:
        if not category_pattern.match(category):
            return None
        return category.replace('&', '&amp;')

    @property
    def explicit_element(self) -> Element:
        return Element('itunes:explicit', text='yes' if self.explicit else 'no')

    @property
    def language_element(self) -> Element:
        return Element('language', text=self.language)
