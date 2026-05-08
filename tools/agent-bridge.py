#!/usr/bin/env python3
"""
Agent Bridge — Concept for LLM-Driven Tool Execution in PrivateGPT

Inspired by the Hermes Agentic CLI ReAct loop. This is a conceptual bridge
showing how PrivateGPT could be extended with tool-use capabilities.

CURRENT STATUS: Concept / Standalone Script
To fully integrate, this would need to be wired into PrivateGPT's chat endpoint
as a post-processing layer or middleware.

Usage (standalone demo):
    python3 agent-bridge.py --task "List all Python files in /home/exo"

Requirements:
    pip install requests
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests


class ToolResult:
    """Result of a tool execution."""

    def __init__(self, success: bool, output: str = "", error: str = "", data: Optional[dict] = None):
        self.success = success
        self.output = output
        self.error = error
        self.data = data or {}

    def __repr__(self):
        status = "OK" if self.success else "ERR"
        return f"[{status}] {self.output[:100]}..."


class TerminalTool:
    """Execute shell commands safely."""

    name = "terminal"
    description = "Execute shell commands in the working directory"

    # Commands that require explicit approval
    DANGEROUS = {"rm", "sudo", "dd", "mkfs", "fdisk", "format", "del", "rd"}

    def __init__(self, working_dir: str = "."):
        self.working_dir = Path(working_dir).resolve()

    def execute(self, command: str, timeout: int = 30) -> ToolResult:
        # Safety: check for dangerous commands
        cmd_parts = command.strip().split()
        if cmd_parts and cmd_parts[0] in self.DANGEROUS:
            return ToolResult(
                success=False,
                error=f"Command '{cmd_parts[0]}' is blocked for safety. "
                      f"Run manually if you really need this.",
            )

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode == 0:
                return ToolResult(success=True, output=result.stdout[:10000])
            else:
                return ToolResult(
                    success=False,
                    output=result.stdout[:5000],
                    error=result.stderr[:5000],
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error=f"Command timed out after {timeout}s")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class FileReadTool:
    """Read file contents."""

    name = "file_read"
    description = "Read the contents of a file"

    def __init__(self, working_dir: str = ".", max_size: int = 100000):
        self.working_dir = Path(working_dir).resolve()
        self.max_size = max_size

    def execute(self, path: str, offset: int = 1, limit: int = 200) -> ToolResult:
        try:
            file_path = Path(path)
            if not file_path.is_absolute():
                file_path = self.working_dir / file_path
            file_path = file_path.resolve()

            # Security: stay within working dir
            file_path.relative_to(self.working_dir)

            if not file_path.exists():
                return ToolResult(success=False, error=f"File not found: {path}")

            size = file_path.stat().st_size
            if size > self.max_size:
                return ToolResult(success=False, error=f"File too large: {size} bytes")

            with open(file_path, "r", errors="replace") as f:
                lines = f.readlines()

            start = max(0, offset - 1)
            end = min(len(lines), start + limit)
            selected = lines[start:end]

            content = "".join(selected)
            if offset > 1 or limit < len(lines):
                numbered = [f"{i+1:4d}| {line}" for i, line in enumerate(selected, start=start)]
                content = "".join(numbered)

            return ToolResult(
                success=True,
                output=content,
                data={"total_lines": len(lines), "lines_read": len(selected)},
            )
        except ValueError:
            return ToolResult(success=False, error=f"Access denied: {path} is outside working directory")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class FileListTool:
    """List directory contents."""

    name = "file_list"
    description = "List files and directories"

    def __init__(self, working_dir: str = "."):
        self.working_dir = Path(working_dir).resolve()

    def execute(self, path: str = ".", recursive: bool = False) -> ToolResult:
        try:
            target = Path(path)
            if not target.is_absolute():
                target = self.working_dir / target
            target = target.resolve()
            target.relative_to(self.working_dir)

            if not target.is_dir():
                return ToolResult(success=False, error=f"Not a directory: {path}")

            entries = []
            iterator = target.rglob("*") if recursive else target.iterdir()
            for item in iterator:
                rel = item.relative_to(target)
                entries.append({
                    "name": str(rel),
                    "type": "dir" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                })

            entries.sort(key=lambda x: (0 if x["type"] == "dir" else 1, x["name"]))
            lines = []
            for e in entries:
                icon = "📁" if e["type"] == "dir" else "📄"
                size = f"({e['size']:,}b)" if e.get("size") else ""
                lines.append(f"{icon} {e['name']} {size}")

            return ToolResult(success=True, output="\n".join(lines), data={"count": len(entries)})
        except ValueError:
            return ToolResult(success=False, error="Access denied: path outside working directory")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ToolRegistry:
    """Registry of available tools."""

    def __init__(self, working_dir: str = "."):
        self.tools = {
            "terminal": TerminalTool(working_dir),
            "file_read": FileReadTool(working_dir),
            "file_list": FileListTool(working_dir),
        }

    def list_tools(self) -> List[dict]:
        return [{"name": name, "description": t.description} for name, t in self.tools.items()]

    def execute(self, name: str, arguments: dict) -> ToolResult:
        tool = self.tools.get(name)
        if not tool:
            return ToolResult(success=False, error=f"Unknown tool: {name}")
        try:
            return tool.execute(**arguments)
        except TypeError as e:
            return ToolResult(success=False, error=f"Invalid arguments for {name}: {e}")


class OllamaClient:
    """Minimal Ollama client for the agent loop."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    def chat(self, messages: List[Dict[str, str]], model: str, temperature: float = 0.7) -> dict:
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "options": {"temperature": temperature},
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


