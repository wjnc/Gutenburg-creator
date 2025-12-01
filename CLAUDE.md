# CLAUDE.md - AI Assistant Guide for Gutenburg-creator

## Project Overview

**Gutenburg-creator** is an open-source project (GPL-3.0) that appears to be in its initial development phase. The name suggests functionality related to creating or managing content, potentially inspired by Project Gutenberg.

**Repository**: wjnc/Gutenburg-creator
**License**: GNU General Public License v3.0
**Current Status**: Initial development phase

## Current Repository State

As of the last analysis, this repository contains:

```
Gutenburg-creator/
├── .git/                # Git version control
├── LICENSE              # GPL-3.0 license
└── README.md            # Project title only
```

### Key Observations

- **Fresh repository**: Only contains initial commit
- **No codebase yet**: No source code, dependencies, or build configuration
- **Minimal documentation**: README contains only project title
- **No tech stack defined**: Programming language and frameworks not yet established

## Development Guidelines for AI Assistants

### 1. Project Setup and Structure

When setting up the initial codebase, consider establishing:

#### Recommended Directory Structure

```
Gutenburg-creator/
├── .github/             # GitHub workflows, issue templates
├── docs/                # Additional documentation
├── src/                 # Source code
│   ├── core/           # Core functionality
│   ├── utils/          # Utility functions
│   └── tests/          # Test files
├── examples/            # Usage examples
├── .gitignore          # Git ignore patterns
├── README.md           # Project documentation
├── CLAUDE.md           # This file
├── CONTRIBUTING.md     # Contribution guidelines
└── [build config]      # package.json, requirements.txt, Cargo.toml, etc.
```

#### Technology Stack Considerations

**Before adding dependencies or choosing a tech stack**, consult with the user about:

- Primary programming language (Python, JavaScript/TypeScript, Rust, Go, etc.)
- Target use case (CLI tool, web app, library, desktop app)
- Deployment environment (local, cloud, containerized)
- Key requirements (performance, portability, ease of use)

### 2. Git Workflow

#### Branch Strategy

- **Feature branches**: Create descriptive feature branches from main
- **Branch naming**: Use format `claude/[feature-description]-[session-id]`
- **Current working branch**: `claude/claude-md-min0ut93b9pdbjaw-01RVqVJtPHm3sXXgHsQfiKDY`

#### Commit Practices

**DO:**
- Write clear, descriptive commit messages
- Focus on "why" rather than "what" in commit messages
- Keep commits atomic and focused on single concerns
- Follow conventional commit format when appropriate
- Stage only relevant files

**DON'T:**
- Commit sensitive information (.env files, credentials, API keys)
- Create empty commits without changes
- Use `--force` push without explicit user permission
- Skip git hooks (--no-verify) unless requested
- Amend commits from other developers

#### Commit Message Style

```
<type>: <concise description>

[optional detailed explanation]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat: Add text parsing functionality for Gutenberg format

Implemented parser that handles plain text format from Project
Gutenberg, including metadata extraction and chapter detection.
```

### 3. Code Quality Standards

#### General Principles

1. **Avoid over-engineering**: Implement only what's requested
2. **Keep it simple**: Prefer clarity over cleverness
3. **No premature optimization**: Optimize only when needed
4. **Minimal abstractions**: Don't create abstractions for single-use code
5. **Delete unused code**: Remove completely rather than commenting out

#### Security Considerations

- Validate all user input at system boundaries
- Avoid common vulnerabilities (XSS, SQL injection, command injection)
- Don't store secrets in code or version control
- Use parameterized queries for database operations
- Sanitize file paths to prevent directory traversal

#### Documentation

- Add docstrings/comments only where logic isn't self-evident
- Keep README up-to-date with setup and usage instructions
- Document breaking changes and migration paths
- Include examples for public APIs

### 4. Testing Strategy

When tests are implemented:

- Write tests for public APIs and critical paths
- Focus on behavior, not implementation details
- Keep tests simple and maintainable
- Use descriptive test names that explain intent
- Mock external dependencies appropriately

### 5. File Operations Best Practices

#### Reading Files

