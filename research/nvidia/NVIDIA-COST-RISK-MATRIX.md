# NVIDIA Cost-Risk Matrix

This matrix collapses NVIDIA catalog entries into service families relevant to this Etsy project. It is an audit artifact, not an integration plan.

| RESOURCE | FREE_STATUS | PRODUCTION_STATUS | EXTERNAL_COMPUTE_REQUIRED | LICENSE_RISK | DEPRECATION_RISK | VENDOR_LOCKIN_RISK | ETSY_RELEVANCE | CORE_ALLOWED | OPTIONAL_ALLOWED | HUMAN_ACTION_REQUIRED | DECISION |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Hosted reasoning, chat, and coding endpoints on NVIDIA Build | FREE_DEVELOPER_PROGRAM | RESEARCH_ONLY | NO | MEDIUM | MEDIUM | MEDIUM | HIGH | NO | YES | YES | RESEARCH_ONLY |
| Embedding and RAG endpoints | FREE_DEVELOPER_PROGRAM | RESEARCH_ONLY | NO | MEDIUM | HIGH | MEDIUM | HIGH | NO | YES | YES | RESEARCH_ONLY |
| Safety and moderation endpoints | FREE_DEVELOPER_PROGRAM | RESEARCH_ONLY | NO | MEDIUM | MEDIUM | MEDIUM | MEDIUM | NO | YES | YES | RESEARCH_ONLY |
| Translation endpoints | FREE_DEVELOPER_PROGRAM | RESEARCH_ONLY | NO | LOW | MEDIUM | MEDIUM | LOW | NO | YES | YES | RESEARCH_ONLY |
| Vision and multimodal endpoints | FREE_DEVELOPER_PROGRAM | RESEARCH_ONLY | NO | MEDIUM | MEDIUM | HIGH | LOW | NO | NO | YES | BLOCK |
| Downloadable NIM microservices for self-hosting | FREE_DEVELOPER_PROGRAM | RESEARCH_ONLY | YES | MEDIUM | MEDIUM | HIGH | HIGH | NO | YES | YES | RESEARCH_ONLY |
| Brev GPU instances | PAID_OR_BILLABLE | BLOCK | YES | HIGH | LOW | HIGH | LOW | NO | NO | YES | BLOCK |
| Blueprints and agent recipes | UNKNOWN | RESEARCH_ONLY | MAYBE | MEDIUM | MEDIUM | HIGH | LOW | NO | NO | YES | BLOCK |

## Notes

- `FREE_DEVELOPER_PROGRAM` rows still require user sign-in and terms acceptance.
- `RESEARCH_ONLY` rows may inform planning or tests, but they must not become deterministic core dependencies.
- `BLOCK` rows are not appropriate for this repo's current architecture or cost policy.
- OpenAI-compatible API support is a transport boundary only; it inherits the cost and license profile of the backing provider.
- Low-relevance categories such as audio, robotics, video generation, and physical AI are deliberately excluded from the Etsy RQ2 path.

