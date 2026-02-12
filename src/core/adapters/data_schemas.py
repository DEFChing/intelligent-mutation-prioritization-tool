from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json

from enum import Enum


class FrameworkType(Enum):
    """Supported mutation testing frameworks"""
    PIT = "PIT"
    STRYKER = "Stryker"


@dataclass
class StandardMutantReport:
    """
    Standardized mutant report format.

    Both PIT and Stryker adapters convert their outputs to this format.
    """
    mutant_id: str
    file_path: str
    line_number: int
    column_number: int
    operator_type: str
    original_code: str
    mutated_code: str
    status: str  # "KILLED", "SURVIVED", "TIMEOUT", "ERROR"
    execution_time_ms: float
    killing_test: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> 'StandardMutantReport':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class StandardTestResult:
    """Standardized test execution result"""
    test_name: str
    passed: bool
    execution_time_ms: float
    mutants_killed: List[str]  # List of mutant IDs killed by this test
    error_message: Optional[str] = None


@dataclass
class StandardProjectMetadata:
    """Standardized project metadata"""
    project_name: str
    language: str
    framework: str  # "PIT" or "Stryker"
    source_files: List[str]
    test_files: List[str]
    lines_of_code: int
    test_count: int


@dataclass
class AdapterConfiguration:
    """
    Configuration for framework adapters.

    Common settings that apply to both PIT and Stryker.
    """
    # Execution settings
    timeout_per_mutant_seconds: float = 5.0
    max_parallel_threads: int = 4
    fail_fast: bool = False  # Stop on first error

    # Output settings
    verbose: bool = True
    generate_html_report: bool = True
    export_json: bool = True

    # Mutation settings
    exclude_patterns: List[str] = None  # e.g., ["*Test.java", "*.spec.js"]
    include_patterns: List[str] = None

    # Framework-specific settings (stored as dict for flexibility)
    framework_options: Dict = None

    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        if self.include_patterns is None:
            self.include_patterns = []
        if self.framework_options is None:
            self.framework_options = {}

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_file(cls, config_file: str) -> 'AdapterConfiguration':
        """Load configuration from JSON file"""
        with open(config_file, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def save_to_file(self, config_file: str):
        """Save configuration to JSON file"""
        with open(config_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)