# Contributing to Gutenberg Dutch Ebook Creator

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the best outcome for the project
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Enhancements

1. Check if the enhancement has been suggested
2. Create a new issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Why this would be useful
   - Any alternatives you've considered

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Write or update tests
5. Update documentation
6. Commit your changes with clear messages
7. Push to your fork
8. Submit a pull request

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/your-username/gutenberg-dutch-ebook.git
cd gutenberg-dutch-ebook
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8 mypy
```

4. Set up pre-commit hooks (optional but recommended):
```bash
pip install pre-commit
pre-commit install
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Keep functions focused and small
- Use meaningful variable names

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update comments for complex logic
- Include examples where helpful

### Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Use descriptive test names

### Commit Messages

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: Add support for German translations

- Implement German language processing
- Add German Wikipedia integration
- Update configuration for DE language

Closes #123
```

## Project Structure

When adding new features:

### Adding a New Agent

1. Create file in `agents/` directory
2. Follow existing agent patterns
3. Implement required methods
4. Add to `agents/__init__.py`
5. Integrate into main pipeline
6. Add tests
7. Update documentation

### Adding Core Functionality

1. Create file in `core/` directory
2. Follow module design patterns
3. Add to `core/__init__.py`
4. Write comprehensive tests
5. Update documentation

### Adding Configuration Options

1. Add to `.env.example`
2. Update `config/settings.py`
3. Document in README.md
4. Add validation if needed

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html tests/
```

Run specific test:
```bash
pytest tests/test_parser.py::test_slugify
```

## Documentation

Build documentation (if using Sphinx):
```bash
cd docs
make html
```

## Code Review Process

1. All submissions require review
2. Reviewers will check:
   - Code quality and style
   - Test coverage
   - Documentation
   - Performance implications
   - Security considerations

3. Address review comments
4. Get approval from maintainer
5. Squash commits if requested
6. Merge!

## Getting Help

- Open an issue for questions
- Join discussions
- Check existing documentation
- Review similar implementations

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing!
