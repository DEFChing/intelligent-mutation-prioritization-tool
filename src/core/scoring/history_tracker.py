import json
from typing import Dict
from pathlib import Path
from ..models import MutationOperator, HistoricalData, Mutant


class HistoryTracker:
    """
    Tracks historical effectiveness of mutation operators.

    Stores data in JSON format:
    {
        "ARITHMETIC": {"generated": 150, "killed": 120, "survived": 30},
        "BOUNDARY": {"generated": 80, "killed": 75, "survived": 5},
        ...
    }
    """

    def __init__(self, history_file: str = "mutation_history.json"):
        self.history_file = Path(history_file)
        self.data: Dict[str, HistoricalData] = {}
        self._load()

    def _load(self):
        """Load historical data from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    raw_data = json.load(f)

                # Convert to HistoricalData objects
                for op_name, stats in raw_data.items():
                    try:
                        operator = MutationOperator(op_name)
                        self.data[op_name] = HistoricalData(
                            operator=operator,
                            times_generated=stats.get('generated', 0),
                            times_killed=stats.get('killed', 0),
                            times_survived=stats.get('survived', 0),
                            average_detection_time=stats.get('avg_time', 0.0)
                        )
                    except ValueError:
                        # Skip invalid operators
                        continue

            except Exception as e:
                print(f"Warning: Could not load history file: {e}")
                self._initialize_defaults()
        else:
            self._initialize_defaults()

    def _initialize_defaults(self):
        """Initialize with default values based on literature"""
        # These are typical effectiveness rates from mutation testing research
        defaults = {
            MutationOperator.ARITHMETIC_REPLACEMENT: (100, 75, 25),  # 75% kill rate
            MutationOperator.BOUNDARY_CONDITION: (100, 85, 15),  # 85% kill rate
            MutationOperator.CONDITIONAL_REPLACEMENT: (100, 70, 30),  # 70% kill rate
            MutationOperator.NEGATE_CONDITIONAL: (100, 80, 20),  # 80% kill rate
            MutationOperator.RETURN_VALUE_REPLACEMENT: (100, 65, 35),  # 65% kill rate
            MutationOperator.REMOVE_CONDITIONAL: (100, 60, 40),  # 60% kill rate
            MutationOperator.INCREMENT_DECREMENT: (100, 72, 28),  # 72% kill rate
            MutationOperator.LOGICAL_OPERATOR: (100, 78, 22),  # 78% kill rate
            MutationOperator.VOID_METHOD_CALL: (100, 45, 55),  # 45% kill rate
        }

        for operator, (gen, kill, surv) in defaults.items():
            self.data[operator.value] = HistoricalData(
                operator=operator,
                times_generated=gen,
                times_killed=kill,
                times_survived=surv,
                average_detection_time=3.0
            )

    def get_operator_history(self, operator: MutationOperator) -> HistoricalData:
        """
        Get historical data for a mutation operator.

        Args:
            operator: Mutation operator type

        Returns:
            HistoricalData object (default if not found)
        """
        if operator.value in self.data:
            return self.data[operator.value]

        # Return default for unknown operator
        return HistoricalData(
            operator=operator,
            times_generated=10,
            times_killed=5,
            times_survived=5,
            average_detection_time=3.0
        )

    def update(self, mutants: list[Mutant]):
        """
        Update history based on mutation test results.

        Args:
            mutants: List of executed mutants with results
        """
        from ..models import MutantStatus

        for mutant in mutants:
            op_key = mutant.operator.value

            if op_key not in self.data:
                self.data[op_key] = HistoricalData(
                    operator=mutant.operator,
                    times_generated=0,
                    times_killed=0,
                    times_survived=0,
                    average_detection_time=0.0
                )

            hist = self.data[op_key]
            hist.times_generated += 1

            if mutant.status == MutantStatus.KILLED:
                hist.times_killed += 1
                # Update average detection time
                total_time = hist.average_detection_time * (hist.times_killed - 1)
                hist.average_detection_time = (total_time + mutant.execution_time) / hist.times_killed

            elif mutant.status == MutantStatus.SURVIVED:
                hist.times_survived += 1

    def save(self):
        """Save historical data to file"""
        try:
            # Convert to JSON-serializable format
            data_dict = {}
            for op_key, hist in self.data.items():
                data_dict[op_key] = {
                    'generated': hist.times_generated,
                    'killed': hist.times_killed,
                    'survived': hist.times_survived,
                    'avg_time': hist.average_detection_time
                }

            with open(self.history_file, 'w') as f:
                json.dump(data_dict, f, indent=2)

        except Exception as e:
            print(f"Error saving history: {e}")

    def get_stats_summary(self) -> Dict:
        """Get summary statistics of all operators"""
        return {
            op_key: {
                'kill_rate': hist.kill_rate,
                'total_executions': hist.times_killed + hist.times_survived,
                'avg_time': hist.average_detection_time
            }
            for op_key, hist in self.data.items()
        }