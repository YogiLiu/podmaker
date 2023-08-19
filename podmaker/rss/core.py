from __future__ import annotations

import sys
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar
from xml.etree.ElementTree import Element, fromstring, tostring

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


class RSSGenerator(metaclass=ABCMeta):
    @abstractmethod
    def render(self) -> Element:
        raise NotImplementedError


class RSSSerializer(RSSGenerator, metaclass=ABCMeta):
    @property
    def xml_str(self) -> str:
        el = self.render()
        return tostring(el, encoding='unicode')

    @property
    def xml_bytes(self) -> bytes:
        el = self.render()
        return tostring(el)


class RSSDeserializer(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_xml(cls, el: Element) -> Self:
        raise NotImplementedError

    @classmethod
    def from_rss(cls, rss: str | bytes) -> Self:
        if isinstance(rss, bytes):
            rss = rss.decode('utf-8')
        el: Element = fromstring(rss)
        return cls.from_xml(el)
