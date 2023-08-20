from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import ParseResult, urlparse
from xml.etree.ElementTree import Element

from podmaker.rss import Episode, Resource
from podmaker.rss.core import PlainResource, RSSDeserializer, RSSSerializer, itunes
from podmaker.rss.util.parse import XMLParser

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

_category_pattern = re.compile(r'^[\w &]+$')


@dataclass
class Owner:
    email: str
    name: str | None = None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Owner):
            return False
        return self.email == other.email and self.name == other.name


@dataclass
class Podcast(RSSSerializer, RSSDeserializer, XMLParser):
    # Defines an episodes. At least one element in the items.
    items: Resource[Iterable[Episode]]
    # Fully-qualified URL of the homepage of the podcast.
    link: ParseResult
    # Name of the podcast.
    title: str
    # An image to associate with the podcast.
    image: Resource[ParseResult]
    # A plaintext description of the podcast.
    description: str
    # Manager's email for the podcast.
    owner: Owner
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

    @property
    def xml(self) -> Element:
        el = Element('rss', {'version': '2.0'})
        channel = Element('channel')
        el.append(channel)
        channel.append(self._link_el)
        channel.append(self._title_el)
        channel.append(self._itunes_image_el)
        channel.append(self._image_el)
        channel.append(self._description_el)
        channel.append(self._summary_el)
        channel.append(self._owner_el)
        channel.append(self._author_el)
        for category in self._category_el:
            channel.append(category)
        channel.append(self._explicit_el)
        if self.language:
            channel.append(self._language_el)
        for item in self._items_el:
            channel.append(item)
        return el

    @classmethod
    def from_xml(cls, el: Element) -> Self:
        items = cls._parse_items(el)
        link = urlparse(cls._parse_required(el, '.channel/link'))
        title = cls._parse_required(el, '.channel/title')
        image = cls._parse_image(el)
        description = cls._parse_required(el, '.channel/description')
        owner = cls._parse_owner(el)
        author = cls._parse_required(el, f'.channel/{itunes("author")}')
        categories = cls._parse_categories(el)
        explicit = cls._parse_optional(el, f'.channel/{itunes("explicit")}') == 'yes'
        language = cls._parse_optional(el, '.channel/language')
        return cls(
            items,
            link,
            title,
            image,
            description,
            owner,
            author,
            categories,
            explicit,
            language
        )

    def merge(self, other: Self) -> bool:
        has_changed = self._common_merge(
            other,
            ('link', 'title', 'description', 'owner', 'author', 'explicit', 'language')
        )
        image_url = self.image.get()
        if image_url != other.image.get():
            self.image = other.image
            has_changed = True
        if set(self.categories) != set(other.categories):
            self.categories = other.categories
            has_changed = True
        if self._merge_items(other.items):
            has_changed = True
        return has_changed

    def _merge_items(self, others: Resource[Iterable[Episode]]) -> bool:
        new_items = []
        old_ids = set(i.unique_id for i in self.items.ensure())
        for item in others.ensure():
            if item.unique_id not in old_ids:
                new_items.append(item)
        if not new_items:
            return False
        sorted_items = sorted(
            list(self.items.ensure()) + new_items,
            key=lambda i: i.pub_date or 0,
            reverse=True
        )
        self.items = PlainResource(sorted_items)
        return True

    @classmethod
    def _parse_owner(cls, el: Element) -> Owner:
        owner_el = el.find(f'.channel/{itunes("owner")}', itunes.namespace)
        if owner_el is None:
            raise ValueError('owner is required')
        owner_name = cls._parse_optional(owner_el, f'.{itunes("name")}')
        owner_email = cls._parse_required(owner_el, f'.{itunes("email")}')
        return Owner(owner_email, owner_name)

    @staticmethod
    def _parse_items(el: Element) -> Resource[Iterable[Episode]]:
        item_els = el.findall('.channel/item')
        if not item_els:
            raise ValueError('items is required')
        items = []
        for item_el in item_els:
            items.append(Episode.from_xml(item_el))
        if not items:
            raise ValueError('items is required')
        return PlainResource(items)

    @staticmethod
    def _parse_categories(el: Element) -> list[str]:
        categories = []
        for category_el in el.findall(f'.channel/{itunes("category")}', itunes.namespace):
            if category_el.text:
                categories.append(category_el.text)
        return categories

    @staticmethod
    def _parse_image(el: Element) -> Resource[ParseResult]:
        image_el = el.find(f'.channel/{itunes("image")}', itunes.namespace)
        if image_el is not None and image_el.get('href'):
            return PlainResource(urlparse(image_el.get('href')))  # type: ignore[arg-type]
        image_url = el.findtext('.channel/image/url')
        if not image_url:
            raise ValueError('image or itunes:image is required')
        return PlainResource(urlparse(image_url))

    @property
    def _items_el(self) -> Iterable[Element]:
        is_empty = True
        for item in self.items.ensure():
            is_empty = False
            yield item.xml
        if is_empty:
            raise ValueError('items is required')

    @property
    def _link_el(self) -> Element:
        return self._el_creator('link', self.link.geturl())

    @property
    def _title_el(self) -> Element:
        return self._el_creator('title', self.title)

    @property
    def _itunes_image_el(self) -> Element:
        return itunes.el('image', href=self.image.ensure().geturl())

    @property
    def _image_el(self) -> Element:
        el = self._el_creator('image', self.image.ensure().geturl())
        el.append(self._el_creator('link', self.link.geturl()))
        el.append(self._el_creator('title', self.title))
        el.append(self._el_creator('url', self.image.ensure().geturl()))
        return el

    @property
    def _description_el(self) -> Element:
        return self._el_creator('description', self.description)

    @property
    def _summary_el(self) -> Element:
        return itunes.el('summary', text=self.description)

    @property
    def _owner_el(self) -> Element:
        el = itunes.el('owner')
        if self.owner.name:
            el.append(itunes.el('name', text=self.owner.name))
        el.append(itunes.el('email', text=self.owner.email))
        return el

    @property
    def _author_el(self) -> Element:
        return itunes.el('author', text=self.author)

    @property
    def _category_el(self) -> Iterable[Element]:
        for category in self.categories:
            parsed_category = self._parse_category(category)
            if parsed_category is not None:
                yield itunes.el('category', text=parsed_category)

    @staticmethod
    def _parse_category(category: str) -> str | None:
        if not _category_pattern.match(category):
            return None
        return category.replace('&', '&amp;')

    @property
    def _explicit_el(self) -> Element:
        return itunes.el('explicit', text='yes' if self.explicit else 'no')

    @property
    def _language_el(self) -> Element:
        if self.language is None:
            raise ValueError('empty language field')
        return self._el_creator('language', self.language)
