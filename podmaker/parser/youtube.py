import logging
import os
from collections.abc import Generator
from datetime import datetime
from tempfile import TemporaryDirectory
from urllib.parse import ParseResult, urlparse

import yt_dlp

from podmaker.parser.core import Parser, Podcast
from podmaker.rss import Episode, Resource, Enclosure
from podmaker.storage import Storage


logger = logging.getLogger(__name__)


class NoneLogger:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class YouTube(Parser):
    def __init__(self, storage: Storage):
        self.storage = storage
        self.ydl_opts = {'logger': NoneLogger()}

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
                link=playlist['webpage_url'],
                title=playlist['title'],
                image=PlaylistThumbnail(playlist['thumbnails']),
                description=playlist['description'],
                owner=os.getenv('PM_OWNER', 'Podmaker'),
                author=playlist['uploader'],
                categories=playlist.get('tags', []),
            )
        return podcast

    def fetch_item(self, entries: Generator) -> Generator[Episode, None, None]:
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
                    duration=video_info['duration'],
                    pub_date=upload_at,
                )


class PlaylistThumbnail(Resource):
    def __init__(self, thumbnails: list[dict]):
        self.thumbnails = thumbnails

    def get(self) -> ParseResult | None:
        if len(self.thumbnails) == 0:
            return None
        thumbnail = max(self.thumbnails, key=lambda t: t['width'])
        return urlparse(thumbnail['url'])


class Audio(Resource):
    uri: ParseResult | None = None
    timeout = 30
    max_retries = 3

    def __init__(self, info: dict, ydl_opts: dict, storage: Storage):
        self.info = info
        self.ydl_opts: dict = {
            'format': 'ba',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        self.ydl_opts.update(ydl_opts)
        self.storage = storage
        self.cache: Enclosure | None = None

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

    def get(self) -> Enclosure | None:
        if self.cache is None:
            key = f'youtube/{self.info["id"]}.mp3'
            info = self.storage.check(key)
            if info:
                logger.info(f'audio already exists: {key}')
                url = info.uri
                length = info.size
            else:
                url, length = self.upload(key)
            self.cache = Enclosure(
                url=url,
                length=length,
                type='audio/mp3',
            )
        return self.cache
