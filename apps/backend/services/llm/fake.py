"""Deterministic offline LLM client — FOR TESTS AND LOCAL DEVELOPMENT ONLY.

This fake generates working code snippets matching common programming requests
(addition, factorial, fibonacci, prime checking, sorting, string manipulation)
and provides clean, human-readable execution summaries.
"""

from __future__ import annotations

import json
import re


class FakeLLMClient:
    """A configurable, deterministic stand-in for a real LLM provider."""

    model = "fake-llm-1"
    is_mock = True

    def __init__(
        self,
        *,
        response: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self._error = error
        self._response = response
        self.last_system: str | None = None
        self.last_user: str | None = None
        self.calls = 0

    def complete(self, *, system: str, user: str) -> str:
        self.calls += 1
        self.last_system = system
        self.last_user = user
        if self._error is not None:
            raise self._error
        if self._response is not None:
            return self._response
        return self._default_response(user)

    # --- deterministic default output ----------------------------------
    def _default_response(self, user: str) -> str:
        language = self._detect_language(user)
        request = " ".join(user.split())
        code = self._stub_code(language, request)
        summary = f"JARVIS generated executable {language.title()} solution for: '{request}'."
        return json.dumps({"language": language, "code": code, "summary": summary})

    @staticmethod
    def _detect_language(user: str) -> str:
        text = user.lower()
        if "javascript" in text or "node" in text or "js" in text:
            return "javascript"
        if "typescript" in text or "ts" in text:
            return "typescript"
        if "java" in text and "javascript" not in text:
            return "java"
        if "c++" in text or "cpp" in text:
            return "c++"
        if "c#" in text or "csharp" in text:
            return "c#"
        if "golang" in text or " go " in f" {text} ":
            return "go"
        if "rust" in text:
            return "rust"
        if "ruby" in text:
            return "ruby"
        return "python"

    @staticmethod
    def _stub_code(language: str, request: str) -> str:
        """Generate actual working code snippets matching common programming requests."""
        text = request.lower()

        # 1. Addition / Math operations
        if any(k in text for k in ["add", "addition", "sum", "2 numbers", "two numbers", "plus"]):
            if language == "python":
                return (
                    "def add_two_numbers(a: float, b: float) -> float:\n"
                    "    \"\"\"Return the sum of two numbers.\"\"\"\n"
                    "    return a + b\n\n"
                    "# Example execution:\n"
                    "if __name__ == '__main__':\n"
                    "    num1 = 15.5\n"
                    "    num2 = 24.5\n"
                    "    total = add_two_numbers(num1, num2)\n"
                    "    print(f'Sum of {num1} and {num2} = {total}')\n"
                )
            elif language in ["javascript", "typescript"]:
                return (
                    "function addTwoNumbers(a: number, b: number): number {\n"
                    "  return a + b;\n"
                    "}\n\n"
                    "const result = addTwoNumbers(15.5, 24.5);\n"
                    "console.log('Sum:', result);\n"
                )

        # 2. Factorial
        if "factorial" in text:
            if language == "python":
                return (
                    "def factorial(n: int) -> int:\n"
                    "    \"\"\"Calculate factorial of n iteratively.\"\"\"\n"
                    "    if n < 0:\n"
                    "        raise ValueError('Factorial is not defined for negative numbers')\n"
                    "    result = 1\n"
                    "    for i in range(2, n + 1):\n"
                    "        result *= i\n"
                    "    return result\n\n"
                    "# Example execution:\n"
                    "if __name__ == '__main__':\n"
                    "    print('Factorial of 5:', factorial(5))\n"
                )
            elif language in ["javascript", "typescript"]:
                return (
                    "function factorial(n: number): number {\n"
                    "  if (n < 0) throw new Error('Factorial undefined for negative numbers');\n"
                    "  let result = 1;\n"
                    "  for (let i = 2; i <= n; i++) result *= i;\n"
                    "  return result;\n"
                    "}\n\n"
                    "console.log('Factorial of 5:', factorial(5));\n"
                )

        # 3. Fibonacci
        if "fibonacci" in text:
            if language == "python":
                return (
                    "def fibonacci(n: int) -> list[int]:\n"
                    "    \"\"\"Generate Fibonacci sequence up to n terms.\"\"\"\n"
                    "    seq = [0, 1]\n"
                    "    while len(seq) < n:\n"
                    "        seq.append(seq[-1] + seq[-2])\n"
                    "    return seq[:n]\n\n"
                    "if __name__ == '__main__':\n"
                    "    print('First 10 Fibonacci numbers:', fibonacci(10))\n"
                )

        # 4. Prime Number Check
        if "prime" in text:
            if language == "python":
                return (
                    "def is_prime(n: int) -> bool:\n"
                    "    \"\"\"Check if a number is prime.\"\"\"\n"
                    "    if n <= 1:\n"
                    "        return False\n"
                    "    for i in range(2, int(n**0.5) + 1):\n"
                    "        if n % i == 0:\n"
                    "            return False\n"
                    "    return True\n\n"
                    "if __name__ == '__main__':\n"
                    "    print('Is 29 prime?', is_prime(29))\n"
                )

        # 5. Sorting
        if "sort" in text:
            if language == "python":
                return (
                    "def bubble_sort(arr: list) -> list:\n"
                    "    \"\"\"Sort an array using bubble sort.\"\"\"\n"
                    "    n = len(arr)\n"
                    "    for i in range(n):\n"
                    "        for j in range(0, n - i - 1):\n"
                    "            if arr[j] > arr[j + 1]:\n"
                    "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
                    "    return arr\n\n"
                    "if __name__ == '__main__':\n"
                    "    data = [64, 34, 25, 12, 22, 11, 90]\n"
                    "    print('Sorted array:', bubble_sort(data))\n"
                )

        # Generic clean runnable Python solution for any other request
        clean_func_name = re.sub(r"\W+", "_", text).strip("_") or "solution"
        if language == "python":
            return (
                f"# Python Solution for: {request}\n"
                f"def {clean_func_name}():\n"
                f"    \"\"\"Full executable solution for request: {request}\"\"\"\n"
                f"    print('Executing task: {request}')\n"
                f"    return True\n\n"
                f"if __name__ == '__main__':\n"
                f"    {clean_func_name}()\n"
            )
        elif language in ["javascript", "typescript"]:
            return (
                f"// JS/TS Solution for: {request}\n"
                f"function {clean_func_name}() {{\n"
                f"  console.log('Executing task: {request}');\n"
                f"  return true;\n"
                f"}}\n"
                f"{clean_func_name}();\n"
            )

        line_comment = "//" if language not in ["python", "ruby"] else "#"
        return (
            f"{line_comment} Solution for: {request}\n"
            f"def main():\n"
            f"    print('Task completed: {request}')\n"
        )
