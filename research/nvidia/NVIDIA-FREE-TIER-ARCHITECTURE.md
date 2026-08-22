# NVIDIA Free-Tier Architecture

## Executive Summary

NVIDIA is an optional capability layer, not a core dependency.

The Etsy research engine remains deterministic and provider-independent. NVIDIA may be used later for advisory tasks such as summarization, external-source synthesis, hypothesis generation, or code assistance, but never for ranking metrics, cohorts, thresholds, or verdicts.

## Current State

- `AI_ENABLED=false` by default.
- `NullAIProvider` is the only implemented provider.
- Core analysis modules do not import NVIDIA packages.
- No live NVIDIA requests are made in this phase.
- No live Etsy requests are made in this phase.

## Target Shape

```text
User
  |
  v
Deterministic Etsy Research Engine
  |
  +-----------------------------+
  |                             |
  v                             v
Core metrics and verdicts   Optional advisory AI
                                  |
                          Provider-neutral interface
                                  |
                 +----------------+----------------+
                 |                |                |
              NVIDIA          Local model       Other provider
```

## Provider-Neutral Interface

The minimal boundary is:

- `AIProvider` protocol
- `AIResult` advisory output object
- `NullAIProvider` fallback
- `AISettings` configuration object

Planned future adapters can include:

- `OpenAICompatibleProvider`
- `NvidiaAIProvider`
- `LocalAIProvider`

The deterministic engine must not call any of these for:

- metric calculation
- ranking
- maturity buckets
- thresholds
- verdicts

## Configuration Surface

Recommended environment variables for a future optional AI layer:

- `AI_ENABLED`
- `AI_PROVIDER`
- `AI_MODEL`
- `AI_BASE_URL`
- `AI_API_KEY_ENV_NAME`
- `AI_COST_CLASS`
- `AI_DEPENDENCY_CLASS`
- `ALLOW_PAID_AI`

Provider-specific values such as `NVIDIA_API_KEY`, `NVIDIA_BASE_URL`, and `NVIDIA_MODEL` must remain placeholders until a human explicitly approves a live integration.

## Allowed Optional Uses

Potentially useful, non-authoritative NVIDIA tasks:

- report summarization
- external-source synthesis
- hypothesis generation
- query-family interpretation
- code assistance
- document/RAG experimentation
- synthetic test-data generation

## Explicit Non-Goals

NVIDIA must not determine:

- ranking metrics
- review cohort assignment
- sales cohort assignment
- shop age
- penetration percentages
- entry score
- GO / CONDITIONAL_GO / NO_GO verdicts
- fee calculations
- financial calculations

RQ2 currently does not require embeddings or vector search, so `RAG_INTEGRATION_CURRENTLY_REQUIRED=NO`.

## Evidence

Official NVIDIA documentation shows:

- build.nvidia.com advertises free serverless APIs for development and requires sign-in plus developer-program terms before API key creation.
- NVIDIA NIM LLM API docs describe an OpenAI-compatible inference API.
- NVIDIA Brev bills per hour for running GPU instances.

That means the correct architecture is:

`CORE -> OPTIONAL_AI`, not `AI -> CORE`.

