# Gutenberg Dutch Ebook Creator

An advanced AI-powered system for translating Project Gutenberg books to simplified Dutch with contextual enrichment. This project specifically focuses on Plutarch's Lives, creating accessible Dutch translations for students aged 14-16.

## Features

### 🤖 Multi-Agent Architecture

- **Translation Agent**: Translates classical English to simplified Dutch while preserving historical accuracy
- **Proofreading Agent**: Verifies translation quality, completeness, and linguistic correctness
- **Cross-Reference Agent**: Compares multiple Gutenberg editions to ensure accuracy
- **Wikipedia Enricher**: Adds contextual information for historical concepts and figures

### 📚 Comprehensive Processing

- Downloads books from Project Gutenberg automatically
- Segments text into logical chapters/lives
- Translates with age-appropriate language simplification
- Cross-checks against multiple source editions
- Enriches with Wikipedia contextual information
- Generates beautiful, styled EPUB files

### 📝 Documentation & Transparency

- Tracks all interpretation decisions
- Documents translation choices and reasoning
- Records cross-reference findings
- Generates human-readable reports
- Maintains full audit trail

## Project Structure

```
gutenberg-dutch-ebook/
├── agents/                  # AI agents for processing
│   ├── translator.py       # Translation + simplification
│   ├── proofreader.py      # Quality verification
│   ├── cross_checker.py    # Edition comparison
│   └── enricher.py         # Wikipedia integration
├── core/                   # Core functionality
│   ├── downloader.py       # Gutenberg downloader
│   ├── parser.py           # Text segmentation
│   ├── epub_generator.py   # EPUB creation
│   └── documentation.py    # Decision tracking
├── config/                 # Configuration
│   └── settings.py         # Central settings
├── data/                   # Data storage
│   ├── source/            # Downloaded books
│   ├── processed/         # Processed segments
│   ├── translated/        # Translations
│   └── documentation/     # Interpretation logs
├── output/                # Generated EPUBs
├── main.py                # Main orchestrator
└── requirements.txt       # Dependencies
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Anthropic API key (for Claude AI)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Gutenburg-creator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Configuration

Edit `.env` file to configure:

```bash
# API Keys
ANTHROPIC_API_KEY=your_key_here

# Source and target settings
SOURCE_LANGUAGE=en
TARGET_LANGUAGE=nl
TARGET_AGE_RANGE=14-16

# Book selection
GUTENBERG_BOOK_ID=674  # Plutarch's Lives

# Cross-checking editions
CROSS_CHECK_EDITIONS=14033,14034,14035,44315

# AI model settings
TRANSLATION_MODEL=claude-sonnet-4-5-20250929
TEMPERATURE=0.3

# Output settings
EPUB_TITLE=Plutarchus - Levens van Beroemde Grieken en Romeinen
EPUB_AUTHOR=Plutarchus
```

## Usage

### Basic Usage

Run the complete pipeline:

```bash
python main.py
```

This will:
1. Download Plutarch's Lives from Project Gutenberg
2. Download comparison editions for cross-checking
3. Parse the text into segments (individual lives)
4. Translate each segment to Dutch
5. Proofread and verify translations
6. Cross-check against other editions
7. Enrich with Wikipedia information
8. Generate a beautiful EPUB file
9. Save documentation of all decisions

### Testing with Limited Segments

For testing, the main.py is configured to process only 5 segments by default. To process the entire book, edit `main.py` and remove the `max_segments` parameter:

```python
output_file = creator.run(
    cross_check=True,
    enrich=True,
    # max_segments=5  # Remove or comment this line
)
```

### Advanced Usage

You can customize the pipeline programmatically:

```python
from main import GutenbergDutchEbookCreator

creator = GutenbergDutchEbookCreator()

