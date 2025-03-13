# Contributing to TelegramPy

Thank you for considering contributing to TelegramPy! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the [Issues](https://github.com/l1v0n1/telegrampy/issues).
- If not, create a new issue with a clear title and description.
- Include steps to reproduce the bug, expected behavior, and actual behavior.
- Include code samples, error messages, and screenshots if applicable.

### Suggesting Features

- Check if the feature has already been suggested in the [Issues](https://github.com/l1v0n1/telegrampy/issues).
- If not, create a new issue with a clear title and description.
- Explain why this feature would be useful to most users.
- Provide examples of how the feature would work.

### Pull Requests

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes.
4. Run tests to ensure your changes don't break existing functionality.
5. Submit a pull request.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/l1v0n1/telegrampy.git
   cd telegrampy
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

3. Run tests:
   ```bash
   pytest
   ```

## Coding Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
- Write docstrings for all functions, classes, and methods.
- Include type hints where appropriate.
- Write tests for new features.
- Keep functions and methods small and focused.
- Use descriptive variable names.

## Git Workflow

1. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message here"
   ```

3. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a pull request from your fork to the main repository.

## Documentation

- Update documentation for any changes you make.
- Document new features, options, and behaviors.
- Keep the README.md up to date.

## License

By contributing to TelegramPy, you agree that your contributions will be licensed under the project's MIT License. 