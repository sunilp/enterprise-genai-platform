# LLM Model Selection Guide

## Decision Framework

### Step 1: Data Classification

What data will the model process?

| Data Classification | Constraint |
|---|---|
| Public | Any approved model |
| Internal | Models with enterprise agreement and data protection |
| Confidential | Models with data residency guarantees, no training on inputs |
| Restricted (PII, financial) | Self-hosted or contractually guaranteed no-retention |

### Step 2: Task Complexity

| Complexity | Recommended Tier |
|---|---|
| Classification, routing | Small model (gpt-4o-mini, gemini-flash) |
| Q&A, summarization | Medium model (gpt-4o, claude-sonnet, gemini-pro) |
| Complex reasoning, multi-step | Large model (gpt-4o, claude-opus) |
| Code generation, analysis | Specialized model (claude-sonnet, gpt-4o) |

### Step 3: Latency Requirements

| Requirement | Approach |
|---|---|
| Real-time (< 2s) | Smaller model, cached responses, streaming |
| Interactive (< 10s) | Standard model, async where possible |
| Batch (minutes) | Any model, optimize for cost over speed |

### Step 4: Cost Sensitivity

For high-volume applications, model cost is the dominant factor. Consider:
- Can a smaller model handle 80% of queries? Route only complex queries to the expensive model.
- Can responses be cached? Semantic caching can reduce costs by 30-50%.
- Is the quality difference between models significant for your use case? Test before assuming bigger = better.
