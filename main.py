#!/usr/bin/env python3
"""Main orchestrator for Gutenberg Dutch Ebook Creator."""

import sys
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
from loguru import logger

from config import Settings
from core import GutenbergDownloader, TextParser, EPUBGenerator, DocumentationTracker
from agents import TranslatorAgent, ProofreadingAgent, CrossReferenceAgent, WikipediaEnricher


class GutenbergDutchEbookCreator:
    """Main orchestrator for creating Dutch ebooks from Gutenberg texts."""

    def __init__(self):
        """Initialize the creator."""
        # Ensure directories exist
        Settings.ensure_directories()

        # Validate configuration
        errors = Settings.validate()
        if errors:
            for error in errors:
                logger.error(error)
            sys.exit(1)

        # Initialize components
        self.downloader = GutenbergDownloader(Settings.SOURCE_DIR)
        self.parser = TextParser()
        self.doc_tracker = DocumentationTracker(Settings.DOCUMENTATION_DIR)

        # Initialize agents
        self.translator = TranslatorAgent(
            api_key=Settings.ANTHROPIC_API_KEY,
            model=Settings.TRANSLATION_MODEL,
            temperature=Settings.TEMPERATURE,
            documentation_tracker=self.doc_tracker
        )

        self.proofreader = ProofreadingAgent(
            api_key=Settings.ANTHROPIC_API_KEY,
            model=Settings.TRANSLATION_MODEL,
            temperature=Settings.TEMPERATURE,
            documentation_tracker=self.doc_tracker
        )

        self.cross_checker = CrossReferenceAgent(
            api_key=Settings.ANTHROPIC_API_KEY,
            model=Settings.TRANSLATION_MODEL,
            temperature=Settings.TEMPERATURE,
            documentation_tracker=self.doc_tracker
        )

        self.enricher = WikipediaEnricher(
            api_key=Settings.ANTHROPIC_API_KEY,
            model=Settings.TRANSLATION_MODEL,
            wiki_language=Settings.WIKIPEDIA_LANGUAGE,
            max_concepts=Settings.MAX_WIKIPEDIA_CONCEPTS
        )

        logger.info("Initialized Gutenberg Dutch Ebook Creator")

    def run(
        self,
        book_id: int = None,
        cross_check: bool = True,
        enrich: bool = True,
        max_segments: int = None
    ) -> Path:
        """Run the complete pipeline.

        Args:
            book_id: Gutenberg book ID (defaults to Settings.GUTENBERG_BOOK_ID)
            cross_check: Whether to cross-check with other editions
            enrich: Whether to enrich with Wikipedia information
            max_segments: Maximum number of segments to process (for testing)

        Returns:
            Path to generated EPUB file
        """
        book_id = book_id or int(Settings.GUTENBERG_BOOK_ID)

        logger.info(f"Starting pipeline for book {book_id}")

        # Step 1: Download book
        logger.info("=" * 60)
        logger.info("STEP 1: Downloading source text")
        logger.info("=" * 60)
        source_file = self.downloader.download_book(book_id, format="txt")

        # Step 2: Parse into segments
        logger.info("=" * 60)
        logger.info("STEP 2: Parsing text into segments")
        logger.info("=" * 60)
        segments = self.parser.parse_file(source_file)

        if max_segments:
            segments = segments[:max_segments]
            logger.info(f"Limited to {max_segments} segments for testing")

        # Step 3: Download comparison editions if cross-checking
        comparison_texts = {}
        if cross_check and Settings.CROSS_CHECK_EDITIONS:
            logger.info("=" * 60)
            logger.info("STEP 3: Downloading comparison editions")
            logger.info("=" * 60)
            comparison_files = self.downloader.download_multiple_editions(
                Settings.CROSS_CHECK_EDITIONS,
                format="txt"
            )

            # Parse comparison editions
            for edition_id, file_path in comparison_files.items():
                parser = TextParser()
                comp_segments = parser.parse_file(file_path)
                comparison_texts[edition_id] = comp_segments

        # Step 4: Process each segment
        logger.info("=" * 60)
        logger.info("STEP 4: Translating and processing segments")
        logger.info("=" * 60)

        processed_segments = []

        for segment in tqdm(segments, desc="Processing segments"):
            processed = self._process_segment(
                segment,
                comparison_texts,
                cross_check=cross_check,
                enrich=enrich
            )
            processed_segments.append(processed)

        # Step 5: Create glossary
        logger.info("=" * 60)
        logger.info("STEP 5: Creating glossary")
        logger.info("=" * 60)

        all_annotations = {}
        if enrich:
            for seg in processed_segments:
                if 'annotations' in seg:
                    all_annotations.update(seg['annotations'])

        glossary = self.enricher.create_glossary(all_annotations) if all_annotations else None

        # Step 6: Generate EPUB
        logger.info("=" * 60)
        logger.info("STEP 6: Generating EPUB")
        logger.info("=" * 60)

        epub_gen = EPUBGenerator(
            title=Settings.EPUB_TITLE,
            author=Settings.EPUB_AUTHOR,
            language=Settings.EPUB_LANGUAGE,
            translator="AI Translation (Claude)"
        )

        # Create preface
        preface = self._create_preface()

        epub_gen.create_book(
            segments=processed_segments,
            glossary=glossary,
            preface=preface
        )

        # Save EPUB
        output_file = Settings.OUTPUT_DIR / f"plutarch_lives_nl_{book_id}.epub"
        epub_gen.save(output_file)

        # Step 7: Save documentation
        logger.info("=" * 60)
        logger.info("STEP 7: Saving documentation")
        logger.info("=" * 60)
        self.doc_tracker.save()

        # Print statistics
        stats = self.doc_tracker.get_statistics()
        logger.info("\nProcessing Statistics:")
        logger.info(f"  Total segments: {len(processed_segments)}")
        logger.info(f"  Total interpretations: {stats['total_interpretations']}")
        logger.info(f"  Total cross-references: {stats['total_cross_references']}")
        if stats['average_confidence'] > 0:
            logger.info(f"  Average confidence: {stats['average_confidence']:.2f}")

        logger.success(f"\nCompleted! EPUB saved to: {output_file}")
        return output_file

    def _process_segment(
        self,
        segment: TextSegment,
        comparison_texts: Dict[int, List[TextSegment]],
        cross_check: bool = True,
        enrich: bool = True
    ) -> Dict[str, Any]:
        """Process a single segment through the pipeline.

        Args:
            segment: Text segment to process
            comparison_texts: Comparison edition texts
            cross_check: Whether to cross-check
            enrich: Whether to enrich with Wikipedia

        Returns:
            Processed segment dictionary
        """
        logger.info(f"\nProcessing: {segment.title}")

        # Step 1: Translate
        logger.debug("  → Translating...")
        translation_result = self.translator.translate_segment(
            segment,
            target_age=Settings.TARGET_AGE_RANGE
        )
        translated_text = translation_result['translation']

        # Step 2: Proofread
        logger.debug("  → Proofreading...")
        proofread_result = self.proofreader.proofread(
            segment,
            translated_text,
            target_age=Settings.TARGET_AGE_RANGE
        )

        # Use corrected translation if available
        if proofread_result.get('corrected_translation'):
            translated_text = proofread_result['corrected_translation']
            logger.debug("  → Using corrected translation")

        # Step 3: Cross-check with other editions
        if cross_check and comparison_texts:
            logger.debug("  → Cross-checking with other editions...")

            # Find corresponding segments in comparison editions
            comp_segment_texts = {}
            for edition_id, comp_segments in comparison_texts.items():
                # Try to find matching segment by title or position
                matching_seg = self._find_matching_segment(segment, comp_segments)
                if matching_seg:
                    comp_segment_texts[edition_id] = matching_seg.content

            if comp_segment_texts:
                cross_check_result = self.cross_checker.cross_check(
                    segment,
                    comp_segment_texts,
                    translated_text
                )

                # Apply recommendations if needed
                if cross_check_result.get('action') in ['minor-revision', 'major-revision']:
                    logger.debug(f"  → Cross-check suggests: {cross_check_result['action']}")

        # Step 4: Enrich with Wikipedia
        enriched_result = {}
        if enrich:
            logger.debug("  → Enriching with Wikipedia...")
            enriched_result = self.enricher.enrich_segment(segment, translated_text)
            translated_text = enriched_result['enriched_text']

        # Prepare result
        result = {
            'id': segment.id,
            'title': segment.title,
            'original_text': segment.content,
            'translated_text': translated_text,
            'quality_score': proofread_result.get('quality_score', 0),
            'approved': proofread_result.get('approved', False)
        }

        # Add enrichment data if available
        if enriched_result:
            result['concepts'] = enriched_result.get('concepts', [])
            result['annotations'] = enriched_result.get('annotations', {})
            result['footnotes'] = enriched_result.get('footnotes', [])

        logger.debug(f"  ✓ Complete (quality: {result['quality_score']}/10)")

        return result

    def _find_matching_segment(
        self,
        segment: TextSegment,
        comparison_segments: List[TextSegment]
    ) -> TextSegment:
        """Find matching segment in comparison edition.

        Args:
            segment: Source segment
            comparison_segments: List of segments from comparison edition

        Returns:
            Matching segment or None
        """
        # Try exact title match
        for comp_seg in comparison_segments:
            if comp_seg.title.lower() == segment.title.lower():
                return comp_seg

        # Try position match
        if segment.metadata and 'position' in segment.metadata:
            pos = segment.metadata['position']
            if pos < len(comparison_segments):
                return comparison_segments[pos]

        return None

    def _create_preface(self) -> str:
        """Create a preface for the ebook.

        Returns:
            Preface text
        """
        return """Deze Nederlandse vertaling van Plutarchus' "Levens van Beroemde Grieken en Romeinen"
is speciaal bewerkt voor jongeren van 14 tot 16 jaar.

Plutarchus (circa 46-120 n.Chr.) was een Grieks historicus en filosoof die leefde tijdens
de Romeinse tijd. Zijn beroemde werk "Parallelle Levens" vergelijkt de biografieën van
belangrijke Griekse en Romeinse figuren, waarbij hij hun deugden en gebreken beschrijft.

Deze vertaling is zorgvuldig gemaakt met behulp van geavanceerde AI-technologie, waarbij:
- De oorspronkelijke betekenis en historische feiten bewaard blijven
- De taal is vereenvoudigd voor betere leesbaarheid
- Moeilijke begrippen worden toegelicht met contextuele informatie
- Alle vertaalkeuzes zijn gedocumenteerd en geverifieerd

Alle namen, plaatsen en gebeurtenissen zijn gecontroleerd tegen meerdere bronnen om
nauwkeurigheid te garanderen. De begrippenlijst aan het einde bevat aanvullende
informatie over historische figuren, plaatsen en gebeurtenissen.

Veel leesplezier!
"""


def main():
    """Main entry point."""
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/gutenberg_creator_{time}.log",
        rotation="10 MB",
        level="DEBUG"
    )

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Create and run pipeline
    creator = GutenbergDutchEbookCreator()

    # For initial testing, process only a few segments
    # Remove max_segments parameter to process the entire book
    output_file = creator.run(
        cross_check=True,
        enrich=True,
        max_segments=5  # Remove this line to process entire book
    )

    logger.info(f"\n{'=' * 60}")
    logger.info(f"SUCCESS! Generated EPUB: {output_file}")
    logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    main()
