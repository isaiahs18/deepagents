# 🔍 Code Review Agent

An AI-powered code reviewer built with Deep Agents. Point it at any file or directory and it produces a structured review covering bugs, security, performance, readability, error handling, and testing — along with concrete fixes.

This is one practical answer to the question: *how can you use Deep Agents to become a better programmer and produce more solid work?*

## Quickstart

**Prerequisites**: Install [uv](https://docs.astral.sh/uv/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Change into the example directory:

```bash
cd examples/code-review-agent
```

Install dependencies:

```bash
uv sync
```

Set your API key:

```bash
cp .env.example .env
# Edit .env and fill in your ANTHROPIC_API_KEY
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

Review a single file:

```bash
uv run python agent.py path/to/your/file.py
```

Review an entire directory:

```bash
uv run python agent.py path/to/your/project/
```

Narrow the focus to a specific dimension:

```bash
# Security audit
uv run python agent.py src/ --focus security

# Performance review
uv run python agent.py app.py --focus performance

# Test coverage and quality
uv run python agent.py lib/ --focus testing
```

Use a different model:

```bash
uv run python agent.py src/ --model openai:gpt-5
```

## What the Agent Reviews

| Dimension | What It Looks For |
|-----------|-------------------|
| **Correctness & Bugs** | Logic errors, off-by-one errors, unhandled edge cases |
| **Security** | Injection risks, insecure defaults, missing input validation |
| **Performance** | Unnecessary allocations, inefficient algorithms, N+1 queries |
| **Readability** | Confusing naming, overly complex logic, unclear intent |
| **Error Handling** | Swallowed exceptions, missing cleanup, broad `except` clauses |
| **Testing** | Missing coverage, untestable designs, logic-duplicating tests |

## Output

The agent writes a Markdown review to `code_review.md` in the target directory. The review includes:

- **Summary** — overall quality and key themes
- **Critical Issues** — bugs, security vulnerabilities, data-loss risks (with corrected code)
- **Improvements** — non-critical but valuable changes
- **Positive Observations** — what the code does well
- **Next Steps** — prioritized, actionable recommendations

## Example Review (excerpt)

```markdown
## Summary

The authentication module is functional but has two critical security issues
that must be addressed before production use, alongside several opportunities
to improve readability and test coverage.

## Critical Issues

### 1. SQL Injection in `get_user` (auth.py:42)

**Problem**: The query is built with f-string interpolation, making it
trivially injectable.

**Fix**:
```python
# Before
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

# After
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

## Positive Observations

- Passwords are hashed with bcrypt (good choice)
- Rate limiting middleware is applied consistently
```

## Customization

The `CODE_REVIEW_SYSTEM_PROMPT` in `agent.py` defines the review persona and format. Edit it to:

- Add language-specific rules (e.g., PEP 8 for Python, Effective Go idioms)
- Enforce project conventions (e.g., "all public functions must have docstrings")
- Adjust the output format for your team's review workflow
- Restrict or expand the review dimensions

```python
from deepagents import create_deep_agent

MY_REVIEW_PROMPT = """
You review Go code for correctness, idiomatic style, and performance.
Always flag missing error returns and nil pointer dereferences first.
"""

agent = create_deep_agent(
    system_prompt=MY_REVIEW_PROMPT,
)
```

## How It Works

The Code Review Agent is a standard `create_deep_agent` with a specialized `system_prompt`. It uses the built-in `read_file`, `glob`, and `grep` tools to read your code, then writes its findings to `code_review.md` via `write_file`.

No custom tools or sub-agents are needed — the review capability comes entirely from the system prompt and the model's understanding of your code.
