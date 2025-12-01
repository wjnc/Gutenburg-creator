"""Tests for text parser module."""

import pytest
from pathlib import Path
from core.parser import TextParser, TextSegment


def test_text_parser_initialization():
    """Test parser initialization."""
    parser = TextParser()
    assert parser is not None
    assert parser.segments == []


def test_remove_gutenberg_boilerplate():
    """Test Gutenberg header/footer removal."""
    parser = TextParser()

    text_with_boilerplate = """
*** START OF THE PROJECT GUTENBERG EBOOK ***
This is the actual content.
*** END OF THE PROJECT GUTENBERG EBOOK ***
"""

    cleaned = parser._remove_gutenberg_boilerplate(text_with_boilerplate)
    assert "START OF" not in cleaned
    assert "END OF" not in cleaned
    assert "This is the actual content." in cleaned


def test_slugify():
    """Test slugification."""
    parser = TextParser()

    assert parser._slugify("Theseus") == "theseus"
    assert parser._slugify("The Life of Theseus") == "the_life_of_theseus"
    assert parser._slugify("Multiple   Spaces") == "multiple_spaces"


def test_create_chunk():
    """Test chunk creation."""
    parser = TextParser()

    parent = TextSegment(
        id="test_segment",
        title="Test Segment",
        content="Test content",
        level=1
    )

    chunk = parser._create_chunk(parent, 0, "Chunk content")

    assert chunk.id == "test_segment_chunk_000"
    assert chunk.parent_id == "test_segment"
    assert chunk.content == "Chunk content"
    assert chunk.level == 2
    assert chunk.metadata['chunk_number'] == 0
