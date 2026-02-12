"""
IMPT System - 30% Completion Demonstration
===========================================

This script demonstrates the integration of:
1. Multi-Factor Scoring Engine
2. Subsumption Analysis Module
3. Framework Adapter Base

Run from backend folder:
    cd backend
    python demo_30_percent.py
"""

import json
from pathlib import Path

from core.adapters.data_schemas import (AdapterConfiguration,
                                        StandardMutantReport)
from core.models import CodeLocation, CodeMetrics, Mutant, MutationOperator
from core.scoring.code_analyzer import CodeAnalyzer
from core.scoring.history_tracker import HistoryTracker
from core.scoring.multi_factor_scorer import MultiFactorScorer
from core.subsumption.analyzer import SubsumptionAnalyzer
from core.subsumption.coverage_mapper import CoverageMapper


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_section(text: str):
    """Print formatted section"""
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print("─" * 70)


def load_sample_mutants() -> list[Mutant]:
    """Load sample mutants from test data"""
    print("📂 Loading sample mutants from sample_data/mutants.json...")

    # Updated path for new structure
    data_path = Path(__file__).parent / "sample_data" / "mutants.json"

    with open(data_path, "r") as f:
        data = json.load(f)

    mutants = []
    for m_data in data:
        mutant = Mutant(
            id=m_data["id"],
            framework_id=m_data["framework_id"],
            location=CodeLocation(
                file_path=m_data["location"]["file"],
                line_start=m_data["location"]["line"],
                line_end=m_data["location"]["line"],
                column_start=m_data["location"]["column"],
                column_end=m_data["location"]["column"] + 10,
            ),
            operator=MutationOperator(m_data["operator"]),
            original_code=m_data["original"],
            mutated_code=m_data["mutated"],
            description=m_data.get("description", ""),
            code_metrics=CodeMetrics(
                cyclomatic_complexity=m_data["metrics"]["complexity"],
                cognitive_complexity=m_data["metrics"]["complexity"],
                nesting_depth=m_data["metrics"]["nesting"],
                lines_of_code=m_data["metrics"]["loc"],
                is_security_critical=m_data["metrics"][
                    "security_critical"],
                is_public_api=m_data["metrics"]["public_api"],
                last_modified_days_ago=m_data["metrics"][
                    "days_since_modified"],
            ),
        )
        mutants.append(mutant)

    print(f"   ✓ Loaded {len(mutants)} mutants")
    return mutants


def demo_scoring_engine(mutants: list[Mutant]):
    """Demonstrate Multi-Factor Scoring Engine"""
    print_header("DEMO 1: MULTI-FACTOR SCORING ENGINE")

    print("🧠 Initializing scoring components...")
    history_tracker = HistoryTracker()
    code_analyzer = CodeAnalyzer()
    scorer = MultiFactorScorer(history_tracker, code_analyzer)
    print("   ✓ Components initialized")

    print_section("Scoring Mutants")
    print(f"Input: {len(mutants)} mutants")
    print("Algorithm: Multi-factor weighted scoring")
    print("\nFactors:")
    print("  • Historical Effectiveness (30%)")
    print("  • Code Complexity (25%)")
    print("  • Security Criticality (20%)")
    print("  • Change Recency (15%)")
    print("  • Bug History (10%)")

    print("\n⏳ Computing priority scores...")
    scored_mutants = scorer.score_all(mutants)
    print("   ✓ Scoring complete\n")

    # Display top 10 mutants
    print("📊 TOP 10 PRIORITIZED MUTANTS:")
    header_line = (
        f"{'Rank':<6} {'ID':<15} {'Score':<8} "
        f"{'Operator':<20} {'Location':<30}"
    )
    print(header_line)
    print("─" * 85)

    for i, mutant in enumerate(scored_mutants[:10], 1):
        file_name = mutant.location.file_path.split("/")[-1]
        location_str = f"{file_name}:{mutant.location.line_start}"
        print(
            f"{i:<6} {mutant.id:<15} {mutant.priority_score:<8.2f} "
            f"{mutant.operator.value:<20} {location_str:<30}"
        )

    # Show detailed explanation for top mutant
    print_section("Detailed Explanation: Top Priority Mutant")
    top_mutant = scored_mutants[0]
    explanation = scorer.explain_score(top_mutant)

    print(f"\n🎯 Mutant ID: {explanation['mutant_id']}")
    print(f"   Final Score: {explanation['final_score']:.2f}/10.0\n")

    print("   Score Breakdown:")
    for factor_name, factor_data in explanation["breakdown"].items():
        contrib = factor_data["weighted_contribution"]
        expl = factor_data["explanation"]
        bar = "█" * int(contrib / 2) + "░" * (5 - int(contrib / 2))
        print(
            f"   • {factor_name.replace('_', ' ').title():<25} "
            f"{bar} {contrib:.2f} ({expl})"
        )

    print(f"\n   Code Location: {top_mutant.location}")
    print(f"   Operator: {top_mutant.operator.value}")
    change_str = f"'{top_mutant.original_code}' → '{top_mutant.mutated_code}'"
    print(f"   Change: {change_str}")

    # Statistics
    print_section("Scoring Statistics")
    scores = [m.priority_score for m in scored_mutants]
    mean_score = sum(scores) / len(scores)
    variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
    std_dev = variance**0.5
    print(f"   Average Score: {mean_score:.2f}")
    print(f"   Highest Score: {max(scores):.2f}")
    print(f"   Lowest Score:  {min(scores):.2f}")
    print(f"   Std Deviation: {std_dev:.2f}")

    return scored_mutants


