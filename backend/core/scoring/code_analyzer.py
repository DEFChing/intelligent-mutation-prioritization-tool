"""
Code Analyzer for IMPT System

Analyzes source code to extract complexity metrics.
For demo purposes, uses simulated metrics based on mutant data.
"""

from core.models import Mutant, CodeMetrics
from core.scoring.complexity_metrics import (
    calculate_cyclomatic_complexity,
    calculate_cognitive_complexity,
    estimate_halstead_metrics,
)
from typing import Optional
import hashlib


class CodeAnalyzer:
    """
    Analyzes source code to extract complexity metrics.
    
    For 30% demo: Uses simulated metrics based on file characteristics.
    For production: Would parse actual source files.
    """
    
    def __init__(self, use_mock_data: bool = True):
        """
        Initialize code analyzer.
        
        Args:
            use_mock_data: If True, generates realistic metrics without reading files
                          If False, attempts to read and analyze actual files
        """
        self.use_mock_data = use_mock_data
        self._analysis_cache = {}
    
    def analyze(self, mutant: Mutant) -> CodeMetrics:
        """
        Analyze code for a mutant and return metrics.
        
        Args:
            mutant: Mutant to analyze
            
        Returns:
            CodeMetrics object with complexity scores
        """
        # If mutant already has metrics, return them
        if mutant.code_metrics:
            return mutant.code_metrics
        
        # Check cache
        cache_key = f"{mutant.location.file_path}:{mutant.location.line_start}"
        if cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]
        
        # For demo: generate realistic metrics
        if self.use_mock_data:
            metrics = self._generate_mock_metrics(mutant)
        else:
            # For production: would read and analyze actual file
            try:
                metrics = self._analyze_real_file(mutant)
            except FileNotFoundError:
                # Fallback to mock if file doesn't exist
                print(f"⚠️  File not found, using mock metrics: {mutant.location.file_path}")
                metrics = self._generate_mock_metrics(mutant)
        
        # Cache the result
        self._analysis_cache[cache_key] = metrics
        
        return metrics
    
    def _generate_mock_metrics(self, mutant: Mutant) -> CodeMetrics:
        """
        Generate realistic metrics based on file and location characteristics.
        
        Uses deterministic randomization based on file hash so results are consistent.
        """
        # Create deterministic seed from file path
        seed = int(hashlib.md5(mutant.location.file_path.encode()).hexdigest(), 16) % 10000
        
        # Base complexity on file type and location
        file_lower = mutant.location.file_path.lower()
        
        # Security critical files (auth, password, security)
        is_security = any(word in file_lower for word in ['auth', 'password', 'security', 'crypto'])
        
        # Service/business logic files tend to be more complex
        is_service = 'service' in file_lower
        
        # Utility files tend to be simpler
        is_util = 'util' in file_lower or 'helper' in file_lower
        
        # Model/DTO files tend to be simple
        is_model = 'model' in file_lower or 'dto' in file_lower or 'entity' in file_lower
        
        # Determine base complexity
        if is_service:
            base_complexity = 8 + (seed % 12)  # 8-20
        elif is_security:
            base_complexity = 6 + (seed % 10)  # 6-16
        elif is_util:
            base_complexity = 3 + (seed % 8)   # 3-11
        elif is_model:
            base_complexity = 1 + (seed % 4)   # 1-5
        else:
            base_complexity = 4 + (seed % 8)   # 4-12
        
        # Adjust based on line number (deeper in file = more complex context)
        depth_factor = min(mutant.location.line_start / 100, 2.0)
        cyclomatic = int(base_complexity * (1 + depth_factor * 0.3))
        
        # Cognitive complexity is usually 1.2-1.5x cyclomatic
        cognitive = int(cyclomatic * 1.3)
        
        # Nesting depth (0-6)
        nesting = min((seed % 7), 6)
        
        # Lines of code in method/class
        if is_model:
            loc = 20 + (seed % 50)   # 20-70
        elif is_util:
            loc = 30 + (seed % 80)   # 30-110
        else:
            loc = 50 + (seed % 200)  # 50-250
        
        # Days since last modification (0-90)
        days_since_modified = seed % 91
        
        # Public API determination
        is_public_api = is_service or 'controller' in file_lower or 'api' in file_lower
        
        return CodeMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            nesting_depth=nesting,
            lines_of_code=loc,
            is_security_critical=is_security,
            is_public_api=is_public_api,
            last_modified_days_ago=days_since_modified
        )
    
    def _analyze_real_file(self, mutant: Mutant) -> CodeMetrics:
        """
        Analyze actual source file (for production use).
        
        This would:
        1. Read the source file
        2. Parse it using a language-specific parser
        3. Calculate real complexity metrics
        4. Determine security/API status
        
        For now, raises FileNotFoundError if file doesn't exist.
        """
        from pathlib import Path
        
        file_path = Path(mutant.location.file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # TODO: Implement real parsing for Java/JavaScript
        # For now, use simple heuristics
        
        lines = source_code.split('\n')
        loc = len(lines)
        
        # Count branches (if, else, while, for, case, catch)
        branch_keywords = ['if', 'else', 'while', 'for', 'case', 'catch', '&&', '||', '?']
        cyclomatic = 1  # Base complexity
        for line in lines:
            for keyword in branch_keywords:
                cyclomatic += line.count(keyword)
        
        # Estimate nesting by counting indentation
        max_indent = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)
        
        nesting = min(max_indent, 6)
        cognitive = int(cyclomatic * 1.3)
        
        # Detect security-critical code
        security_keywords = ['password', 'auth', 'token', 'crypto', 'hash', 'encrypt']
        is_security = any(keyword in source_code.lower() for keyword in security_keywords)
        
        # Detect public API
        is_public = 'public' in source_code and ('class' in source_code or 'method' in source_code)
        
        # Get file modification time
        import datetime
        mod_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
        days_ago = (datetime.datetime.now() - mod_time).days
        
        return CodeMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            nesting_depth=nesting,
            lines_of_code=loc,
            is_security_critical=is_security,
            is_public_api=is_public,
            last_modified_days_ago=days_ago
        )
    
    def get_analysis_summary(self) -> dict:
        """Get summary of analyzed files."""
        return {
            'files_analyzed': len(self._analysis_cache),
            'using_mock_data': self.use_mock_data
        }
    
    def clear_cache(self):
        """Clear analysis cache."""
        self._analysis_cache.clear()