from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class MutationOperator(Enum):
    """Standardized mutation operators across frameworks"""

    ARITHMETIC_REPLACEMENT = "ARITHMETIC"
    BOUNDARY_CONDITION = "BOUNDARY"
    CONDITIONAL_REPLACEMENT = "CONDITIONAL"
    NEGATE_CONDITIONAL = "NEGATE"
    RETURN_VALUE_REPLACEMENT = "RETURN"
    REMOVE_CONDITIONAL = "REMOVE_COND"
    VOID_METHOD_CALL = "VOID_CALL"
    INCREMENT_DECREMENT = "INCREMENT"
    LOGICAL_OPERATOR = "LOGICAL"
    FRAMEWORK_SPECIFIC = "OTHER"


class MutantStatus(Enum):
    """Execution status of a mutant"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    KILLED = "KILLED"
    SURVIVED = "SURVIVED"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


@dataclass
class CodeLocation:
    """Represents a location in source code"""

    file_path: str
    line_start: int
    line_end: int
    column_start: int
    column_end: int

    def __str__(self):
        return f"{self.file_path}:{self.line_start}:{self.column_start}"


@dataclass
class CodeMetrics:
    """Complexity and quality metrics for code containing mutant"""

    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    nesting_depth: int = 0
    lines_of_code: int = 0
    number_of_parameters: int = 0
    is_public_api: bool = False
    is_security_critical: bool = False
    last_modified_days_ago: int = 999


@dataclass
class HistoricalData:
    """Historical effectiveness data for mutation operator"""

    operator: MutationOperator
    times_generated: int = 0
    times_killed: int = 0
    times_survived: int = 0
    average_detection_time: float = 0.0

    @property
    def kill_rate(self) -> float:
        """Calculate historical kill rate (0.0 to 1.0)"""
        total = self.times_killed + self.times_survived
        if total == 0:
            return 0.5  # Default for unknown operators
        return self.times_killed / total


@dataclass
class Mutant:
    """Represents a single mutant"""

    # Identification
    id: str
    framework_id: str  # Original ID from PIT/Stryker

    # Location
    location: CodeLocation

    # Mutation details
    operator: MutationOperator
    original_code: str
    mutated_code: str
    description: str = ""

    # Execution data
    status: MutantStatus = MutantStatus.PENDING
    execution_time: float = 0.0  # seconds
    killing_tests: List[str] = None
    error_message: Optional[str] = None

    # Metrics for prioritization
    code_metrics: Optional[CodeMetrics] = None
    historical_data: Optional[HistoricalData] = None

    # Computed scores
    priority_score: float = 0.0  # 0-10 scale
    estimated_execution_time: float = 3.0  # default 3 seconds

    # Metadata
    created_at: datetime = None

    def __post_init__(self):
        if self.killing_tests is None:
            self.killing_tests = []
        if self.created_at is None:
            self.created_at = datetime.now()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Mutant):
            return False
        return self.id == other.id


@dataclass
class MutationResults:
    """Results of mutation testing run"""

    project_name: str
    total_mutants: int
    mutants_executed: int
    mutants_killed: int
    mutants_survived: int
    mutants_timeout: int
    mutants_error: int

    execution_time: float  # seconds
    time_budget: float  # seconds

    mutation_score: float  # 0-100
    estimated_full_score: float  # estimated if ran all mutants
    correlation_with_full: float  # if known

    mutants: List[Mutant]

    @property
    def time_saved_percent(self) -> float:
        """Calculate percentage of time saved"""
        if self.estimated_full_execution_time == 0:
            return 0.0
        ratio = self.execution_time / self.estimated_full_execution_time
        return (1 - ratio) * 100

    @property
    def estimated_full_execution_time(self) -> float:
        """Estimate how long full testing would take"""
        if self.mutants_executed == 0:
            return 0.0
        avg_time_per_mutant = self.execution_time / self.mutants_executed
        return avg_time_per_mutant * self.total_mutants
