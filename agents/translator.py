"""Translation agent for converting text to simplified Dutch."""

from typing import Optional, Dict, Any
import anthropic
from loguru import logger

from core.parser import TextSegment
from core.documentation import DocumentationTracker


class TranslatorAgent:
    """Agent for translating and simplifying text to Dutch."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.3,
        documentation_tracker: Optional[DocumentationTracker] = None
    ):
        """Initialize the translator agent.

        Args:
            api_key: Anthropic API key
            model: Model to use
            temperature: Temperature for generation
            documentation_tracker: Tracker for documenting decisions
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.doc_tracker = documentation_tracker

    def translate_segment(
        self,
        segment: TextSegment,
        target_age: str = "14-16"
    ) -> Dict[str, Any]:
        """Translate a text segment to simplified Dutch.

        Args:
            segment: Text segment to translate
            target_age: Target age range

        Returns:
            Dictionary containing translation and metadata
        """
        logger.info(f"Translating segment: {segment.id}")

        system_prompt = self._build_system_prompt(target_age)
        user_prompt = self._build_translation_prompt(segment)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            translated_text = response.content[0].text

            # Parse response to extract translation and notes
            result = self._parse_translation_response(translated_text)

            # Document interpretation decisions
            if self.doc_tracker and result.get('interpretation_notes'):
                for note in result['interpretation_notes']:
                    self.doc_tracker.record_interpretation(
                        segment_id=segment.id,
                        original_text=note.get('original', ''),
                        translated_text=note.get('translated', ''),
                        interpretation_type='translation_choice',
                        reason=note.get('reason', ''),
                        alternative_options=note.get('alternatives'),
                        confidence=note.get('confidence'),
                        agent='TranslatorAgent'
                    )

            logger.success(f"Completed translation of {segment.id}")
            return result

        except Exception as e:
            logger.error(f"Translation failed for {segment.id}: {e}")
            raise

    def _build_system_prompt(self, target_age: str) -> str:
        """Build the system prompt for translation.

        Args:
            target_age: Target age range

        Returns:
            System prompt string
        """
        return f"""You are an expert translator specializing in translating classical literature into simplified Dutch for students aged {target_age}.

Your task is to translate Plutarch's Lives from English to Dutch while:

1. **Maintaining Accuracy**: Preserve all historical facts, names, and events accurately
2. **Simplifying Language**: Use clear, accessible Dutch appropriate for {target_age} year old students
3. **Preserving Meaning**: Keep the original meaning and nuance, even when simplifying
4. **Cultural Context**: Adapt cultural references when needed, but document why
5. **Readability**: Create engaging, readable text that maintains the narrative flow

IMPORTANT GUIDELINES:
- Use modern Dutch spelling and grammar
- Simplify complex sentence structures without losing meaning
- Explain or adapt archaic terms and concepts
- Keep proper names in their familiar Dutch/Latin forms (e.g., "Theseus", "Romulus")
- Document any significant interpretation decisions
- When multiple translation options exist, choose the most accessible one

Your output should be structured as:

## Translation
[Your Dutch translation here]

## Interpretation Notes
[Document any significant translation decisions, explaining:]
- Original phrase/concept
- Your translation choice
- Reason for this choice
- Alternative options considered
- Confidence level (0-1)
"""

    def _build_translation_prompt(self, segment: TextSegment) -> str:
        """Build the translation prompt for a specific segment.

        Args:
            segment: Text segment to translate

        Returns:
            User prompt string
        """
        return f"""Please translate the following text from Plutarch's Lives to simplified Dutch for students aged 14-16.

**Segment Title**: {segment.title}

**Text to Translate**:
{segment.content}

Remember to:
1. Maintain historical accuracy
2. Use clear, accessible Dutch
3. Simplify complex structures
4. Document significant interpretation decisions

Provide your translation and any interpretation notes using the structure specified in the system prompt.
"""

    def _parse_translation_response(self, response: str) -> Dict[str, Any]:
        """Parse the translation response.

        Args:
            response: Raw response from the model

        Returns:
            Parsed result dictionary
        """
        result = {
            'translation': '',
            'interpretation_notes': []
        }

        # Split response into sections
        sections = response.split('##')

        for section in sections:
            section = section.strip()
            if not section:
                continue

            if section.lower().startswith('translation'):
                # Extract translation
                content = section.split('\n', 1)[1].strip() if '\n' in section else ''
                result['translation'] = content

            elif section.lower().startswith('interpretation notes'):
                # Extract interpretation notes
                content = section.split('\n', 1)[1].strip() if '\n' in section else ''
                notes = self._parse_interpretation_notes(content)
                result['interpretation_notes'] = notes

        # If no structured response, treat entire response as translation
        if not result['translation']:
            result['translation'] = response.strip()

        return result

    def _parse_interpretation_notes(self, notes_text: str) -> list:
        """Parse interpretation notes from text.

        Args:
            notes_text: Text containing notes

        Returns:
            List of parsed notes
        """
        notes = []

        # Simple parsing - can be enhanced with more structured format
        current_note = {}
        for line in notes_text.split('\n'):
            line = line.strip()
            if not line:
                if current_note:
                    notes.append(current_note)
                    current_note = {}
                continue

            if line.startswith('- Original:'):
                current_note['original'] = line.replace('- Original:', '').strip()
            elif line.startswith('- Translation:') or line.startswith('- Translated:'):
                current_note['translated'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Reason:'):
                current_note['reason'] = line.replace('- Reason:', '').strip()
            elif line.startswith('- Alternatives:'):
                alts = line.replace('- Alternatives:', '').strip()
                current_note['alternatives'] = [a.strip() for a in alts.split(',')]
            elif line.startswith('- Confidence:'):
                try:
                    conf = float(line.replace('- Confidence:', '').strip())
                    current_note['confidence'] = conf
                except ValueError:
                    pass

        if current_note:
            notes.append(current_note)

        return notes
