# GenAI Platform Operating Model

## Team Structure

### Platform Team (Central)
- Owns the GenAI platform infrastructure
- Maintains guardrails, evaluation framework, observability
- Manages model registry and prompt registry
- Provides developer experience (SDK, templates, documentation)
- Does NOT build applications — enables teams to build them

### Application Teams (Domain)
- Build GenAI applications on the shared platform
- Own their prompts, RAG pipelines, and evaluation suites
- Responsible for application-level quality and monitoring
- Follow platform standards for deployment and governance

### AI Governance (Advisory)
- Sets risk classification criteria
- Reviews high-risk use cases before production
- Maintains compliance mapping (EU AI Act, SR 11-7)
- Audits platform compliance periodically

## On-Call

- Platform team: 24/7 on-call for infrastructure issues
- Application teams: business-hours on-call for application issues
- Escalation: application → platform → engineering leadership

## Incident Response

| Severity | Description | Response Time | Escalation |
|---|---|---|---|
| P1 | LLM producing harmful or non-compliant output | 15 min | Immediate: kill switch, notify compliance |
| P2 | LLM unavailable or severely degraded | 30 min | Activate fallback chain, notify teams |
| P3 | Quality degradation detected by monitoring | 4 hours | Investigate, consider model rollback |
| P4 | Non-urgent issue (cost spike, minor quality drift) | Next business day | Investigate and remediate |
