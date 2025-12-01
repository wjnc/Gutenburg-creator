"""Module for parsing and segmenting Gutenberg texts."""

import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from loguru import logger


@dataclass
class TextSegment:
    """Represents a segment of text (chapter, life, section)."""

    id: str
    title: str
    content: str
    level: int  # 0 = book, 1 = life, 2 = chapter, 3 = section
    parent_id: Optional[str] = None
    metadata: Optional[Dict] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TextParser:
    """Parses and segments Project Gutenberg texts."""

    # Pattern to identify Gutenberg header/footer
    HEADER_PATTERN = re.compile(
        r'\*\*\* START OF (THIS|THE) PROJECT GUTENBERG.*?\*\*\*',
        re.IGNORECASE | re.DOTALL
    )
    FOOTER_PATTERN = re.compile(
        r'\*\*\* END OF (THIS|THE) PROJECT GUTENBERG.*?\*\*\*',
        re.IGNORECASE | re.DOTALL
    )

    def __init__(self):
        """Initialize the text parser."""
        self.segments: List[TextSegment] = []

    def parse_file(self, file_path: Path) -> List[TextSegment]:
        """Parse a text file into segments.

        Args:
            file_path: Path to the text file

        Returns:
            List of text segments
        """
        logger.info(f"Parsing file: {file_path}")

        content = file_path.read_text(encoding='utf-8')

        # Remove Gutenberg header and footer
        content = self._remove_gutenberg_boilerplate(content)

        # Parse into segments based on structure
        segments = self._segment_plutarch_lives(content)

        self.segments = segments
        logger.success(f"Parsed {len(segments)} segments")

        return segments

    def _remove_gutenberg_boilerplate(self, text: str) -> str:
        """Remove Project Gutenberg header and footer.

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        # Find and remove header
        header_match = self.HEADER_PATTERN.search(text)
        if header_match:
            text = text[header_match.end():]

        # Find and remove footer
        footer_match = self.FOOTER_PATTERN.search(text)
        if footer_match:
            text = text[:footer_match.start()]

        return text.strip()

    def _segment_plutarch_lives(self, text: str) -> List[TextSegment]:
        """Segment Plutarch's Lives into individual biographies.

        Args:
            text: Cleaned text content

        Returns:
            List of text segments
        """
        segments = []

        # Plutarch's Lives typically has a structure like:
        # THESEUS
        # [content]
        # ROMULUS
        # [content]
        # etc.

        # Pattern to match life titles (all caps, potentially with "THE LIFE OF")
        life_pattern = re.compile(
            r'\n([A-Z\s]{3,})\n',
            re.MULTILINE
        )

        matches = list(life_pattern.finditer(text))

        if not matches:
            # If no structure found, create single segment
            logger.warning("No clear structure found, creating single segment")
            segments.append(TextSegment(
                id="full_text",
                title="Full Text",
                content=text,
                level=0
            ))
            return segments

        # Process each life
        for i, match in enumerate(matches):
            title = match.group(1).strip()

            # Skip if this looks like a generic header
            if len(title) < 3 or title in ['CONTENTS', 'PREFACE', 'INTRODUCTION']:
                continue

            # Get content until next life or end
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()

            # Skip empty sections
            if len(content) < 100:
                continue

            # Clean up title
            title = title.title()
            title = re.sub(r'^The Life Of\s+', '', title, flags=re.IGNORECASE)

            segment_id = f"life_{i:03d}_{self._slugify(title)}"

            segments.append(TextSegment(
                id=segment_id,
                title=title,
                content=content,
                level=1,
                metadata={'position': i}
            ))

        logger.info(f"Found {len(segments)} lives")
        return segments

    def _slugify(self, text: str) -> str:
        """Convert text to a slug.

        Args:
            text: Text to slugify

        Returns:
            Slugified text
        """
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '_', text)
        text = text.strip('_')
        return text

    def split_into_chunks(
        self,
        segment: TextSegment,
        max_chunk_size: int = 2000
    ) -> List[TextSegment]:
        """Split a segment into smaller chunks for translation.

        Args:
            segment: Text segment to split
            max_chunk_size: Maximum characters per chunk

        Returns:
            List of smaller segments
        """
        chunks = []

        # Split by paragraphs first
        paragraphs = segment.content.split('\n\n')

        current_chunk = []
        current_size = 0
        chunk_num = 0

        for para in paragraphs:
            para_size = len(para)

            # If single paragraph is too large, split it
            if para_size > max_chunk_size:
                # Save current chunk if any
                if current_chunk:
                    chunks.append(self._create_chunk(
                        segment, chunk_num, '\n\n'.join(current_chunk)
                    ))
                    chunk_num += 1
                    current_chunk = []
                    current_size = 0

                # Split large paragraph by sentences
                sentences = re.split(r'([.!?]+\s+)', para)
                temp_chunk = []
                temp_size = 0

                for sentence in sentences:
                    if temp_size + len(sentence) > max_chunk_size and temp_chunk:
                        chunks.append(self._create_chunk(
                            segment, chunk_num, ''.join(temp_chunk)
                        ))
                        chunk_num += 1
                        temp_chunk = []
                        temp_size = 0

                    temp_chunk.append(sentence)
                    temp_size += len(sentence)

                if temp_chunk:
                    chunks.append(self._create_chunk(
                        segment, chunk_num, ''.join(temp_chunk)
                    ))
                    chunk_num += 1

            elif current_size + para_size > max_chunk_size:
                # Save current chunk and start new one
                if current_chunk:
                    chunks.append(self._create_chunk(
                        segment, chunk_num, '\n\n'.join(current_chunk)
                    ))
                    chunk_num += 1

                current_chunk = [para]
                current_size = para_size

            else:
                current_chunk.append(para)
                current_size += para_size + 2  # +2 for \n\n

        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                segment, chunk_num, '\n\n'.join(current_chunk)
            ))

        logger.info(f"Split '{segment.title}' into {len(chunks)} chunks")
        return chunks

    def _create_chunk(
        self,
        parent: TextSegment,
        chunk_num: int,
        content: str
    ) -> TextSegment:
        """Create a chunk segment.

        Args:
            parent: Parent segment
            chunk_num: Chunk number
            content: Chunk content

        Returns:
            TextSegment for the chunk
        """
        return TextSegment(
            id=f"{parent.id}_chunk_{chunk_num:03d}",
            title=f"{parent.title} (Part {chunk_num + 1})",
            content=content,
            level=parent.level + 1,
            parent_id=parent.id,
            metadata={
                'chunk_number': chunk_num,
                'parent_title': parent.title
            }
        )

    def save_segments(self, output_dir: Path) -> None:
        """Save segments to individual files.

        Args:
            output_dir: Directory to save segments
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for segment in self.segments:
            file_path = output_dir / f"{segment.id}.txt"
            file_path.write_text(segment.content, encoding='utf-8')

        logger.success(f"Saved {len(self.segments)} segments to {output_dir}")
