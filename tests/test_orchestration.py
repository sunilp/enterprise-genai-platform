"""Tests for orchestration modules."""

from src.orchestration.chain_router import ChainRouter, ChainConfig, Intent
from src.orchestration.prompt_registry import PromptRegistry


class TestChainRouter:
    def setup_method(self):
        self.router = ChainRouter(
            chains={
                Intent.QUESTION_ANSWERING: ChainConfig(
                    intent=Intent.QUESTION_ANSWERING,
                    model="gpt-4o",
                    prompt_template="Answer: {question}",
                ),
                Intent.SUMMARIZATION: ChainConfig(
                    intent=Intent.SUMMARIZATION,
                    model="gpt-4o-mini",
                    prompt_template="Summarize: {text}",
                ),
                Intent.GENERAL: ChainConfig(
                    intent=Intent.GENERAL,
                    model="gpt-4o-mini",
                    prompt_template="{input}",
                ),
            },
        )

    def test_routes_question(self):
        result = self.router.route("What does BCBS 239 require?")
        assert result.intent == Intent.QUESTION_ANSWERING

    def test_routes_summary(self):
        result = self.router.route("Summarize this document for me")
        assert result.intent == Intent.SUMMARIZATION

    def test_default_route(self):
        result = self.router.route("Hello there")
        assert result.intent == Intent.GENERAL


class TestPromptRegistry:
    def test_register_and_get(self):
        registry = PromptRegistry()
        registry.register("test", "Hello {name}")
        prompt = registry.get("test")
        assert prompt.render(name="world") == "Hello world"

    def test_versioning(self):
        registry = PromptRegistry()
        registry.register("test", "v1: {x}")
        registry.register("test", "v2: {x}")
        assert registry.get("test").version == 2
        assert registry.get("test", version=1).version == 1

    def test_rollback(self):
        registry = PromptRegistry()
        registry.register("test", "v1")
        registry.register("test", "v2")
        registry.rollback("test", version=1)
        assert registry.get("test").template == "v1"
