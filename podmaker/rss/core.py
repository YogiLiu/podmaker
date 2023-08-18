from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic
from xml.etree.ElementTree import Element, tostring

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