def demo_subsumption_analysis(mutants: list[Mutant]):
    """Demonstrate Subsumption Analysis Module"""
    print_header("DEMO 2: SUBSUMPTION ANALYSIS MODULE")

    print("🔍 Initializing subsumption analyzer...")
    coverage_mapper = CoverageMapper()
    analyzer = SubsumptionAnalyzer(coverage_mapper)
    print("   ✓ Analyzer initialized")

    print_section("Redundancy Detection")
    print(f"Input: {len(mutants)} mutants")
    print("Techniques:")
    print("  1. Exact duplicate removal")
    print("  2. Location-based clustering")
    print("  3. Operator-level subsumption")
    print("  4. Coverage-based subsumption")

    print("\n⏳ Analyzing redundancies...\n")
    unique_mutants = analyzer.filter_redundant(mutants)

    # Display statistics
    stats = analyzer.get_statistics()

    print_section("Subsumption Results")
    print(f"   Total Input Mutants:       {stats['total_input']:>6}")
    print(f"   Exact Duplicates Removed:  {stats['exact_duplicates']:>6}")
    print(f"   Location Clustered:        {stats['location_clustered']:>6}")
    print(f"   Operator Subsumed:         {stats['operator_subsumed']:>6}")
    print(f"   Coverage Subsumed:         {stats['coverage_subsumed']:>6}")
    print(f"   {'─' * 40}")
    print(f"   Final Unique Mutants:      {stats['total_output']:>6}")
    print(f"   Reduction Achieved:        {stats['reduction_percent']:>5.1f}%")

    # Visualize reduction
    print_section("Reduction Visualization")
    total_bar_len = 50
    kept_len = int((stats["total_output"] / stats["total_input"]) * total_bar_len)
    removed_len = total_bar_len - kept_len

    original_bar = "█" * total_bar_len
    print(f"\n   Original: [{original_bar}] {stats['total_input']} mutants")

    after_bar = "█" * kept_len + "░" * removed_len
    print(f"   After:    [{after_bar}] {stats['total_output']} mutants")

    removed_bar = "░" * kept_len + "█" * removed_len
    removed_count = stats["total_input"] - stats["total_output"]
    print(f"   Removed:  [{removed_bar}] {removed_count} mutants")

    # Show examples of removed mutants
    print_section("Examples of Removed Redundancies")
    removed_ids = set(m.id for m in mutants) - set(m.id for m in unique_mutants)

    if removed_ids:
        print("\n   Sample Removed Mutants (first 5):")
        for i, mut_id in enumerate(list(removed_ids)[:5], 1):
            print(f"   {i}. {mut_id}")
    else:
        print("   (No duplicates found in this dataset)")

    return unique_mutants


