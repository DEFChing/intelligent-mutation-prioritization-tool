from typing import List, Dict, Set
from collections import defaultdict
from ..models import Mutant, MutationOperator


class MutantClusterer:
    """
    Clusters similar mutants together for efficient subsumption analysis.

    Uses hierarchical clustering based on:
    - File location
    - Line proximity
    - Operator type
    """

    def __init__(self, proximity_threshold: int = 10):
        """
        Args:
            proximity_threshold: Max line distance for same cluster
        """
        self.proximity_threshold = proximity_threshold

    def cluster(self, mutants: List[Mutant]) -> Dict[str, List[Mutant]]:
        """
        Cluster mutants into groups.

        Returns:
            Dict mapping cluster_id -> list of mutants in cluster
        """
        # First level: Group by file
        file_groups = defaultdict(list)
        for mutant in mutants:
            file_groups[mutant.location.file_path].append(mutant)

        # Second level: Group by line proximity within each file
        clusters = {}
        cluster_id = 0

        for file_path, file_mutants in file_groups.items():
            # Sort by line number
            file_mutants.sort(key=lambda m: m.location.line_start)

            # Create clusters based on proximity
            current_cluster = []
            last_line = -999

            for mutant in file_mutants:
                if mutant.location.line_start - last_line > self.proximity_threshold:
                    # Start new cluster
                    if current_cluster:
                        clusters[f"cluster_{cluster_id}"] = current_cluster
                        cluster_id += 1
                    current_cluster = [mutant]
                else:
                    # Add to current cluster
                    current_cluster.append(mutant)

                last_line = mutant.location.line_start

            # Add final cluster
            if current_cluster:
                clusters[f"cluster_{cluster_id}"] = current_cluster
                cluster_id += 1

        return clusters

    @staticmethod
    def select_representatives(clusters: Dict[str, List[Mutant]]) -> List[Mutant]:
        """
        Select one representative mutant from each cluster.

        Strategy: Choose mutant with the highest priority score

        Returns:
            List of representative mutants
        """
        representatives = []

        for cluster_id, cluster_mutants in clusters.items():
            if not cluster_mutants:
                continue

            # Select mutant with the highest priority
            best = max(cluster_mutants, key=lambda m: m.priority_score)
            representatives.append(best)

        return representatives

    @staticmethod
    def analyze_cluster_diversity(clusters: Dict[str, List[Mutant]]) -> Dict:
        """
        Analyze diversity within clusters.

        Returns statistics about cluster composition.
        """
        stats = {
            'total_clusters': len(clusters),
            'avg_cluster_size': 0,
            'max_cluster_size': 0,
            'operator_diversity': defaultdict(int)
        }

        sizes = []
        for cluster_mutants in clusters.values():
            sizes.append(len(cluster_mutants))

            # Count operator types
            for mutant in cluster_mutants:
                stats['operator_diversity'][mutant.operator.value] += 1

        if sizes:
            stats['avg_cluster_size'] = sum(sizes) / len(sizes)
            stats['max_cluster_size'] = max(sizes)

        return stats