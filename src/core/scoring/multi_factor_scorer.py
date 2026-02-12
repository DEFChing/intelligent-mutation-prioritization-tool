from typing import List, Dict
import math
from src.core.scoring.history_tracker import HistoryTracker
from src.core.scoring.code_analyzer import CodeAnalyzer
from ..models import Mutant, MutationOperator, CodeMetrics, HistoricalData


class MultiFactorScorer:
    """
    Scores mutants based on multiple factors to prioritize execution.

    Scoring Formula:
    priority_score = Σ(weight_i × normalized_factor_i)

    Factors:
    1. Historical Effectiveness (30%)
    2. Code Complexity (25%)
    3. Security Criticality (20%)
    4. Change Recency (15%)
    5. Bug History (10%)
    """

    # Configurable weights
    WEIGHTS = {
        'historical': 0.30,
        'complexity': 0.25,
        'security': 0.20,
        'recency': 0.15,
        'bug_history': 0.10
    }

    def __init__(self,
                 history_tracker: 'HistoryTracker' = None,
                 code_analyzer: 'CodeAnalyzer' = None):
        """
        Initialize scorer with dependencies.

        Args:
            history_tracker: Tracks historical mutation effectiveness
            code_analyzer: Analyzes code complexity and metrics
        """
        self.history_tracker = history_tracker or HistoryTracker()
        self.code_analyzer = code_analyzer or CodeAnalyzer()

        # Cache for computed metrics
        self._metrics_cache: Dict[str, CodeMetrics] = {}

    def score_all(self, mutants: List[Mutant]) -> List[Mutant]:
        """
        Score all mutants and return sorted by priority (descending).

        Args:
            mutants: List of mutants to score

        Returns:
            Same list with priority_score populated, sorted by score
        """
        # Step 1: Gather metrics for all mutants
        self._precompute_metrics(mutants)

        # Step 2: Normalize factors across all mutants
        normalized_factors = self._compute_normalized_factors(mutants)

        # Step 3: Calculate weighted scores
        for mutant in mutants:
            mutant.priority_score = self._calculate_weighted_score(
                mutant,
                normalized_factors
            )

        # Step 4: Sort by priority (highest first)
        mutants.sort(key=lambda m: m.priority_score, reverse=True)

        return mutants

    def score_single(self, mutant: Mutant, context: List[Mutant] = None) -> float:
        """
        Score a single mutant (useful for incremental scoring).

        Args:
            mutant: Mutant to score
            context: Other mutants for normalization context (optional)

        Returns:
            Priority score (0-10)
        """
        if context:
            return self.score_all([mutant] + context)[0].priority_score

        # Standalone scoring without context
        self._precompute_metrics([mutant])
        factors = self._compute_factors_single(mutant)
        return self._weighted_sum(factors)

    def _precompute_metrics(self, mutants: List[Mutant]):
        """Precompute code metrics for all mutants"""
        for mutant in mutants:
            if mutant.location.file_path not in self._metrics_cache:
                # Analyze file once, cache results
                file_metrics = self.code_analyzer.analyze_file(
                    mutant.location.file_path
                )
                self._metrics_cache[mutant.location.file_path] = file_metrics

            # Attach relevant metrics to mutant
            mutant.code_metrics = self._metrics_cache[mutant.location.file_path]

            # Get historical data for operator type
            mutant.historical_data = self.history_tracker.get_operator_history(
                mutant.operator
            )

    def _compute_normalized_factors(self, mutants: List[Mutant]) -> Dict[str, Dict[str, float]]:
        """
        Compute and normalize all factors across mutants.

        Returns:
            Dict mapping mutant.id -> {factor_name: normalized_value}
        """
        # Extract raw factor values
        raw_factors = {
            'historical': [self._historical_factor(m) for m in mutants],
            'complexity': [self._complexity_factor(m) for m in mutants],
            'security': [self._security_factor(m) for m in mutants],
            'recency': [self._recency_factor(m) for m in mutants],
            'bug_history': [self._bug_history_factor(m) for m in mutants]
        }

        # Normalize each factor using min-max scaling
        normalized = {}
        for factor_name, values in raw_factors.items():
            min_val = min(values)
            max_val = max(values)

            # Avoid division by zero
            if max_val - min_val == 0:
                normalized[factor_name] = [0.5] * len(values)
            else:
                normalized[factor_name] = [
                    (v - min_val) / (max_val - min_val)
                    for v in values
                ]

        # Build per-mutant dictionary
        result = {}
        for i, mutant in enumerate(mutants):
            result[mutant.id] = {
                factor: normalized[factor][i]
                for factor in raw_factors.keys()
            }

        return result

    def _calculate_weighted_score(self,
                                  mutant: Mutant,
                                  normalized: Dict[str, Dict[str, float]]) -> float:
        """
        Calculate weighted sum of normalized factors.

        Returns:
            Score on 0-10 scale
        """
        factors = normalized[mutant.id]

        weighted_sum = sum(
            self.WEIGHTS[factor] * factors[factor]
            for factor in factors.keys()
        )

        # Scale to 0-10
        return weighted_sum * 10.0

    def _weighted_sum(self, factors: Dict[str, float]) -> float:
        """Calculate weighted sum (for standalone scoring)"""
        return sum(
            self.WEIGHTS[key] * value
            for key, value in factors.items()
        ) * 10.0

    # ============= FACTOR COMPUTATION FUNCTIONS =============

    @staticmethod
    def _historical_factor(mutant: Mutant) -> float:
        """
        Historical effectiveness factor.

        Returns kill rate of this operator type (0.0-1.0).
        Higher = more likely to be caught by tests.
        """
        if not mutant.historical_data:
            return 0.5  # Default for unknown

        return mutant.historical_data.kill_rate

    @staticmethod
    def _complexity_factor(mutant: Mutant) -> float:
        """
        Code complexity factor.

        Higher complexity = higher priority (more likely to have bugs).

        Returns:
            Composite complexity score (0.0-1.0+)
        """
        if not mutant.code_metrics:
            return 0.5

        metrics = mutant.code_metrics

        # Weighted complexity formula
        complexity_score = (
                0.4 * min(metrics.cyclomatic_complexity / 20.0, 1.0) +
                0.3 * min(metrics.cognitive_complexity / 30.0, 1.0) +
                0.2 * min(metrics.nesting_depth / 5.0, 1.0) +
                0.1 * min(metrics.number_of_parameters / 8.0, 1.0)
        )

        return complexity_score

    @staticmethod
    def _security_factor(mutant: Mutant) -> float:
        """
        Security criticality factor.

        Returns:
            1.0 if security-critical, 0.3 if public API, 0.0 otherwise
        """
        if not mutant.code_metrics:
            return 0.0

        if mutant.code_metrics.is_security_critical:
            return 1.0
        elif mutant.code_metrics.is_public_api:
            return 0.3
        else:
            return 0.0

    @staticmethod
    def _recency_factor(mutant: Mutant) -> float:
        """
        Code change recency factor.

        More recent changes = higher priority (more likely to have bugs).

        Returns:
            Exponential decay: 1.0 for today, ~0.1 for 30+ days ago
        """
        if not mutant.code_metrics:
            return 0.0

        days = mutant.code_metrics.last_modified_days_ago

        # Exponential decay: e^(-days/10)
        return math.exp(-days / 10.0)

    def _bug_history_factor(self, mutant: Mutant) -> float:
        """
        Bug history factor.

        Files with more historical bugs get higher priority.

        Returns:
            0.0-1.0 based on bug density
        """
        # This would query a bug tracking system
        # For now, stub implementation
        bug_count = self.code_analyzer.get_historical_bug_count(
            mutant.location.file_path
        )

        # Normalize: 0 bugs = 0.0, 10+ bugs = 1.0
        return min(bug_count / 10.0, 1.0)

    def _compute_factors_single(self, mutant: Mutant) -> Dict[str, float]:
        """Compute raw factors for single mutant (standalone mode)"""
        return {
            'historical': self._historical_factor(mutant),
            'complexity': self._complexity_factor(mutant),
            'security': self._security_factor(mutant),
            'recency': self._recency_factor(mutant),
            'bug_history': self._bug_history_factor(mutant)
        }

    def explain_score(self, mutant: Mutant) -> Dict[str, any]:
        """
        Generate human-readable explanation of score.

        Returns:
            Dictionary with score breakdown and justification
        """
        factors = self._compute_factors_single(mutant)

        return {
            'mutant_id': mutant.id,
            'final_score': mutant.priority_score,
            'breakdown': {
                'historical_effectiveness': {
                    'raw_value': factors['historical'],
                    'weighted_contribution': factors['historical'] * self.WEIGHTS['historical'] * 10,
                    'explanation': f"Kill rate: {factors['historical']:.1%}"
                },
                'code_complexity': {
                    'raw_value': factors['complexity'],
                    'weighted_contribution': factors['complexity'] * self.WEIGHTS['complexity'] * 10,
                    'explanation': f"Cyclomatic: {mutant.code_metrics.cyclomatic_complexity if mutant.code_metrics else 'N/A'}"
                },
                'security_criticality': {
                    'raw_value': factors['security'],
                    'weighted_contribution': factors['security'] * self.WEIGHTS['security'] * 10,
                    'explanation': "Security-critical code" if factors['security'] > 0.5 else "Non-critical"
                },
                'change_recency': {
                    'raw_value': factors['recency'],
                    'weighted_contribution': factors['recency'] * self.WEIGHTS['recency'] * 10,
                    'explanation': f"Modified {mutant.code_metrics.last_modified_days_ago if mutant.code_metrics else '?'} days ago"
                },
                'bug_history': {
                    'raw_value': factors['bug_history'],
                    'weighted_contribution': factors['bug_history'] * self.WEIGHTS['bug_history'] * 10,
                    'explanation': f"Historical bugs in file"
                }
            }
        }