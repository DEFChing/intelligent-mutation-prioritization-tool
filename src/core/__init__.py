"""
Core modules for the IMPT system.

This package contains the fundamental components:
- models: Data structures and type definitions
- scoring: Multi-factor prioritization engine
- subsumption: Redundancy elimination algorithms
- adapters: Framework integration interfaces
- optimization: Time-budget optimization (coming soon)
"""

from src.core import models
from src.core.scoring import MultiFactorScorer
from src.core.subsumption import SubsumptionAnalyzer
from src.core.adapters import AdapterFactory

__all__ = [
    'models',
    'MultiFactorScorer',
    'SubsumptionAnalyzer',
    'AdapterFactory',
]