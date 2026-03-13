# Enterprise GenAI Platform

**Reference architecture for deploying LLM-based applications in regulated financial services.**

Most GenAI demos fail in production because they skip guardrails, evaluation, and governance. This is the missing layer — the infrastructure between "the LLM can do it" and "we can ship it in a bank."

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           Enterprise GenAI Platform       │
                    │                                           │
User Query ────────▶│  [Input Validation]                       │
                    │       ↓                                   │
                    │  [Chain Router] ──▶ Prompt Registry        │
                    │       ↓                                   │
                    │  [RAG Retrieval] ──▶ Vector Store          │
                    │       ↓                                   │
                    │  [LLM Generation] ──▶ Model Registry      │
                    │       ↓                                   │
                    │  [Output Filter]                          │
                    │       ↓                                   │
                    │  [Trace + Cost Log]                       │
                    │       ↓                                   │
                    └───────┼──────────────────────────────────┘
                            ↓
                       Response

```

## Components

### Orchestration
- **Chain Router** — routes requests to the right LLM chain based on intent classification
- **Prompt Registry** — versioned prompt management with rollback capability
- **Fallback Handler** — graceful degradation when the LLM is unavailable or produces low-confidence output

### Guardrails
- **Input Validator** — PII detection, prompt injection defense, content policy enforcement
- **Output Filter** — hallucination flagging, compliance checks, toxicity filtering
- **Toxicity Gate** — content safety filtering before responses reach users

### Evaluation
- **Eval Framework** — automated quality testing for LLM outputs
- **Metrics** — faithfulness, relevance, groundedness measurement
- **Regression Tests** — detect quality degradation across model updates

### RAG
- **Retriever** — document retrieval with configurable strategy (naive, hybrid, parent document)
- **Chunking** — multiple chunking strategies for document processing
- **Index Manager** — vector store lifecycle (create, update, rebuild)

### Observability
- **Trace Logger** — full request/response trace capture
- **Cost Tracker** — token usage and cost attribution per request
- **Drift Monitor** — detect output quality changes over time

## Design Decisions

See `docs/design-decisions.md` for the reasoning behind each architectural choice.

## Disclaimer

This is a reference architecture — it demonstrates patterns and trade-offs, not production-ready code. Adapt the patterns to your specific environment, security requirements, and regulatory context.

### Related Writing

- [Your ML Risk Framework Wasn't Built for GenAI](https://sunilprakash.com/writing/ai-governance-genai/)
- [RAG in Production: What Breaks When You Move Past the Tutorial](https://sunilprakash.com/writing/rag-in-production/)

## License

Apache 2.0
