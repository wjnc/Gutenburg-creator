"""Cross-reference agent for comparing with other Gutenberg editions."""

from typing import Dict, Any, List, Optional
from pathlib import Path
import anthropic
from loguru import logger

from core.parser import TextSegment
from core.documentation import DocumentationTracker


class CrossReferenceAgent:
    """Agent for cross-checking translations against other editions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.2,
        documentation_tracker: Optional[DocumentationTracker] = None
    ):
        """Initialize the cross-reference agent.

        Args:
            api_key: Anthropic API key (optional, will use auto-discovery if not provided)
            model: Model to use
            temperature: Temperature for generation
            documentation_tracker: Tracker for documenting decisions
        """
        # If api_key is None, let anthropic library use automatic credential discovery
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = anthropic.Anthropic()
        self.model = model
        self.temperature = temperature
        self.doc_tracker = documentation_tracker

    def cross_check(
        self,
        primary_segment: TextSegment,
        comparison_texts: Dict[int, str],
        translation: str
    ) -> Dict[str, Any]:
        """Cross-check translation against other editions.

        Args:
            primary_segment: Primary text segment
            comparison_texts: Dictionary of edition_id -> text from other editions
            translation: Current Dutch translation

        Returns:
            Dictionary containing cross-check results
        """
        logger.info(f"Cross-checking segment: {primary_segment.id}")

        if not comparison_texts:
            logger.warning("No comparison texts provided")
            return {
                'checked': False,
                'reason': 'No comparison editions available'
            }

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_cross_check_prompt(
            primary_segment,
            comparison_texts,
            translation
        )

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

            result_text = response.content[0].text
            result = self._parse_cross_check_response(result_text)

            # Document cross-reference findings
            if self.doc_tracker and result.get('differences'):
                self.doc_tracker.record_cross_reference(
                    segment_id=primary_segment.id,
                    source_edition=int(primary_segment.metadata.get('source_edition', 674)),
                    comparison_editions=list(comparison_texts.keys()),
                    differences_found=[
                        d.get('description', '') for d in result['differences']
                    ],
                    resolution=result.get('recommendation', ''),
                    confidence=result.get('confidence', 0.8)
                )

            logger.success(f"Completed cross-check of {primary_segment.id}")
            return result

        except Exception as e:
            logger.error(f"Cross-check failed for {primary_segment.id}: {e}")
            raise

    def _build_system_prompt(self) -> str:
        """Build the system prompt for cross-checking.

        Returns:
            System prompt string
        """
        return """You are an expert in classical literature, specializing in Plutarch's Lives.

Your task is to compare different English translations of the same passage to:

1. **Identify Discrepancies**: Find significant differences between versions
2. **Assess Accuracy**: Determine which version is more accurate or complete
3. **Verify Translation**: Ensure the Dutch translation captures the essential meaning
4. **Recommend Improvements**: Suggest if the Dutch translation should be adjusted

IMPORTANT CONSIDERATIONS:
- Different translations may use different words but convey the same meaning
- Look for factual differences (names, dates, events), not just stylistic ones
- Consider historical context and scholarly accuracy
- Some variations are acceptable if meaning is preserved
- Focus on substantive differences that could affect understanding

Your output should be structured as:

## Comparison Summary
- Editions Compared: [count]
- Significant Differences Found: [count]
- Confidence in Primary Source: [0-1]

## Differences Identified
[For each significant difference:]
- Type: [factual/interpretive/stylistic]
- Location: [excerpt]
- Primary Version: [text]
- Alternative Version(s): [text]
- Impact: [high/medium/low]
- Analysis: [explanation]

## Dutch Translation Assessment
- Alignment: [well-aligned/needs-adjustment/problematic]
- Issues: [any problems identified]

## Recommendation
[Your recommendation for the Dutch translation:]
- Action: [keep-as-is/minor-revision/major-revision]
- Suggested Changes: [if applicable]
- Reasoning: [explanation]
"""

    def _build_cross_check_prompt(
        self,
        primary_segment: TextSegment,
        comparison_texts: Dict[int, str],
        translation: str
    ) -> str:
        """Build the cross-check prompt.

        Args:
            primary_segment: Primary text segment
            comparison_texts: Comparison texts
            translation: Dutch translation

        Returns:
            User prompt string
        """
        prompt = f"""Please compare these different English translations of the same passage from Plutarch's Lives.

