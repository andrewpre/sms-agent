from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

REQUIRED_SECTIONS: tuple[str, ...] = (
    "## Purpose",
    "## Responsibilities",
    "## Non-Goals",
    "## Allowed Tools",
    "## Input Contract",
    "## Output Contract",
    "## Escalation Rules",
    "## Safety Rules",
)

DEFAULT_FALLBACK_PROMPT = (
    "You are a focused SMS assistant. Use only available tools, keep responses short, "
    "and avoid making unsupported claims."
)

@dataclass(frozen=True)
class SkillDocument:
    agent_name: str
    path: Path
    content: str


def skills_directory() -> Path:
    return Path(__file__).parent / "skills"


def skill_path_for_agent(agent_name: str) -> Path:
    return skills_directory() / f"{agent_name}.md"


def validate_skill_markdown(content: str) -> list[str]:
    missing_sections: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            missing_sections.append(section)
    return missing_sections


def _read_skill(agent_name: str) -> SkillDocument:
    path = skill_path_for_agent(agent_name)
    content = path.read_text(encoding="utf-8")
    return SkillDocument(agent_name=agent_name, path=path, content=content)


@lru_cache(maxsize=32)
def load_skill_prompt(agent_name: str) -> str:
    doc = _read_skill(agent_name)
    missing_sections = validate_skill_markdown(doc.content)
    if missing_sections:
        missing = ", ".join(missing_sections)
        raise ValueError(
            f"Skill markdown for agent '{agent_name}' is missing required sections: {missing}"
        )
    skill = (f"Follow this agent skill contract for '{agent_name}'. "
        "Do not violate non-goals or safety rules.\n\n"
        f"{doc.content}")
    # print(f"=================== SKILL: {skill} ====================")
    return skill


def load_skill_prompt_safe(phone_number, agent_name: str) -> str:
    try:
        return load_skill_prompt(agent_name)
    except Exception:
        return DEFAULT_FALLBACK_PROMPT


def validate_agent_skills(agent_names: list[str]) -> list[str]:
    errors: list[str] = []
    for agent_name in agent_names:
        path = skill_path_for_agent(agent_name)
        if not path.exists():
            errors.append(f"Missing skill file for agent '{agent_name}': {path}")
            continue
        try:
            _ = load_skill_prompt(agent_name)
        except Exception as exc:
            errors.append(str(exc))
    return errors
