import math
from typing import List, Tuple
from core.taxonomy import Directive, ReasonCode

class FractureEngine:
    @staticmethod
    def calculate_staleness_factor(days_since_release: float) -> float:
        # Logistic curve: 0 to 180 days = low risk, 365+ days = high risk, 730+ days = critical
        if days_since_release <= 90:
            return 0.1
        elif days_since_release <= 180:
            return 0.3
        elif days_since_release <= 365:
            return 0.6
        elif days_since_release <= 730:
            return 0.85
        return 1.0

    @staticmethod
    def calculate_concentration_factor(maintainer_count: int) -> float:
        # Bus factor: 1 maintainer = 1.0, 2 = 0.6, 3+ = 0.2
        if maintainer_count <= 1:
            return 1.0
        elif maintainer_count == 2:
            return 0.6
        return 0.2

    @staticmethod
    def calculate_reach_weight(direct_dependents: int) -> float:
        # Logarithmic reach scaling
        return min(2.0, max(0.5, math.log10(max(10, direct_dependents)) / 2.5))

    def evaluate(
        self,
        days_since_release: float,
        maintainer_count: int,
        direct_dependents: int,
        is_deprecated: bool = False
    ) -> Tuple[float, Directive, float, List[ReasonCode]]:
        s_factor = self.calculate_staleness_factor(days_since_release)
        c_factor = self.calculate_concentration_factor(maintainer_count)
        r_weight = self.calculate_reach_weight(direct_dependents)

        reasons: List[ReasonCode] = []
        if days_since_release >= 365:
            reasons.append(ReasonCode.CRITICAL_RELEASE_STALENESS)
        if maintainer_count <= 1:
            reasons.append(ReasonCode.SINGLE_MAINTAINER_CONCENTRATION)
        if direct_dependents >= 10000:
            reasons.append(ReasonCode.MASSIVE_DOWNSTREAM_BLAST_RADIUS)
        if is_deprecated:
            reasons.append(ReasonCode.DEPRECATION_OR_DISCONTINUATION)

        if is_deprecated:
            score = 98.0
            directive = Directive.MIGRATE_WITHIN_90_DAYS
            confidence = 0.99
            return score, directive, confidence, reasons

        raw_score = ((0.55 * s_factor) + (0.45 * c_factor)) * r_weight * 50.0
        score = min(100.0, max(0.0, round(raw_score, 2)))

        if score >= 75.0:
            directive = Directive.FORK_AND_PIN if direct_dependents >= 5000 else Directive.MIGRATE_WITHIN_90_DAYS
            confidence = 0.92
        elif score >= 50.0:
            directive = Directive.VENDOR_PACKAGE if maintainer_count <= 1 else Directive.ADD_SECONDARY_IMPLEMENTATION
            confidence = 0.88
        else:
            directive = Directive.MAINTAINER_HEALTHY
            confidence = 0.95
            reasons.append(ReasonCode.RELEASE_CADENCE_HEALTHY)

        return score, directive, confidence, list(set(reasons))
