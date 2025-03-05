"""Prompt Registry — versioned prompt management.

Manages prompt templates with versioning, A/B testing support,
and rollback capability. Prompts are loaded from YAML configuration
and can be updated without code deployment.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PromptVersion:
    """A versioned prompt template."""
    template: str
    version: int
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.sha256(self.template.encode()).hexdigest()[:12]

    def render(self, **kwargs) -> str:
        """Render the template with variables."""
        return self.template.format(**kwargs)


class PromptRegistry:
    """Manage versioned prompt templates.

    Usage:
        registry = PromptRegistry()
        registry.register("qa_prompt", "Answer based on: {context}\\nQ: {question}\\nA:")
        prompt = registry.get("qa_prompt").render(context="...", question="...")

        # Update prompt
        registry.register("qa_prompt", "New template: {context}\\n{question}")

        # Rollback
        registry.rollback("qa_prompt", version=1)
    """

    def __init__(self):
        self._prompts: Dict[str, List[PromptVersion]] = {}
        self._active: Dict[str, int] = {}

    def register(self, name: str, template: str, metadata: Optional[Dict] = None) -> PromptVersion:
        """Register a new prompt version."""
        if name not in self._prompts:
            self._prompts[name] = []

        version = len(self._prompts[name]) + 1
        pv = PromptVersion(
            template=template,
            version=version,
            metadata=metadata or {},
        )
        self._prompts[name].append(pv)
        self._active[name] = version
        return pv

    def get(self, name: str, version: Optional[int] = None) -> PromptVersion:
        """Get a prompt by name. Returns active version by default."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found")

        target_version = version or self._active[name]
        versions = self._prompts[name]

        for pv in versions:
            if pv.version == target_version:
                return pv

        raise KeyError(f"Version {target_version} not found for prompt '{name}'")

    def rollback(self, name: str, version: int) -> None:
        """Set the active version to a previous version."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found")
        if version < 1 or version > len(self._prompts[name]):
            raise ValueError(f"Invalid version {version}")
        self._active[name] = version

    def list_prompts(self) -> Dict[str, Dict[str, Any]]:
        """List all prompts with their active versions."""
        return {
            name: {
                "active_version": self._active[name],
                "total_versions": len(versions),
                "active_hash": self.get(name).hash,
            }
            for name, versions in self._prompts.items()
        }
