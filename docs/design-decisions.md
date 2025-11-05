# Design Decisions

## ADR-001: Guardrails as a First-Class Component

**Decision:** Input validation and output filtering are part of the core pipeline, not optional middleware.

**Context:** In regulated environments, every LLM interaction must be validated and logged. Treating guardrails as optional leads to inconsistent enforcement — some teams add them, others don't.

**Consequence:** Every request passes through input validation and every response passes through output filtering, regardless of the use case. This adds ~50ms of latency but ensures consistent safety enforcement.

## ADR-002: Prompt Registry Over Hardcoded Prompts

**Decision:** All prompts are managed through a versioned registry, not hardcoded in application code.

**Context:** Prompt changes are the most frequent modification in GenAI applications. Hardcoding prompts in code means every prompt change requires a code deployment. A registry allows prompt updates without code changes, with version history and rollback.

**Consequence:** Slight increase in complexity but significant improvement in iteration speed and auditability.

## ADR-003: Model Registry with Risk Classification

**Decision:** Only models listed in the model registry may be used in production. Each model has a risk classification that determines which use cases it's approved for.

**Context:** In banking, model risk management (SR 11-7) requires that every model in production is documented, validated, and monitored. An unregistered model is an ungoverned model.

**Consequence:** New models require an approval process before production use. This slows down adoption of new models but ensures governance.

## ADR-004: Fallback Chain for Reliability

**Decision:** Every GenAI endpoint has a defined fallback chain: retry → cheaper model → canned response.

**Context:** LLM APIs have variable availability. In banking applications, "service unavailable" is not an acceptable response. A defined fallback chain ensures the system degrades gracefully.

## ADR-005: Cost Tracking Per Request

**Decision:** Every request is tracked for token usage and cost, attributed to the requesting team/application.

**Context:** GenAI costs can scale unexpectedly. Without per-request cost tracking, it's impossible to identify cost drivers or set team-level budgets. Token tracking also supports chargeback models for shared platform services.
