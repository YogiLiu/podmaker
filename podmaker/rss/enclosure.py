import sys
from dataclasses import dataclass
from urllib.parse import ParseResult, urlparse
from xml.etree.ElementTree import Element

from podmaker.rss import RSSComponent

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
        return Element(
            'enclosure',
            {'url': self.url.geturl(), 'length': str(self.length), 'type': self.type}
        )

    @classmethod
    def from_xml(cls, el: Element) -> Self:
        url = urlparse(el.get('url'))
        length_str = el.get('length')
        if length_str is None:
            raise ValueError('length is required')
        length = int(length_str)
        content_type = el.get('type')
        if content_type is None:
            raise ValueError('type is required')
        return cls(
            url,  # type: ignore[arg-type]
            length,
            content_type
        )
