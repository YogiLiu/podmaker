from __future__ import annotations

from abc import ABC
from xml.etree.ElementTree import Element


class XMLParser(ABC):
    namespace: dict[str, str] = {}

    @classmethod
    def _parse_optional_text(cls, el: Element, xpath: str) -> str | None:
        text = el.findtext(xpath, namespaces=cls.namespace)
        if text is None:
            return None
        return text.strip()

    @classmethod
    def _parse_required_text(cls, el: Element, xpath: str) -> str:
        text = cls._parse_optional_text(el, xpath)
        if text is None:
            raise ValueError(f'{xpath} is required')
        return text

    @classmethod
    def _parse_optional_el(cls, el: Element, xpath: str) -> Element | None:
        return el.find(xpath, namespaces=cls.namespace)

    @classmethod
    def _parse_required_el(cls, el: Element, xpath: str) -> Element:
        target = cls._parse_optional_el(el, xpath)
        if target is None:
            raise ValueError(f'{xpath} is required')
        return target

    @classmethod
    def _parse_els(cls, el: Element, xpath: str) -> list[Element]:
        return el.findall(xpath, namespaces=cls.namespace)

    @classmethod
    def _parse_optional_attrib(cls, el: Element, xpath: str, attrib: str) -> str | None:
        target = cls._parse_optional_el(el, xpath)
        if target is None:
            return None
        attrib_value = target.get(attrib, None)
        if attrib_value is None:
            return None
        return attrib_value.strip()

    @classmethod
    def _parse_required_attrib(cls, el: Element, xpath: str, attrib: str) -> str:
        text = cls._parse_optional_attrib(el, xpath, attrib)
        if text is None:
            raise ValueError(f'attrib {attrib} of {xpath} is required')
        return text
