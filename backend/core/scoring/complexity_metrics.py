"""
Complexity Metrics Calculation Utilities

Provides standalone functions for calculating various code complexity metrics.
Used by CodeAnalyzer to compute complexity scores.
"""

from typing import List
import math


def calculate_cyclomatic_complexity(control_flow_graph: dict) -> int:
    """
    Calculate cyclomatic complexity from control flow graph.

    M = E - N + 2P
    Where:
    - E = number of edges
    - N = number of nodes
    - P = number of connected components (usually 1)

    Args:
        control_flow_graph: Dict with 'edges' and 'nodes' keys

    Returns:
        Cyclomatic complexity value
    """
    edges = control_flow_graph.get('edges', [])
    nodes = control_flow_graph.get('nodes', [])

    E = len(edges)
    N = len(nodes)
    P = 1  # Assume single connected component

    return E - N + 2 * P


def calculate_cognitive_complexity(ast_nodes: list) -> int:
    """
    Calculate cognitive complexity (simpler than cyclomatic).

    Increments for:
    - Nested control structures (+nesting level)
    - Boolean operators in conditions
    - Recursion

    Args:
        ast_nodes: List of AST nodes with 'type' and 'nesting' attributes

    Returns:
        Cognitive complexity score
    """
    score = 0

    for node in ast_nodes:
        node_type = node.get('type', '')
        nesting = node.get('nesting', 0)

        # Control structures
        if node_type in ['if', 'while', 'for', 'switch', 'catch']:
            score += 1 + nesting

        # Boolean operators (&&, ||)
        if node_type in ['and', 'or']:
            score += 1

        # Recursion
        if node_type == 'recursive_call':
            score += nesting + 1

    return score


def estimate_halstead_metrics(operators: List[str], operands: List[str]) -> dict:
    """
    Calculate Halstead complexity metrics.

    Args:
        operators: List of all operators in code
        operands: List of all operands in code

    Returns:
        Dict with various Halstead metrics
    """
    n1 = len(set(operators))  # Unique operators
    n2 = len(set(operands))   # Unique operands
    N1 = len(operators)       # Total operators
    N2 = len(operands)        # Total operands

    vocabulary = n1 + n2
    length = N1 + N2

    # Avoid log(0) errors
    if vocabulary == 0 or n2 == 0:
        return {
            'vocabulary': 0,
            'length': 0,
            'volume': 0,
            'difficulty': 0,
            'effort': 0,
            'time_to_program': 0
        }

    volume = length * math.log2(vocabulary)
    difficulty = (n1 / 2) * (N2 / n2)
    effort = volume * difficulty

    return {
        'vocabulary': vocabulary,
        'length': length,
        'volume': volume,
        'difficulty': difficulty,
        'effort': effort,
        'time_to_program': effort / 18  # Halstead's constant
    }


def calculate_maintainability_index(
    loc: int, 
    cyclomatic: int, 
    halstead_volume: float
) -> float:
    """
    Calculate maintainability index (0-100 scale).

    MI = 171 - 5.2*ln(V) - 0.23*G - 16.2*ln(LOC)
    Where:
    - V = Halstead Volume
    - G = Cyclomatic Complexity
    - LOC = Lines of Code

    Returns:
        Maintainability index (0-100, higher is better)
    """
    if loc == 0 or halstead_volume == 0:
        return 50.0  # Default middle value

    mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * cyclomatic - 16.2 * math.log(loc)

    # Normalize to 0-100
    mi = max(0, min(100, mi))

    return mi


# Legacy class wrapper for backward compatibility
class ComplexityCalculator:
    """
    Legacy wrapper class for complexity metrics.
    
    New code should use the standalone functions above.
    This class is maintained for backward compatibility.
    """
    
    @staticmethod
    def cyclomatic_complexity(control_flow_graph: dict) -> int:
        """Deprecated: Use calculate_cyclomatic_complexity() instead."""
        return calculate_cyclomatic_complexity(control_flow_graph)
    
    @staticmethod
    def cognitive_complexity(ast_nodes: list) -> int:
        """Deprecated: Use calculate_cognitive_complexity() instead."""
        return calculate_cognitive_complexity(ast_nodes)
    
    @staticmethod
    def halstead_metrics(operators: List[str], operands: List[str]) -> dict:
        """Deprecated: Use estimate_halstead_metrics() instead."""
        return estimate_halstead_metrics(operators, operands)
    
    @staticmethod
    def maintainability_index(
        loc: int, 
        cyclomatic: int, 
        halstead_volume: float
    ) -> float:
        """Deprecated: Use calculate_maintainability_index() instead."""
        return calculate_maintainability_index(loc, cyclomatic, halstead_volume)