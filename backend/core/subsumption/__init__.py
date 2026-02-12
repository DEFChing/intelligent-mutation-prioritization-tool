"""
Subsumption Analysis Module

Four-stage redundancy elimination pipeline:
1. Exact duplicate removal
2. Location-based clustering
3. Operator-level subsumption
4. Coverage-based subsumption

Target: 40-60% mutant reduction without losing fault-detection capability.
"""

from core.subsumption.analyzer import SubsumptionAnalyzer
from core.subsumption.coverage_mapper import CoverageMapper
from core.subsumption.mutant_clusterer import MutantClusterer

__all__ = [
    'SubsumptionAnalyzer',
    'CoverageMapper',
    'MutantClusterer',
]