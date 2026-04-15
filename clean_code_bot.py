#!/usr/bin/env python3
"""
Clean Code Bot - CLI tool that refactors and documents code using LLM.
"""

import re
import sys
import json
import hashlib
import os
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

load_dotenv()


class SecurityValidator:
    """Input validation and sanitization to prevent prompt injection attacks."""

    DANGEROUS_PATTERNS = [
        r"__import__",
        r"exec\s*\(",
        r"eval\s*\(",
        r"file\s*:\s*/",
        r"\$\(",
        r"`.*`",
        r"&&.*rm",
        r"\|\s*sh",
        r";\s*rm",
        r">\s*/dev/",
        r"python\s+-c\s+",
    ]

    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_PATTERNS]

    def validate(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validates code for potential malicious patterns.
        Returns (is_safe, error_message).
        """
        if not code or len(code.strip()) == 0:
            return False, "Input code cannot be empty."

        if len(code) > 100000:
            return False, "Input code exceeds maximum length of 100,000 characters."

        for pattern in self.patterns:
            if pattern.search(code):
                return (
                    False,
                    f"Potentially dangerous pattern detected: {pattern.pattern}",
                )

        return True, None

    def sanitize(self, code: str) -> str:
        """Sanitizes code by removing potentially dangerous content."""
        sanitized = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
        sanitized = re.sub(r'""".*?"""', '"""""', sanitized, flags=re.DOTALL)
        sanitized = re.sub(r"'''.*?'''", "'''", sanitized, flags=re.DOTALL)
        return sanitized


class PromptEngine:
    """Chain of Thought (CoT) prompt template system."""

    SYSTEM_PROMPT = """You are an expert software engineer specializing in code refactoring and documentation.
Your task is to analyze code using Chain of Thought reasoning, then provide an optimized version.

## Analysis Process (Chain of Thought):
1. First, identify the current functionality and purpose of the code
2. Analyze current structure for violations of SOLID principles:
   - S: Single Responsibility Principle
   - O: Open/Closed Principle
   - L: Liskov Substitution Principle
   - I: Interface Segregation Principle
   - D: Dependency Inversion Principle
3. Identify code smells and areas for improvement
4. Plan refactoring approach
5. Execute refactoring with proper documentation

## Output Requirements:
- Provide comprehensive docstrings/Google-style comments
- Keep original functionality intact
- Follow language-specific best practices
- Add type hints where appropriate
- Return ONLY the refactored code, no explanations"""

    USER_PROMPT_TEMPLATE = """## Dirty Code (Input):
```{language}
{code}
```

## Refactored Code (Output):"""

    CO_ANALYSIS_TEMPLATE = """
## Chain of Thought Analysis:
### Step 1: Functionality Identification
{functionality}

### Step 2: SOLID Violations Found
{solid_violations}

### Step 3: Code Smells
{code_smells}

### Step 4: Refactoring Plan
{plan}

### Step 5: Execution
[Code has been refactored below]

---

## Refactored Code:
"""

    def build_prompt(self, code: str, language: str = "python") -> tuple[str, str]:
        """Builds the full prompt with CoT analysis request."""
        user_prompt = self.USER_PROMPT_TEMPLATE.format(language=language, code=code)
        cot_prompt = self.CO_ANALYSIS_TEMPLATE.format(
            functionality="<Analyze what the code does>",
            solid_violations="<List any SOLID principle violations>",
            code_smells="<Identify code smells>",
            plan="<Outline refactoring approach>",
        )
        return (
            self.SYSTEM_PROMPT + "\n\n" + user_prompt + "\n\n" + cot_prompt,
            user_prompt,
        )


class LLMClient:
    """Handles communication with LLM providers."""

    PROVIDERS = {
        "openai": {
            "api_key_env": "OPENAI_API_KEY",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-4o-mini",
        },
        "groq": {
            "api_key_env": "GROQ_API_KEY",
            "endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.1-70b-versatile",
        },
    }

    def __init__(self, provider: str = "groq"):
        self.provider = provider
        self.config = self.PROVIDERS.get(provider, self.PROVIDERS["groq"])
        self.api_key = os.getenv(self.config["api_key_env"])

        if not self.api_key:
            raise ValueError(
                f"API key not found. Set {self.config['api_key_env']} environment variable."
            )

    def call(self, prompt: str, temperature: float = 0.3) -> str:
        """Calls the LLM API and returns the response."""
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 8000,
        }

        try:
            response = requests.post(
                self.config["endpoint"], headers=headers, json=payload, timeout=120
            )
            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            raise TimeoutError("Request to LLM timed out.")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"API request failed: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")