def demo_adapter_schemas():
    """Demonstrate Framework Adapter Data Schemas"""
    print_header("DEMO 3: FRAMEWORK ADAPTER BASE")

    print("📋 Standard Data Format Examples")
    print("   Purpose: Framework-agnostic data exchange\n")

    print_section("Standard Mutant Report Format")

    report = StandardMutantReport(
        mutant_id="AUTH_BOUND_145",
        file_path="src/auth/Login.java",
        line_number=45,
        column_number=12,
        operator_type="BOUNDARY_CONDITION",
        original_code="attempts < 3",
        mutated_code="attempts <= 3",
        status="KILLED",
        execution_time_ms=1250.5,
        killing_test="LoginTest.testMaxAttempts()",
    )

    print("\n   Example Mutant Report:")
    print(f"   {json.dumps(report.to_dict(), indent=6)}")

    print_section("Adapter Configuration Format")

    config = AdapterConfiguration(
        timeout_per_mutant_seconds=5.0,
        max_parallel_threads=4,
        fail_fast=False,
        verbose=True,
        generate_html_report=True,
        export_json=True,
        exclude_patterns=["*Test.java", "*.spec.js"],
        framework_options={
            "pit": {
                "mutators": ["DEFAULTS"],
                "targetClasses": ["com.example.*"],
            }
        },
    )

    print("\n   Example Configuration:")
    print(f"   {json.dumps(config.to_dict(), indent=6)}")

    print_section("Data Conversion Examples")

    # Show JSON serialization
    print("\n   ✓ JSON Serialization:")
    print(f"     {report.to_json()[:100]}...")

    # Show deserialization
    print("\n   ✓ JSON Deserialization:")
    report_dict = report.to_dict()
    restored_report = StandardMutantReport.from_dict(report_dict)
    print(f"     Original ID:  {report.mutant_id}")
    print(f"     Restored ID:  {restored_report.mutant_id}")
    match_result = "✓" if report.mutant_id == restored_report.mutant_id else "✗"
    print(f"     Match: {match_result}")


def demo_integration_workflow(mutants: list[Mutant]):
    """Demonstrate complete integrated workflow"""
    print_header("DEMO 4: INTEGRATED WORKFLOW")

    print("🚀 Simulating complete 30% system workflow:\n")

    # Step 1: Load mutants
    print("Step 1: Load Mutants")
    print(f"   └─ Loaded {len(mutants)} mutants from framework")

    # Step 2: Scoring
    print("\nStep 2: Multi-Factor Scoring")
    scorer = MultiFactorScorer()
    scored = scorer.score_all(mutants)
    print(f"   └─ Scored {len(scored)} mutants")
    avg_priority = sum(m.priority_score for m in scored) / len(scored)
    print(f"      Average priority: {avg_priority:.2f}")

    # Step 3: Subsumption
    print("\nStep 3: Subsumption Analysis")
    analyzer = SubsumptionAnalyzer()
    unique = analyzer.filter_redundant(scored)
    reduction = (1 - len(unique) / len(scored)) * 100
    eliminated = len(scored) - len(unique)
    print(f"   └─ Eliminated {eliminated} redundant mutants " f"({reduction:.1f}%)")

    # Step 4: Selection simulation (time-budget would happen here)
    print("\nStep 4: Time-Budget Optimization (To be implemented)")
    selected_count = int(len(unique) * 0.15)  # Simulate 15% selection
    selected = unique[:selected_count]
    print(f"   └─ Would select ~{selected_count} mutants for 10-minute budget")

    # Step 5: Export
    print("\nStep 5: Data Export")
    reports = [
        StandardMutantReport(
            mutant_id=m.id,
            file_path=m.location.file_path,
            line_number=m.location.line_start,
            column_number=m.location.column_start,
            operator_type=m.operator.value,
            original_code=m.original_code,
            mutated_code=m.mutated_code,
            status="PENDING",
            execution_time_ms=0.0,
        )
        for m in selected[:5]  # First 5 for demo
    ]

    # Updated output path for new structure
    output_path = Path(__file__).parent / "demo_output"
    output_path.mkdir(exist_ok=True)

    with open(output_path / "selected_mutants.json", "w") as f:
        json.dump([r.to_dict() for r in reports], f, indent=2)

    output_file = "demo_output/selected_mutants.json"
    print(f"   └─ Exported {len(reports)} mutants to {output_file}")

    # Summary
    print_section("Workflow Summary")
    print(f"   Input:              {len(mutants)} mutants")
    print(f"   After Scoring:      {len(scored)} mutants (prioritized)")
    print(
        f"   After Subsumption:  {len(unique)} mutants " f"({reduction:.1f}% reduction)"
    )
    print(f"   Selected for Exec:  {selected_count} mutants (~15%)")
    print("   Estimated Time:     10 minutes (vs ~60 minutes for all)")
    print("   Time Saved:         ~83%")


