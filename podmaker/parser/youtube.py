import logging
from collections.abc import Generator
from datetime import datetime
from tempfile import TemporaryDirectory
from urllib.parse import ParseResult, urlparse

import yt_dlp

from podmaker.parser.core import Parser, Info, Item, Resource
from podmaker.storage.core import Storage


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

    def fetch(self, uri: ParseResult) -> Info:
        if uri.path == "/playlist":
            return self.fetch_playlist(uri.geturl())
        raise NotImplementedError

    def fetch_playlist(self, url: str) -> Info:
        logger.info(f'fetch playlist: {url}')
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            playlist = ydl.extract_info(url, download=False, process=False)
            info = Info(
                author=playlist['uploader'],
                description=playlist.get('description', ''),
                thumbnail=PlaylistThumbnail(playlist.get('thumbnails', [])),
                items=self.fetch_item(playlist.get('entries', [])),
            )
        return info

    def fetch_item(self, entries: Generator) -> Generator[Item, None, None]:
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            for entry in entries:
                video = ydl.extract_info(entry['url'], download=False)
                upload_at = datetime.strptime(video['upload_date'], '%Y%m%d').date()
                logger.info(f'fetch item: {video["id"]}')
                yield Item(
                    id=video['id'],
                    title=video['title'],
                    description=video.get('description', ''),
                    thumbnail=ItemThumbnail(video.get('thumbnail', '')),
                    audio=Audio(video['original_url'], self.ydl_opts, self.storage),
                    upload_at=upload_at,
                )


class PlaylistThumbnail(Resource):
    def __init__(self, thumbnails: list[dict]):
        self.thumbnails = thumbnails

    def get(self) -> ParseResult | None:
        if len(self.thumbnails) == 0:
            return None
        thumbnail = max(self.thumbnails, key=lambda t: t['width'])
        return urlparse(thumbnail['url'])


class ItemThumbnail(Resource):
    def __init__(self, url: str):
        self.url = url

    def get(self) -> ParseResult | None:
        return urlparse(self.url)


class Audio(Resource):
    uri: ParseResult | None = None
    timeout = 30
    max_retries = 3

    def __init__(self, url: str, ydl_opts: dict, storage: Storage):
        self.url = url
        self.ydl_opts: dict = {
            'format': 'ba',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        self.ydl_opts.update(ydl_opts)
        self.storage = storage

    def get(self) -> ParseResult | None:
        if self.uri is None:
            with TemporaryDirectory(prefix='podmaker_youtube_') as cache_dir:
                opts = {'paths': {'home': cache_dir}}
                opts.update(self.ydl_opts)
                with yt_dlp.YoutubeDL(opts) as ydl:
                    logger.info(f'fetch audio: {self.url}')
                    info = ydl.extract_info(self.url)
                    audio_path = info['requested_downloads'][0]['filepath']
                    key = f'youtube/{info["id"]}.mp3'
                    is_exist = self.storage.check(key)
                    if is_exist:
                        logger.info(f'audio already exists: {key}')
                        url = self.storage.get_uri(key)
                    else:
                        with open(audio_path, 'rb') as f:
                            logger.info(f'upload audio: {key}')
                            url = self.storage.put(f, key=key, content_type='audio/mp3')
                self.uri = urlparse(url)
        return self.uri
