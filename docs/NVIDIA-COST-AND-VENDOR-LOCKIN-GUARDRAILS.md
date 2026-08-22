# NVIDIA Cost and Vendor Lock-In Guardrails

Status: Binding project policy for this audit.

## Purpose

NVIDIA resources may be used only as optional development or prototyping capabilities. They are never required for the deterministic Etsy research core.

## Core Independence

The Etsy research engine must remain fully functional without NVIDIA, GPU compute, paid credits, a developer-program membership, or any NVIDIA API key.

## Cost Classes

- `FREE_VERIFIED`: publicly accessible and verified free to use without a paid plan.
- `FREE_DEVELOPER_PROGRAM`: free access that requires NVIDIA account creation, developer-program membership, or similar human approval.
- `TRIAL_ONLY`: temporary access that expires or changes scope after the trial period.
- `FREE_DOWNLOAD_COMPUTE_EXTERNAL`: software is free to download, but the compute or hosting layer is external and may still cost money.
- `PAID_OR_BILLABLE`: any resource that consumes credits, charges per hour, requires payment, or creates billable cloud usage.
- `UNKNOWN`: pricing or entitlement has not been verified from official sources.

## Dependency Classes

- `OPTIONAL`: may be used only as an add-on.
- `DEVELOPMENT_ONLY`: may be used for local development or evaluation, not for core production decisions.
- `EXPERIMENTAL`: allowed only for isolated experiments and never for authoritative research outputs.
- `FORBIDDEN_AS_CORE`: may never become a required dependency of the Etsy research engine.
- `HUMAN_APPROVAL_REQUIRED`: requires the user to approve the action before the agent proceeds.

## Billing Rules

No automated:

- subscription
- trial activation
- cloud compute creation
- GPU instance creation
- paid endpoint usage
- partner-provider enrollment
- credit purchase
- payment action

If a future provider indicates any billable usage, the default must be to block it until the user explicitly approves the cost.

## Vendor Lock-In Rules

- No NVIDIA-specific model schema inside the deterministic domain layer.
- No provider-specific response model in scoring or verdict logic.
- No NVIDIA-only storage format for canonical research outputs.
- No NVIDIA-only deterministic logic.
- No proprietary AI result may become the sole evidence for a market conclusion.
- No core workflow may require a future NVIDIA feature to remain usable.

## Failure Rule

If NVIDIA is unavailable:

`AI_FEATURE_STATUS=DEGRADED_OR_DISABLED`

but:

`CORE_RESEARCH_STATUS=OPERATIONAL`

## Security Boundary

Do not send to NVIDIA:

- Etsy API keys
- Etsy OAuth tokens
- cookies
- session data
- private member data
- other raw secrets

Send only the minimum necessary sanitized context if an optional AI feature is ever enabled.

## Evidence

Official NVIDIA sources used for this audit:

- [NVIDIA Build home](https://build.nvidia.com/)
- [NVIDIA Build API key page](https://build.nvidia.com/settings/api-keys)
- [NVIDIA NIM API reference](https://docs.nvidia.com/nim/large-language-models/latest/api-reference.html)
- [NVIDIA NIM introduction](https://docs.nvidia.com/nim/large-language-models/1.14.0/introduction.html)
- [NVIDIA Brev GPU instances](https://docs.nvidia.com/brev/concepts/gpu-instances)

