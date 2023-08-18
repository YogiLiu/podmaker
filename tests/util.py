from datetime import timedelta
from urllib.error import URLError
from urllib.request import urlopen


def network_available(url: str, timeout: timedelta = timedelta(seconds=10)) -> bool:
    try:
        urlopen(url, timeout=timeout.total_seconds())
        return True
    except URLError:
        return False