# Process specific book
output_file = creator.run(
    book_id=674,
    cross_check=True,   # Enable cross-checking
    enrich=True,        # Enable Wikipedia enrichment
    max_segments=None   # Process all segments
)
```

## Agent Details

### Translation Agent

The translation agent uses Claude to:
- Translate English to Dutch
- Simplify language for 14-16 year olds
- Preserve historical accuracy
- Document translation choices
- Explain cultural adaptations

### Proofreading Agent

The proofreading agent:
- Verifies completeness (no lost information)
- Checks Dutch grammar and spelling
- Assesses age-appropriateness
- Provides quality scores (0-10)
- Suggests corrections when needed

### Cross-Reference Agent

The cross-reference agent:
- Compares multiple English editions
- Identifies factual discrepancies
- Assesses source reliability
- Recommends translation adjustments
- Documents differences found

### Wikipedia Enricher

The Wikipedia enricher:
- Identifies key historical concepts
- Fetches Dutch Wikipedia summaries
- Creates contextual footnotes
- Generates comprehensive glossary
- Links to source materials

## Output Files

### EPUB File

Location: `output/plutarch_lives_nl_674.epub`

Features:
- Beautiful typography and styling
- Contextual footnotes
- Comprehensive glossary
- Proper navigation and table of contents
- E-reader optimized formatting

### Documentation

Location: `data/documentation/`

Files:
- `interpretations.json`: All translation decisions
- `cross_references.json`: Cross-check findings
- `translation_report.md`: Human-readable summary

## Documentation System

All translation decisions are tracked and documented:

### Interpretation Records

Each significant translation choice is recorded with:
- Original text excerpt
- Translated text
- Interpretation type (translation_choice, simplification, etc.)
- Reasoning and explanation
- Alternative options considered
- Confidence score
- Agent responsible

### Cross-Reference Records

Each cross-check includes:
- Editions compared
- Differences identified
- Resolution chosen
- Confidence level

### Reports

Human-readable markdown reports include:
- Summary statistics
- Interpretation examples
- Cross-reference findings
- Quality assessments

## Technical Details

### AI Model

Uses Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) for:
- High-quality translation
- Nuanced understanding
- Historical context awareness
- Consistency across segments

### Translation Process

1. **Segmentation**: Text divided into manageable chunks
2. **Translation**: English → Simplified Dutch
3. **Verification**: Quality and completeness check
4. **Cross-check**: Compare with other editions
5. **Enrichment**: Add Wikipedia context
6. **Generation**: Create styled EPUB

### Quality Assurance

Multiple layers of quality control:
- AI-powered proofreading
- Cross-edition verification
- Completeness checking
- Style consistency
- Age-appropriateness validation

## Customization

### Add New Source Books

1. Find the Gutenberg book ID
2. Update `.env`:
```bash
GUTENBERG_BOOK_ID=your_book_id
```

3. Update EPUB metadata:
```bash
EPUB_TITLE=Your Book Title
EPUB_AUTHOR=Author Name
```

### Adjust Target Age

Modify `.env`:
```bash
TARGET_AGE_RANGE=12-14  # Or any other range
```

### Change Translation Style

Edit `agents/translator.py` to modify the system prompt and adjust:
- Simplification level
- Cultural adaptation approach
- Terminology choices

## Troubleshooting

### API Key Issues

```
Error: ANTHROPIC_API_KEY is not set
```

Solution: Ensure `.env` file exists with valid API key.

### Wikipedia API Issues

If Wikipedia enrichment fails, the system will continue without it. Check:
- Internet connection
- Wikipedia API availability
- Language code (should be 'nl' for Dutch)

### Memory Issues

For large books, you may need to:
- Increase available RAM
- Process in batches using `max_segments`
- Reduce `MAX_CHUNK_SIZE` in settings

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Agents

1. Create agent file in `agents/`
2. Inherit base patterns from existing agents
3. Integrate into `main.py` pipeline
4. Update documentation

### Contributing

Contributions welcome! Please:
- Follow existing code style
- Add tests for new features
- Update documentation
- Use descriptive commit messages

## License

See LICENSE file for details.

## Acknowledgments

- **Project Gutenberg**: Source texts
- **Anthropic**: Claude AI model
- **Wikipedia**: Contextual information
- **Plutarch**: Original author of these timeless biographies

## Citation

If you use this project in academic work:

```
Gutenberg Dutch Ebook Creator (2025)
AI-powered translation system for classical literature
https://github.com/your-repo/gutenberg-dutch-ebook
```

## Future Enhancements

Planned features:
- [ ] Support for more languages
- [ ] Interactive EPUB with quizzes
- [ ] Audio narration generation
- [ ] Difficulty level adjustment
- [ ] Teacher's guide generation
- [ ] Student comprehension questions
- [ ] Parallel text view (EN/NL)
- [ ] Historical timeline integration

## Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Note**: This is an AI-assisted translation tool. While every effort is made to ensure accuracy, human review is recommended for educational or publication purposes.
