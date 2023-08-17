from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import timedelta, datetime
from typing import TypeVar, Generic
from urllib.parse import ParseResult


ResourceType = TypeVar('ResourceType')


class Resource(Generic[ResourceType], metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> ResourceType | None:
        raise NotImplementedError


@dataclass
class Enclosure:
    # URL of the episode audio file.
    url: ParseResult
    # Size of the episode audio file in bytes.
    length: int
    # The standard MIME type of the episode.
    type: str


@dataclass
class Episode:
    # Fully-qualified URL of the episode audio file, including the format extension (for example, .wav, .mp3).
    enclosure: Resource[Enclosure]
    # Title of the podcast episode.
    title: str
    # A plaintext description of the podcast.
    description: str | None = None
    # Indicates whether this episode contains explicit language or adult content.
    explicit: bool | None = False
    # A permanently-assigned, case-sensitive Globally Unique Identifier for a podcast episode.
    guid: str | None = None
    # Duration of the episode.
    duration: timedelta | None = None
    # Publication date of the episode, in RFC 822 (section 5.1) format.
    # https://www.rfc-editor.org/rfc/rfc822#section-5.1
    pub_date: datetime | None = None


@dataclass
class Podcast:
    # Defines an episodes. At least one element in the items.
    items: Iterable[Episode]
    # Fully-qualified URL of the homepage of the podcast.
    link: str
    # Name of the podcast.
    title: str
    # An image to associate with the podcast.
    image: Resource[ParseResult]
    # A plaintext description of the podcast.
    description: str
    # Manager's name for the podcast.
    owner: str
    # Text name(s) of the author(s) of this podcast.
    # This need not be the same as the owner value.
    author: str
    # The general topic of the podcast.
    categories: list[str] = field(default_factory=list)
    # Indicates whether the podcast is explicit language or adult content.
    explicit: bool = False
    # The two-letter language code of the podcast as defined by ISO 639-1.
    # https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
    language: str | None = None
