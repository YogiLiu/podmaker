from __future__ import annotations

from xml.etree.ElementTree import Element, QName, register_namespace


class NamespaceGenerator:
    def __init__(self, prefix: str, uri: str):
        self.prefix = prefix
        self.url = uri
        register_namespace(prefix, uri)

    @property
    def namespace(self) -> dict[str, str]:
        return {self.prefix: self.url}

    def __call__(self, tag: str) -> QName:
        return QName(self.url, tag)

    def el(self, tag: str, attrib: dict[str, str] | None = None, **extra: str) -> Element:
        attrib = attrib or {}
        return Element(self(tag).text, attrib, **extra)
