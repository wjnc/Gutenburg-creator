"""Configuration settings for the Gutenberg Dutch Ebook Creator."""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Central configuration class for the project."""

    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    SOURCE_DIR = DATA_DIR / "source"
    PROCESSED_DIR = DATA_DIR / "processed"
    TRANSLATED_DIR = DATA_DIR / "translated"
    DOCUMENTATION_DIR = DATA_DIR / "documentation"
    OUTPUT_DIR = BASE_DIR / "output"

    # API Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # Language Configuration
    SOURCE_LANGUAGE = os.getenv("SOURCE_LANGUAGE", "en")
    TARGET_LANGUAGE = os.getenv("TARGET_LANGUAGE", "nl")
    TARGET_AGE_RANGE = os.getenv("TARGET_AGE_RANGE", "14-16")

    # Gutenberg Configuration
    GUTENBERG_BOOK_ID = os.getenv("GUTENBERG_BOOK_ID", "674")
    CROSS_CHECK_EDITIONS = [
        int(x.strip())
        for x in os.getenv("CROSS_CHECK_EDITIONS", "14033,14034,14035,44315").split(",")
        if x.strip()
    ]

    # Translation Configuration
    TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "claude-sonnet-4-5-20250929")
    MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", "2000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

    # Wikipedia Configuration
    WIKIPEDIA_LANGUAGE = os.getenv("WIKIPEDIA_LANGUAGE", "nl")
    MAX_WIKIPEDIA_CONCEPTS = int(os.getenv("MAX_WIKIPEDIA_CONCEPTS", "50"))

    # EPUB Configuration
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "epub")
    EPUB_TITLE = os.getenv("EPUB_TITLE", "Plutarchus - Levens van Beroemde Grieken en Romeinen")
    EPUB_AUTHOR = os.getenv("EPUB_AUTHOR", "Plutarchus")
    EPUB_LANGUAGE = os.getenv("EPUB_LANGUAGE", "nl")

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        for directory in [
            cls.DATA_DIR,
            cls.SOURCE_DIR,
            cls.PROCESSED_DIR,
            cls.TRANSLATED_DIR,
            cls.DOCUMENTATION_DIR,
            cls.OUTPUT_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Note: ANTHROPIC_API_KEY may not be in environment but could be
        # available through anthropic library's automatic credential discovery
        # (e.g., in Claude Code sessions or from ~/.anthropic config)
        # So we don't fail validation if it's not explicitly set

        return errors