- Use `Read` tool for reading specific files (not `cat`)
- Use `Glob` tool for finding files by pattern (not `find`)
- Use `Grep` tool for searching content (not `grep` command)
- Always verify file existence before operations

#### Editing Files

- **ALWAYS** read a file before editing it
- Use `Edit` tool for modifications to existing files
- Preserve indentation style (tabs vs spaces) from original
- Only use `Write` for creating new files
- Prefer editing existing files over creating new ones

#### File Creation

- **DON'T** create files proactively without user request
- Avoid creating markdown documentation unless explicitly asked
- No README files without explicit need
- Consider if editing an existing file would suffice

### 6. Communication Style

- Be concise and direct
- No emojis unless explicitly requested by user
- Use markdown for formatting
- Explain technical decisions when relevant
- Ask clarifying questions for ambiguous requirements
- Prioritize technical accuracy over validation

### 7. Task Management

Use `TodoWrite` tool for:

- Complex multi-step tasks (3+ distinct steps)
- Non-trivial implementations
- User-provided task lists
- Tracking multiple related changes

**Don't use TodoWrite for:**
- Single straightforward operations
- Trivial tasks (< 3 steps)
- Purely conversational requests

**Task state management:**
- Keep exactly ONE task `in_progress` at a time
- Mark tasks `completed` immediately after finishing
- Update status in real-time
- Remove obsolete tasks entirely

### 8. Working with Unknown Codebases

When the project structure becomes established:

1. **Explore first**: Use `Task` tool with `subagent_type=Explore` for codebase questions
2. **Search strategically**:
   - Use `Glob` for file patterns
   - Use `Grep` for content search
   - Use `Read` for specific files
3. **Understand before modifying**: Never propose changes to unread code
4. **Respect existing patterns**: Match existing code style and conventions

## Project-Specific Conventions

### Naming Conventions

(To be established based on chosen technology stack)

### Code Style

(To be established based on chosen technology stack)

### Build and Deployment

(To be documented once build system is established)

## Common Commands Reference

### Development Setup

(To be added once tech stack is chosen)

### Running Tests

(To be added once testing framework is established)

### Building

(To be added once build process is defined)

## License Compliance

This project uses **GPL-3.0**. Key implications:

- All derivative works must also be GPL-3.0
- Source code must be made available
- Changes must be documented
- No additional restrictions can be imposed
- Patent rights are explicitly granted

When adding dependencies:

- Verify license compatibility with GPL-3.0
- Document all third-party licenses
- Avoid proprietary dependencies

## Resources and References

### Project Gutenberg

If this project relates to Project Gutenberg content:

- **Website**: https://www.gutenberg.org
- **Format specs**: Plain text UTF-8, specific header/footer format
- **Catalog**: 70,000+ public domain books
- **License**: Public domain works (pre-1928 in US)

### Documentation Standards

- Keep this CLAUDE.md updated as project evolves
- Document architectural decisions
- Maintain changelog for significant changes
- Update README with setup instructions

## Troubleshooting

### Common Issues

(To be populated as issues are encountered)

### Debug Procedures

(To be documented once project structure is established)

## Future Considerations

As this project develops, consider adding:

1. **CI/CD pipeline**: Automated testing and deployment
2. **Code formatting**: Automated code style enforcement
3. **Linting**: Static analysis for code quality
4. **Documentation generation**: Auto-generated API docs
5. **Version management**: Semantic versioning strategy
6. **Release process**: Standardized release workflow
7. **Issue templates**: Structured bug reports and feature requests
8. **Contributing guide**: Instructions for external contributors

## Questions for Project Direction

Before significant development, clarify:

1. **Primary use case**: What problem does this solve?
2. **Target audience**: Who will use this?
3. **Technology preferences**: Language, frameworks, tools?
4. **Distribution method**: CLI, web app, library, service?
5. **Performance requirements**: Scale, speed, resource constraints?
6. **Integration needs**: APIs, file formats, external services?

## Updates Log

- **2025-12-01**: Initial CLAUDE.md created for fresh repository
  - Repository contains only LICENSE and minimal README
  - No codebase or tech stack established yet
  - GPL-3.0 licensed

---

**Note to AI Assistants**: This document should be updated as the project evolves. When making significant architectural decisions or adding new conventions, update this file to maintain accuracy.