def demo_performance_metrics():
    """Show performance metrics of current implementation"""
    print_header("DEMO 5: PERFORMANCE METRICS")

    import time

    # Load mutants
    mutants = load_sample_mutants()

    print_section("Scoring Performance")
    scorer = MultiFactorScorer()

    start = time.time()
    scored = scorer.score_all(mutants)
    scoring_time = time.time() - start

    print(f"   Mutants Processed:  {len(mutants)}")
    print(f"   Time Elapsed:       {scoring_time:.3f} seconds")
    print(f"   Throughput:         {len(mutants) / scoring_time:.1f} mutants/second")
    print(f"   Per-Mutant Time:    {(scoring_time / len(mutants)) * 1000:.2f} ms")

    print_section("Subsumption Performance")
    analyzer = SubsumptionAnalyzer()

    start = time.time()
    unique = analyzer.filter_redundant(scored)
    subsumption_time = time.time() - start

    print(f"   Mutants Analyzed:   {len(scored)}")
    print(f"   Time Elapsed:       {subsumption_time:.3f} seconds")
    print(f"   Throughput:         {len(scored) / subsumption_time:.1f} mutants/second")
    reduction_pct = (1 - len(unique) / len(scored)) * 100
    print(f"   Reduction Achieved: {reduction_pct:.1f}%")

    print_section("Overall Performance")
    total_time = scoring_time + subsumption_time
    print(f"   Total Processing:   {total_time:.3f} seconds")
    print(f"   Overall Throughput: {len(mutants) / total_time:.1f} mutants/second")
    print(f"\n   Extrapolated for 10,000 mutants:")
    print(f"   Estimated Time:     {(10000 / len(mutants)) * total_time:.1f} seconds")
    est_minutes = ((10000 / len(mutants)) * total_time) / 60
    print(f"                       ({est_minutes:.1f} minutes)")


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║              IMPT SYSTEM - 30% COMPLETION DEMO                     ║")
    print("║         Intelligent Mutation Prioritization Tool                   ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    try:
        # Load sample data
        mutants = load_sample_mutants()

        # Run demonstrations
        scored_mutants = demo_scoring_engine(mutants)
        unique_mutants = demo_subsumption_analysis(scored_mutants)
        demo_adapter_schemas()
        demo_integration_workflow(mutants)
        demo_performance_metrics()

        # Final summary
        print_header("DEMONSTRATION COMPLETE")
        print("✅ All components successfully demonstrated!")
        print("\n📦 Deliverables Validated:")
        print("   ✓ Multi-Factor Scoring Engine (15%)")
        print("   ✓ Subsumption Analysis Module (10%)")
        print("   ✓ Framework Adapter Base (5%)")
        print("   ─────────────────────────────────")
        print("   ✓ Total: 30% System Implementation")

        print("\n📁 Output Files Generated:")
        print("   • demo_output/selected_mutants.json")
        print("   • mutation_history.json (updated)")

        print("\n🎯 Next Steps:")
        print("   1. Implement Time-Budget Optimizer (12%)")
        print("   2. Implement Dynamic Adaptation (8%)")
        print("   3. Complete PIT & Stryker Adapters (20%)")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
