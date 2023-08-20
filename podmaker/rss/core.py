from __future__ import annotations

import sys
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar
from xml.etree.ElementTree import Element, fromstring, tostring

from podmaker.rss.util.namespace import NamespaceGenerator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

ResourceType = TypeVar('ResourceType')


class Resource(Generic[ResourceType], metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> ResourceType | None:
        raise NotImplementedError

    def ensure(self) -> ResourceType:
        resource = self.get()
        if resource is None:
            raise ValueError('Resource not found')
        return resource


class PlainResource(Resource[ResourceType]):
    """
    A resource that is not fetched from a remote location.
    It is useful for store resources that are already available in memory.
    """

    def __init__(self, resource: ResourceType):
        self.resource = resource

    def get(self) -> ResourceType:
        return self.resource


# noinspection HttpUrlsUsage
itunes = NamespaceGenerator('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')


class RSSComponent(metaclass=ABCMeta):
    @property
    @abstractmethod
    def xml(self) -> Element:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_xml(cls, el: Element) -> Self:
        raise NotImplementedError

    @abstractmethod
    def merge(self, other: Self) -> bool:
        """
        Merge the other component into this one.
        :return: Whether changes were made.
        """
        raise NotImplementedError

    @staticmethod
    def _el_creator(tag: str, text: str | None = None, attrib: dict[str, str] | None = None) -> Element:
        el = Element(tag, attrib or {})
        if text is not None:
            el.text = text
        return el

    def _common_merge(self, other: Self, field: str | tuple[str, ...]) -> bool:
        if isinstance(field, tuple):
            return any(self._common_merge(other, f) for f in field)
        a = getattr(self, field)
        b = getattr(other, field)
        if a != b:
            setattr(self, field, b)
            return True
        return False


# https://www.w3.org/TR/xml/#sec-pi
_pis = '<?xml version="1.0" encoding="UTF-8"?>\n'
_pis_bytes = _pis.encode('utf-8')


class RSSSerializer(RSSComponent, metaclass=ABCMeta):
    @property
    def str(self) -> str:
        s = tostring(self.xml, encoding='unicode')
        return _pis + s

    @property
    def bytes(self) -> bytes:
        s = tostring(self.xml)
        return _pis_bytes + s


class RSSDeserializer(RSSComponent, metaclass=ABCMeta):
    @classmethod
    def from_rss(cls, rss: str | bytes) -> Self:
        if isinstance(rss, bytes):
            rss = rss.decode('utf-8')
        el: Element = fromstring(rss)
        return cls.from_xml(el)
