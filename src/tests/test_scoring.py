# File: src/tests/test_scoring.py

import pytest
from src.core.models import Mutant, MutationOperator, CodeLocation, CodeMetrics, HistoricalData
from src.core.scoring.multi_factor_scorer import MultiFactorScorer
from src.core.scoring.history_tracker import HistoryTracker


class TestMultiFactorScorer:

    def test_score_all_basic(self):
        """Test basic scoring of multiple mutants"""
        mutants = [
            Mutant(
                id="m1",
                framework_id="pit_1",
                location=CodeLocation("test.py", 10, 10, 0, 10),
                operator=MutationOperator.ARITHMETIC_REPLACEMENT,
                original_code="a + b",
                mutated_code="a - b",
                code_metrics=CodeMetrics(cyclomatic_complexity=5),
                historical_data=HistoricalData(
                    operator=MutationOperator.ARITHMETIC_REPLACEMENT,
                    times_generated=100,
                    times_killed=80,
                    times_survived=20
                )
            ),
            Mutant(
                id="m2",
                framework_id="pit_2",
                location=CodeLocation("test.py", 20, 20, 0, 10),
                operator=MutationOperator.BOUNDARY_CONDITION,
                original_code="x < 10",
                mutated_code="x <= 10",
                code_metrics=CodeMetrics(cyclomatic_complexity=15),
                historical_data=HistoricalData(
                    operator=MutationOperator.BOUNDARY_CONDITION,
                    times_generated=100,
                    times_killed=90,
                    times_survived=10
                )
            )
        ]

        scorer = MultiFactorScorer()
        scored = scorer.score_all(mutants)

        # Verify scores assigned
        assert scored[0].priority_score > 0
        assert scored[1].priority_score > 0

        # Verify sorted by priority (descending)
        assert scored[0].priority_score >= scored[1].priority_score

    def test_historical_factor(self):
        """Test historical effectiveness factor"""
        scorer = MultiFactorScorer()

        mutant = Mutant(
            id="m1",
            framework_id="test_1",
            location=CodeLocation("test.py", 1, 1, 0, 1),
            operator=MutationOperator.ARITHMETIC_REPLACEMENT,
            original_code="x",
            mutated_code="y",
            historical_data=HistoricalData(
                operator=MutationOperator.ARITHMETIC_REPLACEMENT,
                times_generated=100,
                times_killed=75,
                times_survived=25
            )
        )

        factor = scorer._historical_factor(mutant)
        assert factor == 0.75  # 75% kill rate

    def test_complexity_factor(self):
        """Test code complexity factor"""
        scorer = MultiFactorScorer()

        mutant = Mutant(
            id="m1",
            framework_id="test_1",
            location=CodeLocation("test.py", 1, 1, 0, 1),
            operator=MutationOperator.ARITHMETIC_REPLACEMENT,
            original_code="x",
            mutated_code="y",
            code_metrics=CodeMetrics(
                cyclomatic_complexity=20,
                cognitive_complexity=30,
                nesting_depth=5,
                number_of_parameters=8
            )
        )

        factor = scorer._complexity_factor(mutant)
        assert 0 <= factor <= 1.5  # Can exceed 1.0 for very complex code

    def test_score_explanation(self):
        """Test score explanation generation"""
        scorer = MultiFactorScorer()

        mutant = Mutant(
            id="m1",
            framework_id="test_1",
            location=CodeLocation("test.py", 1, 1, 0, 1),
            operator=MutationOperator.ARITHMETIC_REPLACEMENT,
            original_code="x + y",
            mutated_code="x - y",
            priority_score=7.5,
            code_metrics=CodeMetrics(cyclomatic_complexity=10),
            historical_data=HistoricalData(
                operator=MutationOperator.ARITHMETIC_REPLACEMENT,
                times_generated=100,
                times_killed=80,
                times_survived=20
            )
        )

        explanation = scorer.explain_score(mutant)

        assert 'mutant_id' in explanation
        assert 'final_score' in explanation
        assert 'breakdown' in explanation
        assert 'historical_effectiveness' in explanation['breakdown']


class TestHistoryTracker:

    def test_load_defaults(self):
        """Test that default history loads correctly"""
        tracker = HistoryTracker(history_file="test_history.json")

        hist = tracker.get_operator_history(MutationOperator.ARITHMETIC_REPLACEMENT)
        assert hist.kill_rate > 0

    def test_update_history(self):
        """Test updating history with new results"""
        tracker = HistoryTracker(history_file="test_history.json")

        from src.core.models import MutantStatus

        mutant = Mutant(
            id="m1",
            framework_id="test_1",
            location=CodeLocation("test.py", 1, 1, 0, 1),
            operator=MutationOperator.ARITHMETIC_REPLACEMENT,
            original_code="x",
            mutated_code="y",
            status=MutantStatus.KILLED,
            execution_time=2.5
        )

        tracker.update([mutant])

        hist = tracker.get_operator_history(MutationOperator.ARITHMETIC_REPLACEMENT)
        assert hist.times_killed > 0