from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from tempfile import TemporaryDirectory
from typing import Any, Iterable
from urllib.parse import ParseResult, urlparse

import yt_dlp

from podmaker.config import OwnerConfig, SourceConfig
from podmaker.fetcher import Fetcher
from podmaker.rss import Enclosure, Episode, Owner, Podcast, Resource
from podmaker.rss.core import PlainResource
from podmaker.storage import Storage

logger = logging.getLogger(__name__)


_lock = threading.Lock()


class YouTube(Fetcher):
    def __init__(self, storage: Storage, owner: OwnerConfig | None):
        self.storage = storage
        self.ydl_opts = {'logger': logging.getLogger('yt_dlp')}
        self.owner = owner

    def fetch(self, source: SourceConfig) -> Podcast:
        with _lock:
            if source.url.path == "/playlist":
                return self.fetch_playlist(source)
            raise ValueError(f'unsupported url: {source.url}')

    def fetch_playlist(self, source: SourceConfig) -> Podcast:
        logger.info(f'fetch playlist: {source.url}')
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            playlist = ydl.extract_info(str(source.url), download=False, process=False)
            if self.owner:
                owner = Owner(name=self.owner.name, email=self.owner.email)
            else:
                owner = None
            podcast = Podcast(
                items=Playlist(playlist.get('entries', []), self.ydl_opts, self.storage, source),
                link=urlparse(playlist['webpage_url']),
                title=playlist['title'],
                image=PlaylistThumbnail(playlist['thumbnails']),
                description=playlist['description'],
                owner=owner,
                author=playlist['uploader'],
                categories=playlist.get('tags', []),
            )
        return podcast


class Playlist(Resource[Iterable[Episode]]):
    def __init__(
            self, entries: Iterable[dict[str, Any]], ydl_opts: dict[str, Any], storage: Storage, source: SourceConfig):
        self.entries = entries
        self.ydl_opts = ydl_opts
        self.storage = storage
        self.source = source

    def get(self) -> Iterable[Episode] | None:
        logger.debug('fetch items')
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            is_empty = True
            for entry in self.entries:
                is_empty = False
                video_info = ydl.extract_info(entry['url'], download=False)
                upload_at = datetime.strptime(video_info['upload_date'], '%Y%m%d').replace(tzinfo=timezone.utc)
                logger.info(f'fetch item: {video_info["id"]}')
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


class PlaylistThumbnail(Resource[ParseResult]):
    def __init__(self, thumbnails: list[dict[str, Any]]):
        self.thumbnails = thumbnails

    def get(self) -> ParseResult | None:
        if len(self.thumbnails) == 0:
            return None
        thumbnail = max(self.thumbnails, key=lambda t: t['width'])
        result: ParseResult = urlparse(thumbnail['url'])
        return result


class Audio(Resource[Enclosure]):
    uri: ParseResult | None = None
    timeout = 30
    max_retries = 3

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
        logger.debug(f'upload audio: {key}')
        with TemporaryDirectory(prefix='podmaker_youtube_') as cache_dir:
            opts = {'paths': {'home': cache_dir}}
            opts.update(self.ydl_opts)
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info(f'fetch audio: {self.info["id"]}')
                downloaded_info = ydl.extract_info(self.info['webpage_url'])
                audio_path = downloaded_info['requested_downloads'][0]['filepath']
                length = os.path.getsize(audio_path)
            with open(audio_path, 'rb') as f:
                logger.info(f'upload audio: {key}')
                url = self.storage.put(f, key=key, content_type='audio/mp3')
        return url, length

    @lru_cache(maxsize=1)
    def get(self) -> Enclosure | None:
        logger.debug(f'fetch audio: {self.info["id"]}')
        key = self.source.get_storage_key(f'youtube/{self.info["id"]}.mp3')
        info = self.storage.check(key)
        if info:
            logger.info(f'audio already exists: {key}')
            url = info.uri
            length = info.size
        else:
            url, length = self.upload(key)
        return Enclosure(url=url, length=length, type='audio/mp3')
