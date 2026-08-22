# ADR: NVIDIA Optional Provider

Status: Accepted for the audit-only phase.

## Context

The Etsy research project is deterministic and must keep working if every NVIDIA service disappears tomorrow.

The team wants a safe way to evaluate NVIDIA free-tier resources without making them part of the critical path, without adding paid-service dependency, and without leaking Etsy data or secrets.

## Decision

Add a provider-neutral optional AI boundary and keep NVIDIA out of the deterministic core.

The implemented boundary is:

- `AIProvider` protocol for optional advisory work
- `AIResult` for advisory output
- `NullAIProvider` for the no-AI path and fallback path
- `AISettings` for future configuration

No NVIDIA adapter is added to the deterministic research pipeline in this phase.

## Alternatives Considered

1. Direct NVIDIA integration in the research engine.
2. A local-only AI system with no provider abstraction.
3. No AI boundary at all.

Rejected because each option either increases lock-in, couples the core to a provider, or makes future provider substitution more expensive.

## Consequences

Positive:

- Core Etsy metrics, verdicts, and reports remain provider-independent.
- Future AI can be introduced behind configuration instead of a rewrite.
- The no-AI path stays explicit and testable.

Negative:

- Optional AI remains advisory only until a future implementation is approved.
- A future adapter will still need fresh terms, cost, and security review before it can be used live.

## Cost Policy

- `ALLOW_PAID_AI=false` by default.
- Paid, trial, or compute-backed NVIDIA usage is blocked unless the user explicitly approves it later.
- Free access is still treated as optional, not core.

## Fallback Policy

If a future provider is unavailable:

- return advisory-unavailable
- log a sanitized error
- continue the deterministic pipeline

## Failure Mode

The failure of NVIDIA or any future AI provider must never block:

- query execution
- canonicalization
- shop enrichment
- review cohorts
- sales cohorts
- shop-age cohorts
- entry-signal metrics
- scoring
- verdict generation
- JSON / CSV / report creation

## Security Boundary

Secrets must remain local environment variables.

Never send Etsy credentials, cookies, or private member data to NVIDIA.

Never store secrets in fixtures or reports.

## Why NVIDIA Is Not Core Infrastructure

The project only needs deterministic Python analysis to answer RQ2.

NVIDIA can help with optional advisory tasks, but the business logic must remain correct without it.

That preserves portability, reduces cost risk, and avoids vendor lock-in.

