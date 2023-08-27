from __future__ import annotations

import logging
import os
import tempfile
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from inspect import isgenerator
from tempfile import TemporaryDirectory
from typing import Any, Iterable
from urllib.parse import ParseResult, urlparse

import yt_dlp

from podmaker.config import OwnerConfig, SourceConfig
from podmaker.fetcher import Fetcher
from podmaker.rss import Enclosure, Episode, Owner, Podcast, Resource
from podmaker.rss.core import PlainResource
from podmaker.storage import Storage
from podmaker.util import exit_signal

logger = logging.getLogger(__name__)


class YouTube(Fetcher):
    def __init__(self, storage: Storage, owner_config: OwnerConfig | None):
        self.storage = storage
        self.ydl_opts = {
            'logger': logging.getLogger('yt_dlp'),
            'cachedir': tempfile.gettempdir(),
        }
        self.owner_config = owner_config

    def fetch_info(self, url: str) -> dict[str, Any]:
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(str(url), download=False, process=False)  # type: dict[str, Any]
            return info

    def fetch(self, source: SourceConfig) -> Podcast:
        info = self.fetch_info(str(source.url))
        if isgenerator(info.get('entries', None)):
            return self.fetch_entries(info, source)
        raise ValueError(f'unsupported url: {source.url}')

    def fetch_entries(self, info: dict[str, Any], source: SourceConfig) -> Podcast:
        logger.info(f'[{source.id}] parse entries: {source.url}')
        if self.owner_config:
            owner = Owner(name=self.owner_config.name, email=self.owner_config.email)
        else:
            owner = None
        podcast = Podcast(
            items=Entry(info.get('entries', []), self.ydl_opts, self.storage, source),
            link=urlparse(info['webpage_url']),
            title=source.name or info['title'],
            image=EntryThumbnail(info['thumbnails']),
            description=info['description'],
            owner=owner,
            author=info['uploader'],
            categories=info.get('tags', []),
        )
        return podcast


class Entry(Resource[Iterable[Episode]]):
    def __init__(
            self, entries: Iterable[dict[str, Any]], ydl_opts: dict[str, Any], storage: Storage, source: SourceConfig):
        self.entries = entries
        self.ydl_opts = ydl_opts
        self.storage = storage
        self.source = source

    def get(self) -> Iterable[Episode] | None:
        logger.debug(f'[{self.source.id}] fetch items')
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            is_empty = True
            for entry in self.entries:
                exit_signal.check()
                is_empty = False
                try:
                    video_info = ydl.extract_info(entry['url'], download=False)
                except yt_dlp.DownloadError as e:
                    logger.error(f'[{self.source.id}] failed to fetch item({entry["url"]}) due to {e}')
                    continue
                if self.source.regex and not self.source.regex.search(video_info['title']):
                    logger.info(f'[{self.source.id}] skip item {video_info["id"]} due to regex')
                    continue
                upload_at = datetime.strptime(video_info['upload_date'], '%Y%m%d').replace(tzinfo=timezone.utc)
                logger.info(f'[{self.source.id}] fetch item: {video_info["id"]}')
                yield Episode(
                    enclosure=Audio(video_info, self.ydl_opts, self.storage, self.source),
                    title=video_info['title'],
                    description=video_info['description'],
                    guid=video_info['id'],
                    duration=timedelta(seconds=video_info['duration']),
                    pub_date=upload_at,
                    link=urlparse(video_info['webpage_url']),
                    image=PlainResource(urlparse(video_info['thumbnail'])),
                )
            if is_empty:
                return None


class EntryThumbnail(Resource[ParseResult]):
    def __init__(self, thumbnails: list[dict[str, Any]]):
        self.thumbnails = thumbnails

    def get(self) -> ParseResult | None:
        if len(self.thumbnails) == 0:
            return None
        thumbnail = max(self.thumbnails, key=lambda t: t.get('width', 0))
        result: ParseResult = urlparse(thumbnail['url'])
        return result


class Audio(Resource[Enclosure]):
    def __init__(self, info: dict[str, Any], ydl_opts: dict[str, Any], storage: Storage, source: SourceConfig):
        self.info = info
        self.ydl_opts: dict[str, Any] = {
            'format': 'ba',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        self.ydl_opts.update(ydl_opts)
        self.storage = storage
        self.source = source

    def upload(self, key: str) -> tuple[ParseResult, int]:
        logger.debug(f'[{self.source.id}] upload audio: {key}')
        with TemporaryDirectory(prefix='podmaker_youtube_') as cache_dir:
            opts = {'paths': {'home': cache_dir}}
            opts.update(self.ydl_opts)
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info(f'[{self.source.id}] fetch audio: {self.info["id"]}')
                downloaded_info = ydl.extract_info(self.info['webpage_url'])
                audio_path = downloaded_info['requested_downloads'][0]['filepath']
                length = os.path.getsize(audio_path)
            with open(audio_path, 'rb') as f:
                logger.info(f'[{self.source.id}] upload audio: {key}')
                url = self.storage.put(f, key=key, content_type='audio/mp3')
        return url, length

    @lru_cache(maxsize=1)
    def get(self) -> Enclosure | None:
        logger.debug(f'[{self.source.id}] fetch audio: {self.info["id"]}')
        key = self.source.get_storage_key(f'youtube/{self.info["id"]}.mp3')
        info = self.storage.check(key)
        if info:
            logger.info(f'[{self.source.id}] audio already exists: {key}')
            url = info.uri
            length = info.size
        else:
            url, length = self.upload(key)
        return Enclosure(url=url, length=length, type='audio/mp3')
