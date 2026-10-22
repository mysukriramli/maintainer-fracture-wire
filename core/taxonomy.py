from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Directive(str, Enum):
    VENDOR_PACKAGE = "VENDOR_PACKAGE"
    FORK_AND_PIN = "FORK_AND_PIN"
    MIGRATE_WITHIN_90_DAYS = "MIGRATE_WITHIN_90_DAYS"
    ADD_SECONDARY_IMPLEMENTATION = "ADD_SECONDARY_IMPLEMENTATION"
    MAINTAINER_HEALTHY = "MAINTAINER_HEALTHY"

class ReasonCode(str, Enum):
    CRITICAL_RELEASE_STALENESS = "CRITICAL_RELEASE_STALENESS"
    SINGLE_MAINTAINER_CONCENTRATION = "SINGLE_MAINTAINER_CONCENTRATION"
    MASSIVE_DOWNSTREAM_BLAST_RADIUS = "MASSIVE_DOWNSTREAM_BLAST_RADIUS"
    DEPRECATION_OR_DISCONTINUATION = "DEPRECATION_OR_DISCONTINUATION"
    RELEASE_CADENCE_HEALTHY = "RELEASE_CADENCE_HEALTHY"

class FractureRecord(BaseModel):
    package_name: str
    ecosystem: str
    purl: str
    latest_version: str
    days_since_last_release: float
    estimated_maintainer_count: int
    direct_dependents: int
    fracture_probability_score: float = Field(ge=0.0, le=100.0)
    directive: Directive
    confidence: float = Field(ge=0.0, le=1.0)
    reason_codes: List[ReasonCode]
    alternatives: List[str]
