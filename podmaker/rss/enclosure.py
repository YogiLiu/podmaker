from dataclasses import dataclass
from urllib.parse import ParseResult
from xml.etree.ElementTree import Element

from podmaker.rss.core import RSSGenerator


@dataclass
class Enclosure(RSSGenerator):
    # URL of the episode audio file.
    url: ParseResult
    # Size of the episode audio file in bytes.
    length: int
    # The standard MIME type of the episode.
    type: str

    def render(self) -> Element:
        el = Element('enclosure')
        el.set('url', self.url.geturl())
        el.set('length', str(self.length))
        el.set('type', self.type)
        return el
