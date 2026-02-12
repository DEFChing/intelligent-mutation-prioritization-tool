import pytest
from core.models import Mutant, MutationOperator, CodeLocation
from core.subsumption.analyzer import SubsumptionAnalyzer


class TestSubsumptionAnalyzer:

    def test_remove_exact_duplicates(self):
        """Test duplicate removal"""
        mutants = [
            Mutant(
                id="m1", framework_id="1",
                location=CodeLocation("test.py", 10, 10, 0, 5),
                operator=MutationOperator.ARITHMETIC_REPLACEMENT,
                original_code="a + b",
                mutated_code="a - b"
            ),
            Mutant(
                id="m2", framework_id="2",
                location=CodeLocation("test.py", 10, 10, 0, 5),
                operator=MutationOperator.ARITHMETIC_REPLACEMENT,
                original_code="a + b",
                mutated_code="a - b"  # Exact duplicate
            ),
            Mutant(
                id="m3", framework_id="3",
                location=CodeLocation("test.py", 20, 20, 0, 5),
                operator=MutationOperator.BOUNDARY_CONDITION,
                original_code="x < 10",
                mutated_code="x <= 10"
            )
        ]

        analyzer = SubsumptionAnalyzer()
        unique = analyzer._remove_exact_duplicates(mutants)

        assert len(unique) == 2  # m2 should be removed
        assert analyzer.stats['exact_duplicates'] == 1

    def test_location_clustering(self):
        """Test location-based clustering"""
        mutants = [
            Mutant(
                id="m1", framework_id="1",
                location=CodeLocation("test.py", 10, 10, 0, 5),
                operator=MutationOperator.ARITHMETIC_REPLACEMENT,
                original_code="a + b", mutated_code="a - b",
                priority_score=8.0
            ),
            Mutant(
                id="m2", framework_id="2",
                location=CodeLocation("test.py", 10, 10, 0, 5),  # Same location
                operator=MutationOperator.BOUNDARY_CONDITION,
                original_code="x < 10", mutated_code="x <= 10",
                priority_score=6.0
            )
        ]

        analyzer = SubsumptionAnalyzer()
        clustered = analyzer._cluster_by_location(mutants)

        # Should keep m1 (higher priority)
        assert len(clustered) == 1
        assert clustered[0].id == "m1"