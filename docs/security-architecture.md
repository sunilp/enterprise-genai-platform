# Security Architecture

## Principles

1. **No PII to external LLMs** without explicit approval and contractual guarantees
2. **Encrypt everything** — in transit (TLS 1.3) and at rest (AES-256 / CMEK)
3. **Least privilege** — API keys scoped to specific models and use cases
4. **Full audit trail** — every LLM interaction logged with user attribution
5. **Defense in depth** — input validation + output filtering + monitoring

## Data Flow Security

```
User → [TLS] → API Gateway → [Auth] → Input Validator → [PII Check]
                                                              ↓
                                              [PII Redacted] → LLM API → [TLS]
                                                              ↓
                                              Output Filter → [Audit Log] → User
```

## Key Management

- LLM API keys stored in Secret Manager (GCP) or Key Vault (Azure)
- Keys rotated every 90 days
- Separate keys per environment (dev/staging/prod)
- No keys in code, config files, or environment variables on developer machines

## Data Residency

For EU-regulated data:
- Use Vertex AI (GCP Frankfurt/London region) or Azure OpenAI (EU regions)
- Verify that the provider does not train on your data (opt-out confirmed)
- Log data residency region per request for audit purposes
