# Project Guidelines

## Code Security
- **CRITICAL**: Never use string concatenation or interpolation to construct SQL queries. Always use parameterized queries or an ORM.
- **CRITICAL**: Never pass unsanitized user input directly to system shells (e.g., `os.system`).
- **CRITICAL**: Do not use `pickle` for deserializing untrusted data due to RCE risks. Use `json` instead.
- **CRITICAL**: Never hardcode sensitive credentials (passwords, API keys, tokens) in source code. Use environment variables.

## Code Quality
- **ERROR HANDLING**: Do not use bare `except:` clauses. Always specify the exact Exception being caught and handle it properly.
- **RUNTIME SAFETY**: Ensure inputs are validated to prevent runtime crashes like `ZeroDivisionError`.