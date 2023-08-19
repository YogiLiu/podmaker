from __future__ import annotations

from abc import ABC
from xml.etree.ElementTree import Element

from podmaker.rss.core import itunes


class XMLParser(ABC):
    @staticmethod
    def _parse_optional(el: Element, xpath: str) -> str | None:
        return el.findtext(xpath, namespaces=itunes.namespace)

    @classmethod
    def _parse_required(cls, el: Element, xpath: str) -> str:
        text = cls._parse_optional(el, xpath)
        if text is None:
            raise ValueError(f'{xpath} is required')
        return text
