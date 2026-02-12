from typing import Dict, Set, List
from ..models import Mutant
import hashlib


class CoverageMapper:
    """
    Maps mutants to the set of tests that cover them.

    This is a simplified implementation for undergraduate level.
    In production, this would integrate with actual coverage tools.
    """

    def __init__(self):
        self._cache: Dict[str, Set[str]] = {}

    def map_mutant_coverage(self, mutants: List[Mutant]) -> Dict[str, Set[str]]:
        """
        Generate test coverage mapping for mutants.

        Args:
            mutants: List of mutants to analyze

        Returns:
            Dict mapping mutant_id -> set of test names that cover it
        """
        coverage_map = {}

        for mutant in mutants:
            coverage_map[mutant.id] = self._estimate_coverage(mutant)

        return coverage_map

    def _estimate_coverage(self, mutant: Mutant) -> Set[str]:
        """
        Estimate which tests cover this mutant.

        Real implementation would:
        1. Parse test execution traces
        2. Match stack traces to mutant locations
        3. Build coverage matrix

        Simplified implementation:
        - Use file path and line number as proxy
        - Generate deterministic test set based on location
        """
        # Check cache
        cache_key = f"{mutant.location.file_path}:{mutant.location.line_start}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Generate deterministic test set based on location
        # This simulates coverage analysis
        test_set = self._generate_test_set(mutant)

        self._cache[cache_key] = test_set
        return test_set

    @staticmethod
    def _generate_test_set(mutant: Mutant) -> Set[str]:
        """
        Generate a deterministic set of test names for this mutant.

        Uses hash of location to create consistent test assignments.
        """
        # Create hash from location
        location_str = f"{mutant.location.file_path}:{mutant.location.line_start}"
        hash_value = int(hashlib.md5(location_str.encode()).hexdigest(), 16)

        # Generate 3-8 test names based on hash
        num_tests = 3 + (hash_value % 6)

        test_names = set()
        for i in range(num_tests):
            # Create test name
            test_hash = (hash_value + i) % 1000
            test_name = f"test_{mutant.location.file_path.replace('/', '_').replace('.', '_')}_{test_hash}"
            test_names.add(test_name)

        return test_names

    def load_actual_coverage(self, coverage_data: Dict[str, Set[str]]):
        """
        Load actual coverage data from external source.

        Args:
            coverage_data: Dict mapping location -> set of test names
        """
        self._cache.update(coverage_data)

    @staticmethod
    def compute_similarity(tests1: Set[str], tests2: Set[str]) -> float:
        """
        Compute Jaccard similarity between two test sets.

        Similarity = |A ∩ B| / |A ∪ B|

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not tests1 and not tests2:
            return 1.0

        if not tests1 or not tests2:
            return 0.0

        intersection = len(tests1.intersection(tests2))
        union = len(tests1.union(tests2))

        return intersection / union if union > 0 else 0.0