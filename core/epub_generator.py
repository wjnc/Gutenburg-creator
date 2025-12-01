"""Module for generating beautiful EPUB files."""

from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from ebooklib import epub
from loguru import logger

from core.parser import TextSegment


class EPUBGenerator:
    """Generates EPUB files from translated segments."""

    def __init__(
        self,
        title: str,
        author: str,
        language: str = "nl",
        translator: str = "AI Translation"
    ):
        """Initialize the EPUB generator.

        Args:
            title: Book title
            author: Book author
            language: Book language code
            translator: Translator name
        """
        self.title = title
        self.author = author
        self.language = language
        self.translator = translator

        self.book = epub.EpubBook()
        self.chapters: List[epub.EpubHtml] = []
        self.toc: List[Any] = []

    def create_book(
        self,
        segments: List[Dict[str, Any]],
        glossary: Optional[str] = None,
        preface: Optional[str] = None
    ) -> epub.EpubBook:
        """Create EPUB book from segments.

        Args:
            segments: List of segment dictionaries with translated text
            glossary: Optional glossary text
            preface: Optional preface text

        Returns:
            EpubBook instance
        """
        logger.info(f"Creating EPUB: {self.title}")

        # Set metadata
        self._set_metadata()

        # Add CSS styling
        self._add_stylesheet()

        # Add cover (optional)
        # self._add_cover()

        # Add preface if provided
        if preface:
            self._add_preface(preface)

        # Add translated chapters
        for segment in segments:
            self._add_chapter(segment)

        # Add glossary if provided
        if glossary:
            self._add_glossary(glossary)

        # Add navigation
        self._add_navigation()

        logger.success(f"Created EPUB with {len(self.chapters)} chapters")
        return self.book

    def save(self, output_path: Path) -> Path:
        """Save the EPUB file.

        Args:
            output_path: Path to save the EPUB

        Returns:
            Path to saved file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        epub.write_epub(str(output_path), self.book)
        logger.success(f"Saved EPUB to: {output_path}")

        return output_path

    def _set_metadata(self) -> None:
        """Set book metadata."""
        self.book.set_identifier(str(uuid.uuid4()))
        self.book.set_title(self.title)
        self.book.set_language(self.language)

        self.book.add_author(self.author)
        self.book.add_metadata('DC', 'contributor', self.translator, {'role': 'translator'})
        self.book.add_metadata('DC', 'publisher', 'Gutenberg Dutch Ebook Creator')
        self.book.add_metadata('DC', 'date', datetime.now().strftime('%Y-%m-%d'))
        self.book.add_metadata('DC', 'description',
            'Nederlandse vertaling van Plutarchus\' Levens, vereenvoudigd voor jongeren van 14-16 jaar.')

    def _add_stylesheet(self) -> None:
        """Add CSS stylesheet for beautiful formatting."""
        css = '''
@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: Georgia, serif;
    line-height: 1.6;
    margin: 1em;
    color: #333;
}

h1 {
    font-size: 2em;
    color: #8B4513;
    text-align: center;
    margin-top: 2em;
    margin-bottom: 1em;
    border-bottom: 2px solid #D2691E;
    padding-bottom: 0.5em;
}

h2 {
    font-size: 1.5em;
    color: #A0522D;
    margin-top: 1.5em;
    margin-bottom: 0.75em;
}

h3 {
    font-size: 1.2em;
    color: #8B4513;
    margin-top: 1em;
    margin-bottom: 0.5em;
}

p {
    text-align: justify;
    margin-bottom: 1em;
    text-indent: 1.5em;
}

p.first {
    text-indent: 0;
}

.footnote {
    font-size: 0.9em;
    color: #666;
    border-left: 3px solid #D2691E;
    padding-left: 1em;
    margin: 1em 0;
    background-color: #FFF8DC;
}

.footnote-ref {
    font-size: 0.8em;
    vertical-align: super;
    color: #8B4513;
}

.glossary-entry {
    margin-bottom: 1.5em;
}

.glossary-term {
    font-weight: bold;
    color: #8B4513;
}

.preface {
    font-style: italic;
    color: #555;
}

.chapter-header {
    text-align: center;
    margin: 2em 0;
}

.wiki-link {
    color: #4169E1;
    text-decoration: none;
    border-bottom: 1px dotted #4169E1;
}

blockquote {
    margin: 1.5em 2em;
    padding: 1em;
    background-color: #F5F5DC;
    border-left: 4px solid #8B4513;
    font-style: italic;
}

/* For better readability on e-readers */
@media amzn-kf8 {
    body {
        line-height: 1.4;
    }
}

@media amzn-mobi {
    body {
        line-height: 1.4;
    }
}
'''

        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=css
        )

        self.book.add_item(nav_css)
        self.style = nav_css

    def _add_preface(self, preface_text: str) -> None:
        """Add preface chapter.

        Args:
            preface_text: Preface text
        """
        content = f'''
<html>
<head>
    <link rel="stylesheet" href="style/nav.css" type="text/css"/>
</head>
<body>
    <div class="preface">
        <h1>Voorwoord</h1>
        {self._format_text(preface_text)}
    </div>
</body>
</html>
'''

        preface = epub.EpubHtml(
            title='Voorwoord',
            file_name='preface.xhtml',
            lang=self.language
        )
        preface.content = content

        self.book.add_item(preface)
        self.chapters.append(preface)
        self.toc.append(epub.Link('preface.xhtml', 'Voorwoord', 'preface'))

    def _add_chapter(self, segment_data: Dict[str, Any]) -> None:
        """Add a chapter from a segment.

        Args:
            segment_data: Segment data dictionary
        """
        segment_id = segment_data.get('id', f'chapter_{len(self.chapters)}')
        title = segment_data.get('title', 'Untitled')
        translated_text = segment_data.get('translated_text', '')
        footnotes = segment_data.get('footnotes', [])

        # Create chapter content
        content = f'''
<html>
<head>
    <link rel="stylesheet" href="style/nav.css" type="text/css"/>
</head>
<body>
    <div class="chapter">
        <div class="chapter-header">
            <h1>{title}</h1>
        </div>
        {self._format_text(translated_text)}
'''

        # Add footnotes if present
        if footnotes:
            content += '\n<hr/>\n<div class="footnotes">\n<h3>Toelichtingen</h3>\n'
            for footnote in footnotes:
                num = footnote.get('number', '')
                concept = footnote.get('concept', '')
                text = footnote.get('text', '')
                source = footnote.get('source', '')

                content += f'''
<div class="footnote" id="fn{num}">
    <p><span class="footnote-ref">[{num}]</span> <strong>{concept}</strong>: {text}</p>
    <p><em>Bron: {source}</em></p>
</div>
'''
            content += '</div>\n'

        content += '''
    </div>
</body>
</html>
'''

        # Create chapter
        file_name = f'chapter_{segment_id}.xhtml'
        chapter = epub.EpubHtml(
            title=title,
            file_name=file_name,
            lang=self.language
        )
        chapter.content = content

        self.book.add_item(chapter)
        self.chapters.append(chapter)
        self.toc.append(epub.Link(file_name, title, segment_id))

    def _add_glossary(self, glossary_text: str) -> None:
        """Add glossary chapter.

        Args:
            glossary_text: Glossary markdown text
        """
        # Convert markdown to HTML (simple conversion)
        html_content = self._markdown_to_html(glossary_text)

        content = f'''
<html>
<head>
    <link rel="stylesheet" href="style/nav.css" type="text/css"/>
</head>
<body>
    <div class="glossary">
        {html_content}
    </div>
</body>
</html>
'''

        glossary = epub.EpubHtml(
            title='Begrippenlijst',
            file_name='glossary.xhtml',
            lang=self.language
        )
        glossary.content = content

        self.book.add_item(glossary)
        self.chapters.append(glossary)
        self.toc.append(epub.Link('glossary.xhtml', 'Begrippenlijst', 'glossary'))

    def _add_navigation(self) -> None:
        """Add table of contents and navigation."""
        self.book.toc = tuple(self.toc)

        # Add navigation files
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # Define spine (reading order)
        self.book.spine = ['nav'] + self.chapters

    def _format_text(self, text: str) -> str:
        """Format plain text as HTML paragraphs.

        Args:
            text: Plain text

        Returns:
            HTML formatted text
        """
        paragraphs = text.split('\n\n')
        html = []

        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue

            # Clean up the paragraph
            para = para.replace('\n', ' ')
            para = para.replace('  ', ' ')

            # First paragraph has no indent
            if i == 0:
                html.append(f'<p class="first">{para}</p>')
            else:
                html.append(f'<p>{para}</p>')

        return '\n'.join(html)

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Simple markdown to HTML conversion.

        Args:
            markdown_text: Markdown text

        Returns:
            HTML text
        """
        html = []
        lines = markdown_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Headers
            if line.startswith('# '):
                html.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                html.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                html.append(f'<h3>{line[4:]}</h3>')
            # Bold
            elif '**' in line:
                # Simple bold replacement
                parts = line.split('**')
                formatted = ''
                for i, part in enumerate(parts):
                    if i % 2 == 1:
                        formatted += f'<strong>{part}</strong>'
                    else:
                        formatted += part
                html.append(f'<p class="glossary-entry">{formatted}</p>')
            else:
                html.append(f'<p>{line}</p>')

        return '\n'.join(html)
