from __future__ import annotations

import logging
import os
from collections.abc import Generator
from datetime import datetime, timedelta
from functools import lru_cache
from tempfile import TemporaryDirectory
from typing import Any
from urllib.parse import ParseResult, urlparse

import yt_dlp

from podmaker.config import OwnerConfig
from podmaker.fetcher import Fetcher
from podmaker.rss import Enclosure, Episode, Owner, Podcast, Resource
from podmaker.storage import Storage

logger = logging.getLogger(__name__)


class NoneLogger:
    def debug(self, msg: Any) -> None:
        pass

    def info(self, msg: Any) -> None:
        pass

    def warning(self, msg: Any) -> None:
        pass

    def error(self, msg: Any) -> None:
        pass


class YouTube(Fetcher):
    def __init__(self, storage: Storage, owner: OwnerConfig):
        self.storage = storage
        self.ydl_opts = {'logger': NoneLogger()}
        self.owner = owner

    def fetch(self, uri: ParseResult) -> Podcast:
        if uri.path == "/playlist":
            return self.fetch_playlist(uri.geturl())
        raise NotImplementedError

    def fetch_playlist(self, url: str) -> Podcast:
        logger.info(f'fetch playlist: {url}')
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            playlist = ydl.extract_info(url, download=False, process=False)
            podcast = Podcast(
                items=self.fetch_item(playlist.get('entries', [])),
                link=urlparse(playlist['webpage_url']),
                title=playlist['title'],
                image=PlaylistThumbnail(playlist['thumbnails']),
                description=playlist['description'],
                owner=Owner(name=self.owner.name, email=self.owner.email),
                author=playlist['uploader'],
                categories=playlist.get('tags', []),
            )
        return podcast

    def fetch_item(self, entries: Generator[dict[str, Any], None, None]) -> Generator[Episode, None, None]:
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            for entry in entries:
                video_info = ydl.extract_info(entry['url'], download=False)
                upload_at = datetime.strptime(video_info['upload_date'], '%Y%m%d')
                logger.info(f'fetch item: {video_info["id"]}')
                yield Episode(
                    enclosure=Audio(video_info, self.ydl_opts, self.storage),
                    title=video_info['title'],
                    description=video_info['description'],
                    guid=video_info['id'],
                    duration=timedelta(seconds=video_info['duration']),
                    pub_date=upload_at,
                )


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

    def __init__(self, info: dict[str, Any], ydl_opts: dict[str, Any], storage: Storage):
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

    def upload(self, key: str) -> tuple[ParseResult, int]:
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
        key = f'youtube/{self.info["id"]}.mp3'
        info = self.storage.check(key)
        if info:
            logger.info(f'audio already exists: {key}')
            url = info.uri
            length = info.size
        else:
            url, length = self.upload(key)
        return Enclosure(url=url, length=length, type='audio/mp3')