class AgentBridge:
    """
    ReAct agent loop that connects to Ollama and executes tools.

    This is the bridge concept: LLM reasons, decides to use tools,
    executes them, observes results, and continues.
    """

    TOOL_PATTERN = re.compile(r"```(?:tool|json)\s*\n?({[\s\S]*?})\s*```")

    def __init__(self, ollama_url: str = "http://localhost:11434", working_dir: str = "."):
        self.llm = OllamaClient(ollama_url)
        self.tools = ToolRegistry(working_dir)
        self.max_iterations = 20

    def _build_system_prompt(self) -> str:
        tool_descs = "\n".join(
            f"- {t['name']}: {t['description']}" for t in self.tools.list_tools()
        )
        return f"""You are an autonomous agent. Your goal is to complete tasks using available tools.

AVAILABLE TOOLS:
{tool_descs}

INSTRUCTIONS:
1. Analyze the task and break it into steps
2. Use tools when needed (terminal, file_read, file_list)
3. After each tool use, observe the result and plan next steps
4. When complete, say TASK COMPLETE and summarize

TOOL FORMAT:
When you need a tool, output exactly:
```tool
{{"name": "tool_name", "arguments": {{"param": "value"}}}}
```

SAFETY:
- Destructive commands (rm, sudo) are blocked
- You cannot access files outside the working directory
"""

    def run(self, task: str, model: str = "dolphin-mistral") -> str:
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": f"Task: {task}"},
        ]

        print(f"🤖 Task: {task}")
        print(f"   Model: {model}")
        print(f"   Max iterations: {self.max_iterations}\n")

        for i in range(self.max_iterations):
            print(f"--- Iteration {i + 1} ---")

            response = self.llm.chat(messages, model)
            if "error" in response:
                return f"Error: {response['error']}"

            content = response.get("message", {}).get("content", "")
            print(f"💭 Thought: {content[:200]}...")

            messages.append({"role": "assistant", "content": content})

            # Check for completion
            if "task complete" in content.lower():
                print(f"\n✅ Task complete after {i + 1} iterations")
                return content

            # Parse tool call
            match = self.TOOL_PATTERN.search(content)
            if match:
                try:
                    tool_call = json.loads(match.group(1))
                    name = tool_call.get("name") or tool_call.get("tool")
                    arguments = tool_call.get("arguments") or tool_call.get("args") or {}

                    print(f"🔧 Tool: {name}({arguments})")
                    result = self.tools.execute(name, arguments)

                    if result.success:
                        obs = f"Success: {result.output[:2000]}"
                    else:
                        obs = f"Error: {result.error[:2000]}"

                    print(f"📊 Result: {obs[:150]}...")
                    messages.append({"role": "user", "content": f"Tool result:\n{obs}"})
                except json.JSONDecodeError:
                    messages.append({"role": "user", "content": "Invalid tool format. Use the specified JSON format."})
            else:
                # No tool call — ask to continue or complete
                messages.append({
                    "role": "user",
                    "content": "If the task is complete, say TASK COMPLETE. Otherwise, use a tool to make progress.",
                })

        return f"Reached max iterations ({self.max_iterations}). Last response: {content[:500]}"


def main():
    parser = argparse.ArgumentParser(description="Agent Bridge — LLM-driven tool execution")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--model", default="dolphin-mistral", help="Ollama model to use")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--working-dir", default=".", help="Working directory for tools")
    args = parser.parse_args()

    bridge = AgentBridge(ollama_url=args.ollama_url, working_dir=args.working_dir)
    result = bridge.run(task=args.task, model=args.model)
    print("\n" + "=" * 60)
    print("FINAL RESULT:")
    print(result)


if __name__ == "__main__":
    main()
