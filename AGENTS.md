# Agent Guidelines

This repository uses Python for Telegram snowball sampling scripts. Agents contributing to this repo should adhere to the following instructions:

## Code Style

- Use Python 3.10 or later.
- Follow [PEP 8](https://peps.python.org/pep-0008/) styling.
- Include type hints for function definitions and public variables.
- Limit line length to 100 characters.
- Prefer descriptive variable and function names.
- Use f-strings for string formatting.
- Document public functions and modules with concise docstrings.

## Commit Practices

- Make atomic commits with clear messages.
- Avoid amending commits pushed to the repository.

## Testing and Checks

- Run static compilation checks before committing:

```bash
python -m py_compile $(git ls-files '*.py')
```

- If additional tests or scripts are provided in the future, run them and ensure they pass.

## Repository Structure

- `main.py` orchestrates the snowball sampling process.
- `EdgeList.py` and `utils.py` provide helper functions.
- Place new modules in logically named files and update relevant imports.

## Documentation

- Keep README.md updated when adding new features or changing behaviour.
- Use Markdown headings and lists for clarity.

## Dependencies

- Declare any new Python dependencies in `requirements.txt` and pin to specific versions when possible.

Following these guidelines helps maintain code consistency and reliability across contributions.
