import sys
from dataclasses import dataclass
from urllib.parse import ParseResult, urlparse
from xml.etree.ElementTree import Element

from podmaker.rss.core import RSSComponent

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@dataclass
class Enclosure(RSSComponent):
    # URL of the episode audio file.
    url: ParseResult
    # Size of the episode audio file in bytes.
    length: int
    # The standard MIME type of the episode.
    type: str

    @property
    def xml(self) -> Element:
        return self._el_creator(
            'enclosure',
            attrib={'url': self.url.geturl(), 'length': str(self.length), 'type': self.type}
        )

    @classmethod
    def from_xml(cls, el: Element) -> Self:
        url = urlparse(cls._parse_required_attrib(el, '.', 'url'))
        length_str = cls._parse_required_attrib(el, '.', 'length')
        try:
            length = int(length_str)
        except ValueError:
            raise ValueError(f'length must be int: {length_str}')
        content_type = cls._parse_required_attrib(el, '.', 'type')
        return cls(
            url,
            length,
            content_type
        )

    def merge(self, other: Self) -> bool:
        return self._common_merge(other, ('url', 'length', 'type'))
