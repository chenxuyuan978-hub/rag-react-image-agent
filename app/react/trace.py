import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReActStep:
    """One ReAct execution step."""

    thought: str
    action: str
    action_input: dict[str, Any]
    observation: dict[str, Any]


@dataclass
class ReActTrace:
    """Complete ReAct execution trace."""

    steps: list[ReActStep] = field(default_factory=list)
    final_answer: str = ""

    def to_text(self) -> str:
        """Format the trace as readable text."""
        lines: list[str] = []
        for index, step in enumerate(self.steps, start=1):
            lines.append(f"Step {index}")
            lines.append(f"Thought: {step.thought}")
            lines.append(f"Action: {step.action}")
            lines.append(
                "Action Input: "
                + json.dumps(step.action_input, ensure_ascii=False, indent=2)
            )
            lines.append(
                "Observation: "
                + json.dumps(step.observation, ensure_ascii=False, indent=2)
            )
            lines.append("")

        lines.append(f"Final Answer: {self.final_answer}")
        return "\n".join(lines)
