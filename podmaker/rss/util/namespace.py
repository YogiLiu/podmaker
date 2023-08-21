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

    def el(self, tag: str, *, text: str| None = None, attrib: dict[str, str] | None = None) -> Element:
        el = Element(self(tag).text, attrib or {})
        if text is not None:
            el.text = text
        return el