**Primary Version (Edition {primary_segment.metadata.get('source_edition', 674)})**:
{primary_segment.content}

---

"""

        for edition_id, text in comparison_texts.items():
            prompt += f"**Alternative Version (Edition {edition_id})**:\n{text}\n\n---\n\n"

        prompt += f"""**Current Dutch Translation**:
{translation}

---

Please analyze:
1. Significant differences between the English versions
2. Which version seems more accurate or complete
3. Whether the Dutch translation aligns well with the best English version
4. Any recommendations for improving the Dutch translation

Provide your analysis using the structure specified in the system prompt.
"""

        return prompt

    def _parse_cross_check_response(self, response: str) -> Dict[str, Any]:
        """Parse the cross-check response.

        Args:
            response: Raw response from the model

        Returns:
            Parsed result dictionary
        """
        result = {
            'checked': True,
            'editions_compared': 0,
            'differences_count': 0,
            'confidence': 0.8,
            'differences': [],
            'alignment': 'unknown',
            'recommendation': '',
            'action': 'keep-as-is'
        }

        sections = response.split('##')

        for section in sections:
            section = section.strip()
            if not section:
                continue

            if section.lower().startswith('comparison summary'):
                result.update(self._parse_summary(section))

            elif section.lower().startswith('differences identified'):
                result['differences'] = self._parse_differences(section)
                result['differences_count'] = len(result['differences'])

            elif section.lower().startswith('dutch translation assessment'):
                result.update(self._parse_assessment(section))

            elif section.lower().startswith('recommendation'):
                result.update(self._parse_recommendation(section))

        return result

    def _parse_summary(self, summary_text: str) -> Dict[str, Any]:
        """Parse comparison summary.

        Args:
            summary_text: Summary text

        Returns:
            Dictionary with summary data
        """
        data = {}

        for line in summary_text.split('\n'):
            line = line.strip()

            if 'Editions Compared:' in line:
                try:
                    count = int(line.split(':', 1)[1].strip())
                    data['editions_compared'] = count
                except ValueError:
                    pass

            elif 'Confidence in Primary Source:' in line:
                try:
                    conf = float(line.split(':', 1)[1].strip())
                    data['confidence'] = conf
                except ValueError:
                    pass

        return data

    def _parse_differences(self, diff_text: str) -> List[Dict[str, Any]]:
        """Parse differences.

        Args:
            diff_text: Text containing differences

        Returns:
            List of differences
        """
        differences = []
        current_diff = {}

        for line in diff_text.split('\n'):
            line = line.strip()
            if not line:
                if current_diff:
                    differences.append(current_diff)
                    current_diff = {}
                continue

            if line.startswith('- Type:'):
                current_diff['type'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Location:'):
                current_diff['location'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Primary Version:'):
                current_diff['primary'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Alternative Version'):
                current_diff['alternative'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Impact:'):
                current_diff['impact'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Analysis:'):
                current_diff['analysis'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Description:'):
                current_diff['description'] = line.split(':', 1)[1].strip()

        if current_diff:
            differences.append(current_diff)

        return differences

    def _parse_assessment(self, assessment_text: str) -> Dict[str, Any]:
        """Parse Dutch translation assessment.

        Args:
            assessment_text: Assessment text

        Returns:
            Dictionary with assessment data
        """
        data = {}

        for line in assessment_text.split('\n'):
            line = line.strip()

            if 'Alignment:' in line:
                align = line.split(':', 1)[1].strip().lower()
                data['alignment'] = align

        return data

    def _parse_recommendation(self, rec_text: str) -> Dict[str, Any]:
        """Parse recommendation.

        Args:
            rec_text: Recommendation text

        Returns:
            Dictionary with recommendation data
        """
        data = {}
        full_text = []

        for line in rec_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            if 'Action:' in line:
                action = line.split(':', 1)[1].strip().lower()
                data['action'] = action
            else:
                full_text.append(line)

        data['recommendation'] = ' '.join(full_text)

        return data
