from abc import ABC, abstractmethod
from typing import List, Dict
from pathlib import Path
from ..models import Mutant, MutationResults, MutationOperator


class MutationFrameworkAdapter(ABC):
    """
    Abstract base class for mutation testing framework adapters.

    Both PIT (Java) and Stryker (JavaScript) adapters must implement this interface.
    This ensures the core engine remains framework-agnostic.
    """

    def __init__(self, project_path: str):
        """
        Initialize adapter with project path.

        Args:
            project_path: Path to the project to test
        """
        self.project_path = Path(project_path)
        self.framework_name = "UNKNOWN"

        # Validate project structure
        if not self._validate_project():
            raise ValueError(f"Invalid project structure at {project_path}")

    @abstractmethod
    def _validate_project(self) -> bool:
        """
        Validate that project structure is compatible with framework.

        Returns:
            True if project is valid, False otherwise
        """
        pass

    @abstractmethod
    def generate_mutants(self) -> List[Mutant]:
        """
        Run framework's mutant generation phase.

        This tells the framework to analyze code and generate all possible mutants
        WITHOUT executing them yet.

        Returns:
            List of all generated mutants (with status=PENDING)
        """
        pass

    @abstractmethod
    def execute_mutants(self,
                        selected_mutants: List[Mutant],
                        time_budget_seconds: float) -> List[Mutant]:
        """
        Execute specific mutants through the framework.

        Args:
            selected_mutants: Mutants chosen by prioritization engine
            time_budget_seconds: Maximum time allowed for execution

        Returns:
            Same mutants with updated status (KILLED/SURVIVED/TIMEOUT/ERROR)
        """
        pass

    @abstractmethod
    def map_mutation_operator(self, framework_operator: str) -> MutationOperator:
        """
        Map framework-specific operator name to standardized enum.

        Args:
            framework_operator: Operator name from framework (e.g., "MATH_MUTATOR" from PIT)

        Returns:
            Standardized MutationOperator enum value
        """
        pass

    @abstractmethod
    def parse_results(self, framework_output: str) -> MutationResults:
        """
        Parse framework's output into standardized MutationResults.

        Args:
            framework_output: Raw output from framework (XML, JSON, etc.)

        Returns:
            Standardized MutationResults object
        """
        pass

    @staticmethod
    def estimate_execution_time() -> float:
        """
        Estimate execution time for a single mutant.

        Default implementation: 3 seconds per mutant.
        Subclasses can override with framework-specific logic.

        Returns:
            Estimated time in seconds
        """
        return 3.0

    def get_framework_info(self) -> Dict:
        """
        Get information about the framework.

        Returns:
            Dict with framework name, version, capabilities
        """
        return {
            'name': self.framework_name,
            'version': self._get_framework_version(),
            'supported_languages': self._get_supported_languages(),
            'supported_operators': self._get_supported_operators()
        }

    @abstractmethod
    def _get_framework_version(self) -> str:
        """Get installed framework version"""
        pass

    @abstractmethod
    def _get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        pass

    @abstractmethod
    def _get_supported_operators(self) -> List[str]:
        """Get list of supported mutation operators"""
        pass

    def cleanup(self):
        """
        Clean up temporary files created during testing.

        Optional: Subclasses can override if needed.
        """
        pass