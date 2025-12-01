"""Module for tracking translation decisions and interpretations."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from loguru import logger


@dataclass
class InterpretationRecord:
    """Record of a translation interpretation decision."""

    segment_id: str
    timestamp: str
    original_text: str
    translated_text: str
    interpretation_type: str  # 'translation_choice', 'simplification', 'cultural_adaptation'
    reason: str
    alternative_options: Optional[List[str]] = None
    confidence: Optional[float] = None
    agent: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class CrossReferenceNote:
    """Record of cross-reference checking with other editions."""

    segment_id: str
    timestamp: str
    source_edition: int
    comparison_editions: List[int]
    differences_found: List[str]
    resolution: str
    confidence: float

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class DocumentationTracker:
    """Tracks and documents translation decisions and interpretations."""

    def __init__(self, output_dir: Path):
        """Initialize the documentation tracker.

        Args:
            output_dir: Directory to save documentation
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.interpretations: List[InterpretationRecord] = []
        self.cross_references: List[CrossReferenceNote] = []

        # Load existing documentation if available
        self._load_existing()

    def record_interpretation(
        self,
        segment_id: str,
        original_text: str,
        translated_text: str,
        interpretation_type: str,
        reason: str,
        alternative_options: Optional[List[str]] = None,
        confidence: Optional[float] = None,
        agent: Optional[str] = None
    ) -> None:
        """Record a translation interpretation decision.

        Args:
            segment_id: ID of the text segment
            original_text: Original text snippet
            translated_text: Translated text
            interpretation_type: Type of interpretation
            reason: Explanation of the decision
            alternative_options: Other options considered
            confidence: Confidence score (0-1)
            agent: Name of the agent making the decision
        """
        record = InterpretationRecord(
            segment_id=segment_id,
            timestamp=datetime.now().isoformat(),
            original_text=original_text[:500],  # Limit length
            translated_text=translated_text[:500],
            interpretation_type=interpretation_type,
            reason=reason,
            alternative_options=alternative_options,
            confidence=confidence,
            agent=agent
        )

        self.interpretations.append(record)
        logger.debug(f"Recorded interpretation for {segment_id}")

    def record_cross_reference(
        self,
        segment_id: str,
        source_edition: int,
        comparison_editions: List[int],
        differences_found: List[str],
        resolution: str,
        confidence: float
    ) -> None:
        """Record a cross-reference check.

        Args:
            segment_id: ID of the text segment
            source_edition: Main edition being translated
            comparison_editions: Editions compared against
            differences_found: List of differences found
            resolution: How differences were resolved
            confidence: Confidence in the resolution
        """
        record = CrossReferenceNote(
            segment_id=segment_id,
            timestamp=datetime.now().isoformat(),
            source_edition=source_edition,
            comparison_editions=comparison_editions,
            differences_found=differences_found,
            resolution=resolution,
            confidence=confidence
        )

        self.cross_references.append(record)
        logger.debug(f"Recorded cross-reference for {segment_id}")

    def save(self) -> None:
        """Save all documentation to files."""
        # Save interpretations
        interpretations_file = self.output_dir / "interpretations.json"
        with open(interpretations_file, 'w', encoding='utf-8') as f:
            json.dump(
                [record.to_dict() for record in self.interpretations],
                f,
                indent=2,
                ensure_ascii=False
            )

        # Save cross-references
        cross_ref_file = self.output_dir / "cross_references.json"
        with open(cross_ref_file, 'w', encoding='utf-8') as f:
            json.dump(
                [record.to_dict() for record in self.cross_references],
                f,
                indent=2,
                ensure_ascii=False
            )

        # Generate human-readable report
        self._generate_report()

        logger.success(f"Saved documentation to {self.output_dir}")

    def _generate_report(self) -> None:
        """Generate a human-readable markdown report."""
        report_file = self.output_dir / "translation_report.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Translation Documentation Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Interpretation summary
            f.write("## Translation Interpretations\n\n")
            f.write(f"Total interpretations recorded: {len(self.interpretations)}\n\n")

            # Group by type
            by_type: Dict[str, List[InterpretationRecord]] = {}
            for record in self.interpretations:
                if record.interpretation_type not in by_type:
                    by_type[record.interpretation_type] = []
                by_type[record.interpretation_type].append(record)

            for interp_type, records in by_type.items():
                f.write(f"### {interp_type.replace('_', ' ').title()}\n\n")
                f.write(f"Count: {len(records)}\n\n")

                for record in records[:10]:  # Show first 10
                    f.write(f"**Segment**: {record.segment_id}\n\n")
                    f.write(f"**Original**: {record.original_text}\n\n")
                    f.write(f"**Translated**: {record.translated_text}\n\n")
                    f.write(f"**Reason**: {record.reason}\n\n")
                    if record.confidence:
                        f.write(f"**Confidence**: {record.confidence:.2f}\n\n")
                    f.write("---\n\n")

            # Cross-reference summary
            f.write("## Cross-Reference Checks\n\n")
            f.write(f"Total cross-references: {len(self.cross_references)}\n\n")

            for record in self.cross_references[:20]:  # Show first 20
                f.write(f"**Segment**: {record.segment_id}\n\n")
                f.write(f"**Editions compared**: {record.comparison_editions}\n\n")
                f.write(f"**Differences**: {len(record.differences_found)}\n\n")
                if record.differences_found:
                    for diff in record.differences_found[:5]:
                        f.write(f"- {diff}\n")
                    f.write("\n")
                f.write(f"**Resolution**: {record.resolution}\n\n")
                f.write(f"**Confidence**: {record.confidence:.2f}\n\n")
                f.write("---\n\n")

        logger.info(f"Generated report: {report_file}")

    def _load_existing(self) -> None:
        """Load existing documentation if available."""
        interpretations_file = self.output_dir / "interpretations.json"
        if interpretations_file.exists():
            with open(interpretations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.interpretations = [
                    InterpretationRecord(**record) for record in data
                ]
            logger.info(f"Loaded {len(self.interpretations)} existing interpretations")

        cross_ref_file = self.output_dir / "cross_references.json"
        if cross_ref_file.exists():
            with open(cross_ref_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cross_references = [
                    CrossReferenceNote(**record) for record in data
                ]
            logger.info(f"Loaded {len(self.cross_references)} existing cross-references")

    def get_statistics(self) -> Dict:
        """Get documentation statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            'total_interpretations': len(self.interpretations),
            'total_cross_references': len(self.cross_references),
            'interpretations_by_type': {
                interp_type: len([
                    r for r in self.interpretations
                    if r.interpretation_type == interp_type
                ])
                for interp_type in set(r.interpretation_type for r in self.interpretations)
            },
            'average_confidence': sum(
                r.confidence for r in self.interpretations if r.confidence
            ) / len([r for r in self.interpretations if r.confidence])
            if any(r.confidence for r in self.interpretations) else 0
        }
