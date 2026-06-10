import logging

import requests

logger = logging.getLogger(__name__)

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    ),
}


class Fetcher:
    def __init__(self, url: str):
        self.url = url

    def fetch(self) -> dict | None:
        try:
            response = requests.get(self.url, headers=HTTP_HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("获取数据失败: %s", e)
            return None
