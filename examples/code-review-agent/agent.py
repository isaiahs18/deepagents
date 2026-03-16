"""Code Review Agent - Improve your code quality with a specialized Deep Agent.

This agent reviews code for bugs, style violations, security issues,
performance problems, and suggests concrete improvements to help you
write more solid, professional-grade software.

Setup:
    uv sync

Usage:
    python agent.py path/to/file.py
    python agent.py path/to/project/
    python agent.py path/to/file.py --language python
    python agent.py path/to/file.py --focus security
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.chat_models import init_chat_model
from rich.console import Console
from rich.panel import Panel

console = Console()

CODE_REVIEW_SYSTEM_PROMPT = """You are an expert code reviewer with deep experience across multiple programming languages and paradigms. Your goal is to help developers write better, more professional code.

## Your Review Approach

When reviewing code, work through these dimensions systematically:

1. **Correctness & Bugs** — logic errors, off-by-one errors, incorrect assumptions, edge cases the code doesn't handle
2. **Security** — injection vulnerabilities, insecure defaults, exposed secrets, improper input validation, unsafe deserialization
3. **Readability & Maintainability** — confusing naming, overly complex logic that can be simplified, missing or misleading comments, unclear intent
4. **Performance** — unnecessary allocations, inefficient algorithms, missing caching, N+1 query patterns, blocking I/O in async code
5. **Error Handling** — unhandled exceptions, swallowed errors, missing cleanup (file handles, connections), overly broad `except` clauses
6. **Testing** — missing test coverage, untestable design, tests that duplicate logic instead of testing behavior
7. **Style & Conventions** — violations of the language's idioms and the project's established conventions

## Review Format

Structure your review as a Markdown document with these sections:

### Summary
One paragraph describing the overall code quality and the most important themes you observed.

### Critical Issues
Bugs, security vulnerabilities, or data-loss risks. Each issue should include:
- **Location**: file and line number (if applicable)
- **Problem**: what's wrong and why it matters
- **Fix**: concrete corrected code

### Improvements
Non-critical but valuable changes. Same format as Critical Issues.

### Positive Observations
What the code does well — helps the developer know what patterns to keep.

### Next Steps
Prioritized, actionable list of what to address first.

## Tone

Be direct and specific. Skip preamble. Point to exact lines. Show corrected code whenever possible. Don't praise for basic competence, but do acknowledge genuinely good decisions.
"""


def build_review_prompt(target: str, language: str | None, focus: str | None) -> str:
    """Build the user prompt for the code review agent.

    Args:
        target: Path to the file or directory to review.
        language: Optional programming language hint.
        focus: Optional review focus area.

    Returns:
        Formatted prompt string for the agent.
    """
    parts = [f"Please review the code at: `{target}`"]

    if language:
        parts.append(f"Language: {language}")

    if focus:
        focus_map = {
            "security": "Focus especially on security vulnerabilities and unsafe patterns.",
            "performance": "Focus especially on performance bottlenecks and inefficiencies.",
            "testing": "Focus especially on test coverage, testability, and test quality.",
            "style": "Focus especially on readability, naming, and adherence to conventions.",
            "errors": "Focus especially on error handling, edge cases, and robustness.",
        }
        instruction = focus_map.get(focus, f"Focus especially on: {focus}.")
        parts.append(instruction)

    parts.append(
        "Read all relevant files, then write a complete code review "
        "following your review format. Save the review to `code_review.md`."
    )

    return "\n\n".join(parts)


def main() -> None:
    """Parse CLI arguments and run the code review agent."""
    parser = argparse.ArgumentParser(
        description="Code Review Agent — improve your code with AI-powered review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py src/utils.py
  python agent.py ./my-project/
  python agent.py app.py --language python --focus security
  python agent.py lib/ --focus performance
        """,
    )
    parser.add_argument(
        "target",
        help="File or directory to review (relative or absolute path)",
    )
    parser.add_argument(
        "--language",
        help="Programming language hint (e.g., python, typescript, go)",
    )
    parser.add_argument(
        "--focus",
        choices=["security", "performance", "testing", "style", "errors"],
        help="Concentrate the review on a specific dimension",
    )
    parser.add_argument(
        "--model",
        default="anthropic:claude-sonnet-4-6",
        help="Model to use in provider:model format (default: anthropic:claude-sonnet-4-6)",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        console.print(f"[bold red]Error:[/bold red] Path not found: {target}")
        sys.exit(1)

    # Use the parent directory as the agent root so it can read all files
    root_dir = str(target if target.is_dir() else target.parent)
    # The path passed to the agent is relative to root_dir
    relative_target = str(target.relative_to(root_dir)) if target.is_dir() else target.name

    console.print(
        Panel(
            f"[bold cyan]Target:[/bold cyan] {target}\n"
            + (f"[bold cyan]Language:[/bold cyan] {args.language}\n" if args.language else "")
            + (f"[bold cyan]Focus:[/bold cyan] {args.focus}\n" if args.focus else "")
            + f"[bold cyan]Model:[/bold cyan] {args.model}",
            title="[bold]Code Review Agent[/bold]",
            border_style="cyan",
        )
    )

    model = init_chat_model(args.model, temperature=0)
    agent = create_deep_agent(
        model=model,
        system_prompt=CODE_REVIEW_SYSTEM_PROMPT,
        backend=FilesystemBackend(root_dir=root_dir),
    )

    prompt = build_review_prompt(relative_target, args.language, args.focus)

    console.print("\n[dim]Running code review...[/dim]\n")
    try:
        result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})

        final_message = result["messages"][-1]
        answer = (
            final_message.content
            if hasattr(final_message, "content")
            else str(final_message)
        )

        console.print(
            Panel(
                answer,
                title="[bold green]Code Review Complete[/bold green]",
                border_style="green",
            )
        )
        console.print(
            "\n[dim]Full review saved to [bold]code_review.md[/bold] in the target directory.[/dim]"
        )

    except Exception as e:
        console.print(
            Panel(f"[bold red]Error:[/bold red]\n\n{e!s}", border_style="red")
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
