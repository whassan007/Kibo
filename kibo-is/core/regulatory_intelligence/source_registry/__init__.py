"""
KIBO Privacy OS — Unified Curated Regulatory Source Registry (Section 4)
Aggregates authoritative US, Canadian, and European Union legislative, regulatory,
supervisory, enforcement, and judicial sources across G01–G15.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from core.regulatory_intelligence import RegulatorySourceEntry
from core.regulatory_intelligence.source_registry.us_federal_sources import (
    AUTHENTIC_US_FEDERAL_FIXTURES,
    get_us_federal_sources,
)
from core.regulatory_intelligence.source_registry.us_states_a_m_sources import (
    AUTHENTIC_US_STATE_A_M_AMENDMENT_FIXTURES,
    get_us_states_a_m_sources,
)
from core.regulatory_intelligence.source_registry.us_states_n_w_dc_sources import (
    get_us_states_n_w_dc_sources,
)
from core.regulatory_intelligence.source_registry.us_enforcement_sources import (
    AUTHENTIC_US_ENFORCEMENT_FIXTURES,
    get_us_enforcement_sources,
)
from core.regulatory_intelligence.source_registry.us_judicial_sources import (
    AUTHENTIC_US_JUDICIAL_FIXTURES,
    get_us_judicial_sources,
)
from core.regulatory_intelligence.source_registry.canada_federal_sources import (
    AUTHENTIC_CANADA_FEDERAL_FIXTURES,
    get_canada_federal_sources,
)
from core.regulatory_intelligence.source_registry.canada_provincial_sources import (
    AUTHENTIC_CANADA_PROVINCIAL_FIXTURES,
    get_canada_provincial_sources,
)
from core.regulatory_intelligence.source_registry.canada_commissioner_sources import (
    AUTHENTIC_CANADIAN_COMMISSIONER_DECISIONS,
    get_canada_commissioner_sources,
)
from core.regulatory_intelligence.source_registry.canada_judicial_sources import (
    AUTHENTIC_CANADIAN_JUDICIAL_FIXTURES,
    get_canada_judicial_sources,
)
from core.regulatory_intelligence.source_registry.eu_union_sources import (
    AUTHENTIC_EURLEX_FIXTURES,
    get_eu_union_sources,
)
from core.regulatory_intelligence.source_registry.eu_member_states_1_9 import (
    get_eu_member_states_1_9_sources,
)
from core.regulatory_intelligence.source_registry.eu_member_states_10_18 import (
    AUTHENTIC_FR_DE_MULTILINGUAL_FIXTURES,
    get_eu_member_states_10_18_sources,
)
from core.regulatory_intelligence.source_registry.eu_member_states_19_27 import (
    get_eu_member_states_19_27_sources,
)
from core.regulatory_intelligence.source_registry.eu_edpb_edps_cjeu_sources import (
    AUTHENTIC_CJEU_EDPB_FIXTURES,
    get_eu_edpb_edps_cjeu_sources,
)
from core.regulatory_intelligence.source_registry.eu_national_dpa_sources import (
    AUTHENTIC_EU_DPA_DECISION_FIXTURES,
    get_eu_national_dpa_sources,
)


def get_all_regulatory_sources() -> List[RegulatorySourceEntry]:
    """Return deduplicated list of all curated US, Canadian, and EU regulatory sources."""
    combined: List[RegulatorySourceEntry] = []
    seen_ids = set()
    for getter in (
        get_us_federal_sources,
        get_us_states_a_m_sources,
        get_us_states_n_w_dc_sources,
        get_us_enforcement_sources,
        get_us_judicial_sources,
        get_canada_federal_sources,
        get_canada_provincial_sources,
        get_canada_commissioner_sources,
        get_canada_judicial_sources,
        get_eu_union_sources,
        get_eu_member_states_1_9_sources,
        get_eu_member_states_10_18_sources,
        get_eu_member_states_19_27_sources,
        get_eu_edpb_edps_cjeu_sources,
        get_eu_national_dpa_sources,
    ):
        for entry in getter():
            if entry.source_id not in seen_ids:
                seen_ids.add(entry.source_id)
                combined.append(entry)
    return combined


def get_sources_by_jurisdiction(jurisdiction_id: str) -> List[RegulatorySourceEntry]:
    jur = jurisdiction_id.strip().upper()
    return [
        s for s in get_all_regulatory_sources()
        if s.jurisdiction_id.upper() == jur or (s.parent_jurisdiction and s.parent_jurisdiction.upper() == jur)
    ]


def get_allowed_official_domains() -> List[str]:
    return sorted({s.official_domain.lower() for s in get_all_regulatory_sources() if s.official_domain})
