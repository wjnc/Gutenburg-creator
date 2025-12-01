"""Proofreading agent for verifying translation quality and completeness."""

from typing import Dict, Any, Optional
import anthropic
from loguru import logger

from core.parser import TextSegment
from core.documentation import DocumentationTracker


class ProofreadingAgent:
    """Agent for proofreading and verifying translations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.2,
        documentation_tracker: Optional[DocumentationTracker] = None
    ):
        """Initialize the proofreading agent.

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

    def proofread(
        self,
        original_segment: TextSegment,
        translated_text: str,
        target_age: str = "14-16"
    ) -> Dict[str, Any]:
        """Proofread a translation.

        Args:
            original_segment: Original text segment
            translated_text: Translated text
            target_age: Target age range

        Returns:
            Dictionary containing proofreading results
        """
        logger.info(f"Proofreading segment: {original_segment.id}")

        system_prompt = self._build_system_prompt(target_age)
        user_prompt = self._build_proofread_prompt(original_segment, translated_text)

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
            result = self._parse_proofread_response(result_text)

            # Document issues found
            if self.doc_tracker and result.get('issues'):
                for issue in result['issues']:
                    self.doc_tracker.record_interpretation(
                        segment_id=original_segment.id,
                        original_text=issue.get('original', ''),
                        translated_text=issue.get('translated', ''),
                        interpretation_type='proofreading_correction',
                        reason=issue.get('issue_type', '') + ': ' + issue.get('description', ''),
                        alternative_options=[issue.get('suggestion', '')],
                        confidence=issue.get('severity', 0.5),
                        agent='ProofreadingAgent'
                    )

            logger.success(f"Completed proofreading of {original_segment.id}")
            return result

        except Exception as e:
            logger.error(f"Proofreading failed for {original_segment.id}: {e}")
            raise

    def _build_system_prompt(self, target_age: str) -> str:
        """Build the system prompt for proofreading.

        Args:
            target_age: Target age range

        Returns:
            System prompt string
        """
        return f"""You are an expert proofreader specializing in Dutch translations of classical literature for students aged {target_age}.

Your task is to verify translations from Plutarch's Lives, checking for:

1. **Accuracy**: Ensure no information is lost or distorted
2. **Completeness**: Verify all content is translated
3. **Language Quality**: Check Dutch grammar, spelling, and style
4. **Age Appropriateness**: Confirm language is suitable for {target_age} year olds
5. **Clarity**: Ensure the text is clear and understandable
6. **Consistency**: Check for consistent terminology and style

IMPORTANT CHECKS:
- All names, places, and dates are correctly preserved
- No historical facts are changed or omitted
- Dutch grammar and spelling are correct
- Sentence structure is clear and appropriate
- No unnecessary simplification that loses meaning
- Cultural references are appropriately handled
- Tone and style are consistent

Your output should be structured as:

## Overall Assessment
- Quality Score: [0-10]
- Completeness: [complete/incomplete]
- Summary: [Brief assessment]

## Issues Found
[List any issues, for each provide:]
- Issue Type: [accuracy/grammar/clarity/consistency/other]
- Severity: [high/medium/low]
- Location: [excerpt from text]
- Description: [What's wrong]
- Suggestion: [How to fix]

## Approved Translation
[If quality score >= 8, provide "APPROVED" and optionally minor edits]
[If quality score < 8, provide corrected version]
"""

    def _build_proofread_prompt(
        self,
        original_segment: TextSegment,
        translated_text: str
    ) -> str:
        """Build the proofreading prompt.

        Args:
            original_segment: Original text segment
            translated_text: Translated text

        Returns:
            User prompt string
        """
        return f"""Please proofread this Dutch translation of a segment from Plutarch's Lives.

**Segment**: {original_segment.title}

**Original English Text**:
{original_segment.content}

---

**Dutch Translation**:
{translated_text}

---

Please verify:
1. All information from the original is present
2. Translation is accurate and faithful to the original
3. Dutch language quality (grammar, spelling, style)
4. Appropriateness for 14-16 year old students
5. Clarity and readability

Provide your assessment using the structure specified in the system prompt.
"""

    def _parse_proofread_response(self, response: str) -> Dict[str, Any]:
        """Parse the proofreading response.

        Args:
            response: Raw response from the model

        Returns:
            Parsed result dictionary
        """
        result = {
            'quality_score': 0,
            'completeness': 'unknown',
            'summary': '',
            'issues': [],
            'approved': False,
            'corrected_translation': None
        }

        sections = response.split('##')

        for section in sections:
            section = section.strip()
            if not section:
                continue

            if section.lower().startswith('overall assessment'):
                result.update(self._parse_assessment(section))

            elif section.lower().startswith('issues found'):
                result['issues'] = self._parse_issues(section)

            elif section.lower().startswith('approved translation'):
                content = section.split('\n', 1)[1].strip() if '\n' in section else ''
                if 'APPROVED' in content.upper():
                    result['approved'] = True
                else:
                    result['corrected_translation'] = content

        # Auto-approve if quality score is high and no major issues
        if result['quality_score'] >= 8 and not any(
            issue.get('severity') == 'high' for issue in result['issues']
        ):
            result['approved'] = True

        return result

    def _parse_assessment(self, assessment_text: str) -> Dict[str, Any]:
        """Parse the overall assessment section.

        Args:
            assessment_text: Assessment text

        Returns:
            Dictionary with assessment data
        """
        data = {}

        for line in assessment_text.split('\n'):
            line = line.strip()

            if 'Quality Score:' in line:
                try:
                    score = line.split(':', 1)[1].strip()
                    # Handle formats like "8/10" or "8"
                    if '/' in score:
                        score = score.split('/')[0]
                    data['quality_score'] = int(score)
                except (ValueError, IndexError):
                    pass

            elif 'Completeness:' in line:
                comp = line.split(':', 1)[1].strip().lower()
                data['completeness'] = comp

            elif 'Summary:' in line:
                data['summary'] = line.split(':', 1)[1].strip()

        return data

    def _parse_issues(self, issues_text: str) -> list:
        """Parse issues from text.

        Args:
            issues_text: Text containing issues

        Returns:
            List of parsed issues
        """
        issues = []
        current_issue = {}

        for line in issues_text.split('\n'):
            line = line.strip()
            if not line:
                if current_issue:
                    issues.append(current_issue)
                    current_issue = {}
                continue

            if line.startswith('- Issue Type:'):
                current_issue['issue_type'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Severity:'):
                severity = line.split(':', 1)[1].strip().lower()
                current_issue['severity'] = severity
                # Convert to numeric for documentation
                severity_map = {'high': 0.9, 'medium': 0.6, 'low': 0.3}
                current_issue['severity_score'] = severity_map.get(severity, 0.5)
            elif line.startswith('- Location:'):
                current_issue['location'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Description:'):
                current_issue['description'] = line.split(':', 1)[1].strip()
            elif line.startswith('- Suggestion:'):
                current_issue['suggestion'] = line.split(':', 1)[1].strip()

        if current_issue:
            issues.append(current_issue)

        return issues
