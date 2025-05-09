from bs4 import BeautifulSoup
import requests
from include.DebugHelper import DebugHelper, time_func


class HTMLFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    @time_func()
    def fetch_page(self, url, parser="html.parser", timeout=10) -> BeautifulSoup:
        """Fetch and parse HTML page"""
        try:
            DebugHelper.log(f"Fetching {url}", self.__class__.__qualname__)
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, parser)
        except Exception as e:
            return None