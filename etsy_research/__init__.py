from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path


__path__ = extend_path(__path__, __name__)  # type: ignore[name-defined]
_SRC_PACKAGE = Path(__file__).resolve().parent.parent / "src" / "etsy_research"
if _SRC_PACKAGE.is_dir():
    __path__.append(str(_SRC_PACKAGE))  # type: ignore[attr-defined]

from .analyze import (  # noqa: E402
    assign_review_cohort,
    calculate_cr10,
    calculate_cr5,
    calculate_entry_score,
    calculate_new_shop_share,
    calculate_price_summary,
    calculate_rank_window_metrics,
    calculate_recent_listing_share,
    calculate_unique_shop_penetration,
    classify_verdict,
)
from .config import load_query_config, load_threshold_config  # noqa: E402
from .models import (  # noqa: E402
    CanonicalListing,
    CanonicalShop,
    EntryScoreResult,
    FamilyMetrics,
    PriceSummary,
    QueryDefinition,
    QueryMetrics,
    RankWindowMetrics,
    RawObservation,
    ResearchRun,
    ResearchVerdict,
)
from .normalize import build_canonical_listings, build_canonical_shops, normalize_listing_id  # noqa: E402

__all__ = [
    "__version__",
    "assign_review_cohort",
    "build_canonical_listings",
    "build_canonical_shops",
    "calculate_cr10",
    "calculate_cr5",
    "calculate_entry_score",
    "calculate_new_shop_share",
    "calculate_price_summary",
    "calculate_rank_window_metrics",
    "calculate_recent_listing_share",
    "calculate_unique_shop_penetration",
    "classify_verdict",
    "load_query_config",
    "load_threshold_config",
    "normalize_listing_id",
    "CanonicalListing",
    "CanonicalShop",
    "EntryScoreResult",
    "FamilyMetrics",
    "PriceSummary",
    "QueryDefinition",
    "QueryMetrics",
    "RankWindowMetrics",
    "RawObservation",
    "ResearchRun",
    "ResearchVerdict",
]

__version__ = "0.1.0"

