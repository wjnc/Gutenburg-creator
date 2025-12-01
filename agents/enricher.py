"""Wikipedia enrichment agent for adding contextual information."""

from typing import Dict, Any, List, Optional, Set
import re
import anthropic
from loguru import logger

try:
    import wikipediaapi
except ImportError:
    wikipediaapi = None

from core.parser import TextSegment


class WikipediaEnricher:
    """Agent for enriching text with Wikipedia contextual information."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        wiki_language: str = "nl",
        max_concepts: int = 50
    ):
        """Initialize the Wikipedia enricher.

        Args:
            api_key: Anthropic API key (optional, will use auto-discovery if not provided)
            model: Model to use
            wiki_language: Wikipedia language code
            max_concepts: Maximum concepts to enrich per segment
        """
        # If api_key is None, let anthropic library use automatic credential discovery
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = anthropic.Anthropic()
        self.model = model
        self.wiki_language = wiki_language
        self.max_concepts = max_concepts

        # Initialize Wikipedia API if available
        if wikipediaapi:
            self.wiki = wikipediaapi.Wikipedia(
                language=wiki_language,
                user_agent='GutenbergDutchEbookCreator/1.0'
            )
        else:
            self.wiki = None
            logger.warning("wikipediaapi not installed, some features may be limited")

        # Cache for Wikipedia lookups
        self.wiki_cache: Dict[str, Optional[str]] = {}

    def enrich_segment(
        self,
        segment: TextSegment,
        translated_text: str
    ) -> Dict[str, Any]:
        """Enrich a translated segment with Wikipedia information.

        Args:
            segment: Original text segment
            translated_text: Translated Dutch text

        Returns:
            Dictionary containing enriched text and annotations
        """
        logger.info(f"Enriching segment: {segment.id}")

        # Step 1: Identify key concepts
        concepts = self._identify_concepts(segment, translated_text)

        # Step 2: Fetch Wikipedia information
        wiki_info = {}
        for concept in concepts[:self.max_concepts]:
            info = self._get_wikipedia_info(concept)
            if info:
                wiki_info[concept] = info

        # Step 3: Create enriched version with annotations
        enriched_result = {
            'enriched_text': translated_text,
            'concepts': list(wiki_info.keys()),
            'annotations': wiki_info,
            'footnotes': self._create_footnotes(wiki_info)
        }

        logger.success(f"Enriched {segment.id} with {len(wiki_info)} concepts")
        return enriched_result

    def _identify_concepts(
        self,
        segment: TextSegment,
        translated_text: str
    ) -> List[str]:
        """Identify key concepts that need contextual information.

        Args:
            segment: Original text segment
            translated_text: Translated text

        Returns:
            List of concept names
        """
        logger.debug(f"Identifying concepts in {segment.id}")

        system_prompt = """You are an expert in classical history and literature.

Your task is to identify key historical concepts, people, places, and events in a text that would benefit from additional context for students aged 14-16.

Focus on:
- Historical figures and their roles
- Places and geographical locations
- Historical events and battles
- Cultural concepts and practices
- Mythological references
- Political institutions

Output only a comma-separated list of concepts, using their Dutch names if available.
Keep the list focused (maximum 20 most important concepts).
"""

        user_prompt = f"""Identify key concepts in this Dutch translation from Plutarch's Lives that would benefit from Wikipedia context:

**Title**: {segment.title}

**Text**:
{translated_text[:3000]}

Please provide a comma-separated list of the most important concepts.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            concepts_text = response.content[0].text.strip()

            # Parse comma-separated list
            concepts = [
                c.strip() for c in concepts_text.split(',')
                if c.strip() and len(c.strip()) > 2
            ]

            logger.debug(f"Identified {len(concepts)} concepts")
            return concepts

        except Exception as e:
            logger.error(f"Failed to identify concepts: {e}")
            return []

    def _get_wikipedia_info(self, concept: str) -> Optional[Dict[str, str]]:
        """Get Wikipedia information for a concept.

        Args:
            concept: Concept name

        Returns:
            Dictionary with Wikipedia info or None
        """
        # Check cache
        if concept in self.wiki_cache:
            cached = self.wiki_cache[concept]
            return cached if cached else None

        if not self.wiki:
            logger.warning("Wikipedia API not available")
            return None

        try:
            page = self.wiki.page(concept)

            if not page.exists():
                logger.debug(f"No Wikipedia page found for: {concept}")
                self.wiki_cache[concept] = None
                return None

            # Get summary (first paragraph)
            summary = page.summary

            # Limit length
            if len(summary) > 500:
                # Truncate at sentence boundary
                summary = summary[:500]
                last_period = summary.rfind('.')
                if last_period > 0:
                    summary = summary[:last_period + 1]

            info = {
                'title': page.title,
                'summary': summary,
                'url': page.fullurl
            }

            self.wiki_cache[concept] = info
            logger.debug(f"Retrieved Wikipedia info for: {concept}")
            return info

        except Exception as e:
            logger.debug(f"Failed to get Wikipedia info for {concept}: {e}")
            self.wiki_cache[concept] = None
            return None

    def _create_footnotes(self, wiki_info: Dict[str, Dict[str, str]]) -> List[Dict[str, str]]:
        """Create footnotes from Wikipedia information.

        Args:
            wiki_info: Dictionary of concept -> Wikipedia info

        Returns:
            List of footnote dictionaries
        """
        footnotes = []

        for i, (concept, info) in enumerate(wiki_info.items(), 1):
            footnote = {
                'number': i,
                'concept': concept,
                'text': info['summary'],
                'source': f"Wikipedia: {info['url']}"
            }
            footnotes.append(footnote)

        return footnotes

    def create_glossary(
        self,
        all_annotations: Dict[str, Dict[str, str]]
    ) -> str:
        """Create a glossary from all annotations.

        Args:
            all_annotations: All Wikipedia annotations collected

        Returns:
            Formatted glossary text
        """
        glossary_entries = []

        for concept in sorted(all_annotations.keys()):
            info = all_annotations[concept]
            entry = f"**{info['title']}**: {info['summary']}\n"
            glossary_entries.append(entry)

        glossary = "# Begrippenlijst\n\n"
        glossary += "\n".join(glossary_entries)

        return glossary
