# NVIDIA Human Action Gates

Any action below requires explicit human approval. The agent must stop before performing it.

| GATE | WHY IT IS HUMAN-ONLY | AGENT ACTION | CURRENT STATUS |
| --- | --- | --- | --- |
| Join the NVIDIA Developer Program | Terms acceptance cannot be delegated to the agent | Stop and request the user to act | REQUIRED |
| Accept NVIDIA Technology Access Terms | Legal acceptance must be human-approved | Stop and request the user to act | REQUIRED |
| Create or reveal an NVIDIA API key | Keys must not be created or handled without human approval | Stop and request the user to act | REQUIRED |
| Enable a paid plan, credits, or payment method | Billing actions are forbidden by default | Stop and request the user to act | REQUIRED |
| Activate a trial | Trial-only access cannot be used as a core dependency | Stop and request the user to act | REQUIRED |
| Create Brev GPU instances | This creates billable compute | Stop and request the user to act | REQUIRED |
| Deploy NIM containers or blueprints | This can create compute, license, and lock-in exposure | Stop and request the user to act | REQUIRED |
| Accept third-party model licenses | License scope must be reviewed before use | Stop and request the user to act | REQUIRED |
| Route Etsy secrets or raw Etsy data to NVIDIA | Secrets and Etsy data must not leave the project boundary | Forbidden | NEVER |

## Allowed Now

- Read official public NVIDIA documentation.
- Write guardrail documents and ADRs.
- Add placeholder configuration fields only.
- Add tests that prove optional AI does not affect deterministic Etsy analysis.
- Keep `NVIDIA_LIVE_API_REQUEST_COUNT=0`.
- Keep `ETSY_LIVE_API_REQUEST_COUNT=0`.