class CleanCodeBot:
    """Main application class."""

    def __init__(self, provider: str = "groq"):
        self.security = SecurityValidator()
        self.prompt_engine = PromptEngine()
        self.llm = LLMClient(provider)

    def process(
        self, code: str, language: str = "python", verbose: bool = False
    ) -> str:
        """
        Process dirty code and return cleaned version.
        """
        is_safe, error = self.security.validate(code)
        if not is_safe:
            raise ValueError(f"Security validation failed: {error}")

        sanitized_code = self.security.sanitize(code)

        prompt, _ = self.prompt_engine.build_prompt(sanitized_code, language)

        if verbose:
            click.echo(f"[{click.style('DEBUG', fg='cyan')}] Sending request to LLM...")

        try:
            result = self.llm.call(prompt)
        except Exception as e:
            raise RuntimeError(f"LLM processing failed: {str(e)}")

        cleaned_code = self._extract_code(result)

        if (
            not cleaned_code
            or len(cleaned_code.strip()) < len(sanitized_code.strip()) * 0.5
        ):
            raise ValueError("Refactored code appears invalid or empty.")

        return cleaned_code

    def _extract_code(self, response: str) -> str:
        """Extracts code from markdown code blocks in response."""
        code_block_pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(code_block_pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        lines = response.split("\n")
        code_lines = []
        in_code = False

        for line in lines:
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                code_lines.append(line)

        if code_lines:
            return "\n".join(code_lines).strip()

        return response.strip()


@click.command()
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.option(
    "-o", "--output", "output_file", type=click.Path(), help="Output file path"
)
@click.option("-l", "--language", default="python", help="Programming language")
@click.option(
    "-p",
    "--provider",
    default="groq",
    type=click.Choice(["openai", "groq"]),
    help="LLM provider",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option(
    "-a", "--api-key", "api_key", type=str, help="API key (overrides env var)"
)
def main(input_file, output_file, language, provider, verbose, api_key):
    """
    Clean Code Bot - Refactor and document your code.

    Takes a dirty or undocumented code file and returns an optimized version
    that follows SOLID principles with comprehensive documentation.

    Examples:

        clean-code-bot dirty.py

        clean-code-bot dirty.py -o clean.py -v

        clean-code-bot script.py --language javascript
    """
    if api_key:
        os.environ["GROQ_API_KEY" if provider == "groq" else "OPENAI_API_KEY"] = api_key

    try:
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                code = f.read()
            if verbose:
                click.echo(
                    f"[{click.style('INFO', fg='green')}] Read {len(code)} characters from {input_file}"
                )
        else:
            if verbose:
                click.echo(
                    f"[{click.style('INFO', fg='green')}] Waiting for stdin input..."
                )
            code = sys.stdin.read()

        if not code.strip():
            click.echo(
                click.style("Error: No input code provided.", fg="red"), err=True
            )
            sys.exit(1)

        bot = CleanCodeBot(provider=provider)

        if verbose:
            click.echo(f"[{click.style('INFO', fg='green')}] Processing code...")

        result = bot.process(code, language=language, verbose=verbose)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            click.echo(
                click.style(f"Success: Output written to {output_file}", fg="green")
            )
        else:
            click.echo(result)

    except ValueError as e:
        click.echo(click.style(f"Validation Error: {str(e)}", fg="red"), err=True)
        sys.exit(1)
    except RuntimeError as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nAborted.", err=True)
        sys.exit(130)


if __name__ == "__main__":
    main()
