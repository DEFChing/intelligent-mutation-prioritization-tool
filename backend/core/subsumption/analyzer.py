from typing import List, Set, Dict, Tuple
from collections import defaultdict
from ..models import Mutant, MutationOperator, CodeLocation
from .coverage_mapper import CoverageMapper


class SubsumptionAnalyzer:
    """
    Identifies and eliminates redundant mutants using subsumption analysis.

    Three strategies:
    1. Exact subsumption (same location, equivalent mutations)
    2. Coverage-based subsumption (dominated coverage)
    3. Operator-level subsumption (known redundant operators)
    """

    # Known subsumption relationships from mutation testing literature
    OPERATOR_SUBSUMPTIONS = {
        # If ABS mutant is killed, these are also likely killed
        MutationOperator.ARITHMETIC_REPLACEMENT: {
            MutationOperator.INCREMENT_DECREMENT
        },
        # If boundary condition is killed, negate is often killed
        MutationOperator.BOUNDARY_CONDITION: {
            MutationOperator.NEGATE_CONDITIONAL
        },
        # Return value replacement subsumes void calls
        MutationOperator.RETURN_VALUE_REPLACEMENT: {
            MutationOperator.VOID_METHOD_CALL
        }
    }

    def __init__(self,
                 coverage_mapper: 'CoverageMapper' = None,
                 similarity_threshold: float = 0.90):
        """
        Initialize subsumption analyzer.

        Args:
            coverage_mapper: Maps mutants to test coverage
            similarity_threshold: Minimum similarity for subsumption (0-1)
        """
        self.coverage_mapper = coverage_mapper or CoverageMapper()
        self.similarity_threshold = similarity_threshold

        # Statistics
        self.stats = {
            'total_input': 0,
            'exact_duplicates': 0,
            'coverage_subsumed': 0,
            'operator_subsumed': 0,
            'location_clustered': 0,
            'total_output': 0
        }

    def filter_redundant(self, mutants: List[Mutant]) -> List[Mutant]:
        """
        Remove redundant mutants, keeping only unique/representative ones.

        Args:
            mutants: All generated mutants

        Returns:
            Filtered list of unique mutants (40-60% reduction expected)
        """
        self.stats['total_input'] = len(mutants)

        print(f"🔍 Subsumption Analysis: Processing {len(mutants)} mutants...")

        # Stage 1: Remove exact duplicates
        unique = self._remove_exact_duplicates(mutants)
        print(f"   ├─ After duplicate removal: {len(unique)} mutants")

        # Stage 2: Cluster by location
        clustered = self._cluster_by_location(unique)
        print(f"   ├─ After location clustering: {len(clustered)} mutants")

        # Stage 3: Apply operator-level subsumption
        after_operator = self._apply_operator_subsumption(clustered)
        print(f"   ├─ After operator subsumption: {len(after_operator)} mutants")

        # Stage 4: Coverage-based subsumption (most expensive)
        final = self._apply_coverage_subsumption(after_operator)
        print(f"   └─ Final unique mutants: {len(final)} mutants")

        self.stats['total_output'] = len(final)
        reduction_pct = (1 - len(final) / len(mutants)) * 100
        print(f"✅ Eliminated {len(mutants) - len(final)} redundant mutants ({reduction_pct:.1f}% reduction)")

        return final

    def _remove_exact_duplicates(self, mutants: List[Mutant]) -> List[Mutant]:
        """
        Remove mutants that are exactly identical.

        Two mutants are duplicates if they have:
        - Same location
        - Same operator
        - Same original/mutated code
        """
        seen = set()
        unique = []

        for mutant in mutants:
            # Create hash key
            key = (
                mutant.location.file_path,
                mutant.location.line_start,
                mutant.location.column_start,
                mutant.operator.value,
                mutant.original_code,
                mutant.mutated_code
            )

            if key not in seen:
                seen.add(key)
                unique.append(mutant)
            else:
                self.stats['exact_duplicates'] += 1

        return unique

    def _cluster_by_location(self, mutants: List[Mutant]) -> List[Mutant]:
        """
        Cluster mutants at the same location and keep only the most valuable.

        Strategy: For mutants at the same exact location, keep only the one
        with the highest priority score (or first if not scored yet).
        """
        # Group by exact location
        location_groups = defaultdict(list)

        for mutant in mutants:
            location_key = (
                mutant.location.file_path,
                mutant.location.line_start,
                mutant.location.column_start
            )
            location_groups[location_key].append(mutant)

        # Keep the best mutant from each location
        selected = []
        for location_key, group in location_groups.items():
            if len(group) == 1:
                selected.append(group[0])
            else:
                # Keep mutant with the highest priority or first if unscored
                best = max(group, key=lambda m: m.priority_score)
                selected.append(best)
                self.stats['location_clustered'] += len(group) - 1

        return selected

    def _apply_operator_subsumption(self, mutants: List[Mutant]) -> List[Mutant]:
        """
        Apply known operator-level subsumption rules.

        If mutant M1 subsumes M2 and both exist at nearby locations,
        remove M2.
        """
        # Group by file and approximate location
        file_groups = defaultdict(list)
        for mutant in mutants:
            file_groups[mutant.location.file_path].append(mutant)

        to_remove = set()

        for file_path, file_mutants in file_groups.items():
            # Sort by line number
            file_mutants.sort(key=lambda m: m.location.line_start)

            for i, m1 in enumerate(file_mutants):
                # Check if m1 subsumes any nearby mutants
                subsumed_ops = self.OPERATOR_SUBSUMPTIONS.get(m1.operator, set())

                if not subsumed_ops:
                    continue

                # Look for subsumed mutants within 5 lines
                for j, m2 in enumerate(file_mutants[i + 1:], start=i + 1):
                    if m2.id in to_remove:
                        continue

                    # Check line proximity
                    if abs(m2.location.line_start - m1.location.line_start) > 5:
                        break  # Too far away

                    # Check if m1 subsumes m2
                    if m2.operator in subsumed_ops:
                        to_remove.add(m2.id)
                        self.stats['operator_subsumed'] += 1

        # Filter out subsumed mutants
        return [m for m in mutants if m.id not in to_remove]

    def _apply_coverage_subsumption(self, mutants: List[Mutant]) -> List[Mutant]:
        """
        Apply coverage-based subsumption analysis.

        Mutant M1 subsumes M2 if:
        - coverage(M1) ⊇ coverage(M2) AND
        - similarity(M1, M2) >= threshold

        This is the most powerful but also most expensive analysis.
        """
        # Get test coverage for all mutants
        coverage_map = self.coverage_mapper.map_mutant_coverage(mutants)

        to_remove = set()

        # Compare each pair (O(n²) - expensive for large n)
        # For undergraduate level: simplified to only compare similar mutants
        for i, m1 in enumerate(mutants):
            if m1.id in to_remove:
                continue

            c1 = coverage_map.get(m1.id, set())

            for m2 in mutants[i + 1:]:
                if m2.id in to_remove:
                    continue

                # Quick filter: only compare if operators are related
                if not self._are_operators_related(m1.operator, m2.operator):
                    continue

                c2 = coverage_map.get(m2.id, set())

                # Check if m1 subsumes m2
                if c1.issuperset(c2) and len(c2) > 0:
                    similarity = len(c1.intersection(c2)) / len(c1.union(c2))

                    if similarity >= self.similarity_threshold:
                        # m1 subsumes m2, remove m2
                        to_remove.add(m2.id)
                        self.stats['coverage_subsumed'] += 1

        return [m for m in mutants if m.id not in to_remove]

    def _are_operators_related(self, op1: MutationOperator, op2: MutationOperator) -> bool:
        """Check if two operators are related (for coverage comparison)"""
        # Same operator type
        if op1 == op2:
            return True

        # Check subsumption relationships
        if op2 in self.OPERATOR_SUBSUMPTIONS.get(op1, set()):
            return True
        if op1 in self.OPERATOR_SUBSUMPTIONS.get(op2, set()):
            return True

        # Both are arithmetic-related
        arithmetic_ops = {
            MutationOperator.ARITHMETIC_REPLACEMENT,
            MutationOperator.INCREMENT_DECREMENT
        }
        if op1 in arithmetic_ops and op2 in arithmetic_ops:
            return True

        # Both are conditional-related
        conditional_ops = {
            MutationOperator.CONDITIONAL_REPLACEMENT,
            MutationOperator.NEGATE_CONDITIONAL,
            MutationOperator.REMOVE_CONDITIONAL,
            MutationOperator.BOUNDARY_CONDITION
        }
        if op1 in conditional_ops and op2 in conditional_ops:
            return True

        return False

    def get_statistics(self) -> Dict:
        """Get subsumption analysis statistics"""
        return {
            **self.stats,
            'reduction_percent': (1 - self.stats['total_output'] / self.stats['total_input']) * 100
            if self.stats['total_input'] > 0 else 0
        }

    @staticmethod
    def explain_removal(removed_mutant_id: str) -> str:
        """
        Generate explanation for why a mutant was removed.

        Returns human-readable justification.
        """
        # This would track removal reasons during analysis
        # Simplified for undergraduate level
        return f"Mutant {removed_mutant_id} was removed due to subsumption analysis"