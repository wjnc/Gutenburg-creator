"""Module for downloading books from Project Gutenberg."""

import re
import time
from pathlib import Path
from typing import Optional, Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from loguru import logger


class GutenbergDownloader:
    """Downloads and manages Project Gutenberg books."""

    BASE_URL = "https://www.gutenberg.org"
    CACHE_DIR = Path("data/source")

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the downloader.

        Args:
            cache_dir: Directory to cache downloaded books
        """
        self.cache_dir = cache_dir or self.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Gutenberg Dutch Ebook Creator/1.0)'
        })

    def download_book(self, book_id: int, format: str = "txt") -> Path:
        """Download a book from Project Gutenberg.

        Args:
            book_id: The Gutenberg book ID
            format: Format to download (txt, html, epub)

        Returns:
            Path to the downloaded file
        """
        cache_file = self.cache_dir / f"{book_id}.{format}"

        if cache_file.exists():
            logger.info(f"Using cached file: {cache_file}")
            return cache_file

        logger.info(f"Downloading book {book_id} in {format} format...")

        # Try different URL patterns
        urls = self._get_download_urls(book_id, format)

        for url in urls:
            try:
                response = self._download_with_retry(url)
                if response.status_code == 200:
                    cache_file.write_bytes(response.content)
                    logger.success(f"Downloaded to: {cache_file}")
                    return cache_file
            except Exception as e:
                logger.warning(f"Failed to download from {url}: {e}")
                continue

        raise RuntimeError(f"Failed to download book {book_id} in format {format}")

    def _get_download_urls(self, book_id: int, format: str) -> List[str]:
        """Generate possible download URLs for a book.

        Args:
            book_id: The Gutenberg book ID
            format: Format to download

        Returns:
            List of possible URLs to try
        """
        urls = []

        if format == "txt":
            # Plain text UTF-8
            urls.append(f"{self.BASE_URL}/files/{book_id}/{book_id}-0.txt")
            urls.append(f"{self.BASE_URL}/files/{book_id}/{book_id}.txt")
            urls.append(f"{self.BASE_URL}/cache/epub/{book_id}/pg{book_id}.txt")
        elif format == "html":
            # HTML format
            urls.append(f"{self.BASE_URL}/files/{book_id}/{book_id}-h/{book_id}-h.htm")
            urls.append(f"{self.BASE_URL}/cache/epub/{book_id}/pg{book_id}.html")
        elif format == "epub":
            # EPUB format
            urls.append(f"{self.BASE_URL}/ebooks/{book_id}.epub3.images")
            urls.append(f"{self.BASE_URL}/ebooks/{book_id}.epub.images")

        return urls

    def _download_with_retry(
        self,
        url: str,
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> requests.Response:
        """Download with exponential backoff retry.

        Args:
            url: URL to download
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds

        Returns:
            Response object
        """
        delay = initial_delay

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                return response
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2

        raise RuntimeError(f"Failed to download after {max_retries} attempts")

    def get_book_metadata(self, book_id: int) -> Dict[str, str]:
        """Fetch metadata for a Gutenberg book.

        Args:
            book_id: The Gutenberg book ID

        Returns:
            Dictionary containing book metadata
        """
        url = f"{self.BASE_URL}/ebooks/{book_id}"

        try:
            response = self._download_with_retry(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            metadata = {
                'book_id': str(book_id),
                'title': '',
                'author': '',
                'language': '',
                'subjects': []
            }

            # Extract title
            title_elem = soup.find('h1', itemprop='name')
            if title_elem:
                metadata['title'] = title_elem.get_text(strip=True)

            # Extract author
            author_elem = soup.find('a', itemprop='creator')
            if author_elem:
                metadata['author'] = author_elem.get_text(strip=True)

            # Extract language
            lang_elem = soup.find('tr', {'property': 'dcterms:language'})
            if lang_elem:
                metadata['language'] = lang_elem.find('td').get_text(strip=True)

            return metadata

        except Exception as e:
            logger.error(f"Failed to fetch metadata: {e}")
            return {'book_id': str(book_id)}

    def download_multiple_editions(self, book_ids: List[int], format: str = "txt") -> Dict[int, Path]:
        """Download multiple editions/versions of books.

        Args:
            book_ids: List of Gutenberg book IDs
            format: Format to download

        Returns:
            Dictionary mapping book IDs to file paths
        """
        results = {}

        for book_id in book_ids:
            try:
                path = self.download_book(book_id, format)
                results[book_id] = path
            except Exception as e:
                logger.error(f"Failed to download book {book_id}: {e}")

        return results
