"""
Framework Adapter Layer

Provides language-agnostic integration with mutation testing frameworks:
- PIT (Java) - Coming in April 2026
- Stryker (JavaScript/TypeScript) - Coming in April 2026

Current Status: Base adapter interface implemented (5% of system)
"""

from src.core.adapters.base_adapter import MutationFrameworkAdapter
from src.core.adapters.data_schemas import (
    StandardMutantReport,
    AdapterConfiguration,
    FrameworkType
)
from src.core.adapters.adapter_factory import AdapterFactory

__all__ = [
    'MutationFrameworkAdapter',
    'StandardMutantReport',
    'AdapterConfiguration',
    'FrameworkType',
    'AdapterFactory',
]