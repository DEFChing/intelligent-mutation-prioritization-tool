import ast
import os
from typing import Dict
from ..models import CodeMetrics


class CodeAnalyzer:
    """
    Analyzes source code to extract complexity metrics and metadata.

    Supports: Python, Java (basic), JavaScript (basic)
    """

    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self._file_cache: Dict[str, CodeMetrics] = {}
        self._bug_history: Dict[str, int] = {}  # file -> bug count

    def analyze_file(self, file_path: str) -> CodeMetrics:
        """
        Analyze a source file and return complexity metrics.

        Args:
            file_path: Path to source file

        Returns:
            CodeMetrics object with computed metrics
        """
        # Check cache
        if file_path in self._file_cache:
            return self._file_cache[file_path]

        # Determine language
        ext = os.path.splitext(file_path)[1]

        if ext == '.py':
            metrics = self._analyze_python(file_path)
        elif ext in ['.java']:
            metrics = self._analyze_java(file_path)
        elif ext in ['.js', '.ts']:
            metrics = self._analyze_javascript()
        else:
            # Default metrics for unknown languages
            metrics = CodeMetrics()

        # Cache and return
        self._file_cache[file_path] = metrics
        return metrics

    def _analyze_python(self, file_path: str) -> CodeMetrics:
        """Analyze Python file using AST"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)

            # Calculate metrics
            visitor = PythonMetricsVisitor()
            visitor.visit(tree)

            return CodeMetrics(
                cyclomatic_complexity=visitor.cyclomatic_complexity,
                cognitive_complexity=visitor.cognitive_complexity,
                nesting_depth=visitor.max_nesting_depth,
                lines_of_code=len(source.splitlines()),
                number_of_parameters=visitor.max_parameters,
                is_public_api=visitor.has_public_methods,
                is_security_critical=self._detect_security_patterns(source),
                last_modified_days_ago=self._get_file_age(file_path)
            )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return CodeMetrics()

    def _analyze_java(self, file_path: str) -> CodeMetrics:
        """Basic Java analysis (simplified for undergraduate level)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # Simple heuristic-based analysis
            lines = source.splitlines()

            # Count control flow statements for cyclomatic complexity
            control_keywords = ['if', 'else', 'while', 'for', 'case', 'catch']
            complexity = 1  # Base complexity
            for line in lines:
                for keyword in control_keywords:
                    complexity += line.count(f' {keyword} ') + line.count(f' {keyword}(')

            # Detect nesting depth
            max_depth = 0
            current_depth = 0
            for line in lines:
                current_depth += line.count('{') - line.count('}')
                max_depth = max(max_depth, current_depth)

            return CodeMetrics(
                cyclomatic_complexity=complexity,
                cognitive_complexity=complexity,  # Approximation
                nesting_depth=max_depth,
                lines_of_code=len([l for l in lines if l.strip()]),
                is_public_api='public class' in source or 'public interface' in source,
                is_security_critical=self._detect_security_patterns(source),
                last_modified_days_ago=self._get_file_age(file_path)
            )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return CodeMetrics()

    @staticmethod
    def _analyze_javascript() -> CodeMetrics:
        """Basic JavaScript analysis"""
        # Similar heuristic approach as Java
        # Implementation omitted for brevity (similar to _analyze_java)
        return CodeMetrics()

    @staticmethod
    def _detect_security_patterns(source: str) -> bool:
        """
        Detect security-critical code patterns.

        Returns True if code contains security-related keywords.
        """
        security_keywords = [
            'password', 'auth', 'token', 'secret', 'encrypt',
            'decrypt', 'hash', 'crypto', 'ssl', 'tls', 'certificate',
            'login', 'credential', 'security', 'permission', 'access'
        ]

        source_lower = source.lower()
        return any(keyword in source_lower for keyword in security_keywords)

    @staticmethod
    def _get_file_age(file_path: str) -> int:
        """
        Get days since file was last modified.

        Returns:
            Days since modification (0 = today)
        """
        try:
            from datetime import datetime
            mod_time = os.path.getmtime(file_path)
            mod_date = datetime.fromtimestamp(mod_time)
            age = (datetime.now() - mod_date).days
            return max(0, age)
        except:
            return 999  # Unknown age

    def get_historical_bug_count(self, file_path: str) -> int:
        """
        Get number of historical bugs in file.

        This would typically query a bug tracking system.
        For now, returns cached data or 0.
        """
        return self._bug_history.get(file_path, 0)

    def load_bug_history(self, bug_data: Dict[str, int]):
        """
        Load bug history data from external source.

        Args:
            bug_data: Dict mapping file_path -> bug_count
        """
        self._bug_history.update(bug_data)


class PythonMetricsVisitor(ast.NodeVisitor):
    """AST visitor to calculate Python code metrics"""

    def __init__(self):
        self.cyclomatic_complexity = 1  # Base complexity
        self.cognitive_complexity = 0
        self.max_nesting_depth = 0
        self.current_depth = 0
        self.max_parameters = 0
        self.has_public_methods = False

    def visit_FunctionDef(self, node):
        # Count parameters
        self.max_parameters = max(self.max_parameters, len(node.args.args))

        # Check if public (no leading underscore)
        if not node.name.startswith('_'):
            self.has_public_methods = True

        self.generic_visit(node)

    def visit_If(self, node):
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self._track_nesting()
        self.generic_visit(node)

    def visit_While(self, node):
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self._track_nesting()
        self.generic_visit(node)

    def visit_For(self, node):
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self._track_nesting()
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def _track_nesting(self):
        self.current_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.current_depth)