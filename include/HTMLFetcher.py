from bs4 import BeautifulSoup
import requests
from include.DebugHelper import DebugHelper

class HTMLFetcher:
    """
    Responsible for fetching and parsing HTML content from a given URL.
    """
    def __init__(self, headers=None, timeout=10):
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.timeout = timeout

    def fetch_page(self, url, parser="html.parser") -> BeautifulSoup:
        """
        Fetch and parse HTML content from the given URL.

        Args:
            url (str): The URL to fetch.
            parser (str): The parser to use for BeautifulSoup.

        Returns:
            BeautifulSoup: Parsed HTML content or None if an error occurs.
        """
        DebugHelper().log(f"Fetching {url}", self.__class__.__qualname__)
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, parser)
        except requests.RequestException as e:
            DebugHelper().log(f"Error fetching {url}: {e}", self.__class__.__qualname__)
            return None