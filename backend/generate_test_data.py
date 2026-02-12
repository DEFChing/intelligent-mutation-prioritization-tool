"""
Generate realistic sample test data for IMPT system demonstration.

This creates:
1. Sample mutants (100 mutants across 10 files)
2. Historical effectiveness data
3. Bug tracking data
4. Code metrics data
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_sample_mutants(count: int = 100) -> list[dict]:
    """Generate sample mutant data"""

    # Sample files
    files = [
        "src/auth/Login.java",
        "src/auth/Register.java",
        "src/auth/PasswordReset.java",
        "src/service/UserService.java",
        "src/service/PaymentService.java",
        "src/service/OrderService.java",
        "src/utils/Validator.java",
        "src/utils/StringHelper.java",
        "src/model/User.java",
        "src/model/Order.java",
    ]

    # Sample code mutations
    mutations = [
        ("x + y", "x - y", "ARITHMETIC"),
        ("x - y", "x + y", "ARITHMETIC"),
        ("x * y", "x / y", "ARITHMETIC"),
        ("x < 10", "x <= 10", "BOUNDARY"),
        ("x <= 10", "x < 10", "BOUNDARY"),
        ("x > 0", "x >= 0", "BOUNDARY"),
        ("x == y", "x != y", "CONDITIONAL"),
        ("x && y", "x || y", "CONDITIONAL"),
        ("!flag", "flag", "NEGATE"),
        ("return true", "return false", "RETURN"),
        ("return 0", "return 1", "RETURN"),
        ("count++", "count--", "INCREMENT"),
        ("index + 1", "index - 1", "ARITHMETIC"),
    ]

    mutants = []

    for i in range(count):
        file = random.choice(files)
        original, mutated, operator = random.choice(mutations)

        # Security critical for auth files
        is_security = "auth" in file.lower() or "password" in file.lower()

        # Public API for service classes
        is_public = "service" in file.lower()

        mutant = {
            "id": f"MUT_{i + 1:03d}",
            "framework_id": f"pit_{random.randint(1000, 9999)}",
            "location": {
                "file": file,
                "line": random.randint(10, 300),
                "column": random.randint(0, 50),
            },
            "operator": operator,
            "original": original,
            "mutated": mutated,
            "description": f"Mutate {operator.lower()} operator",
            "metrics": {
                "complexity": random.randint(1, 25),
                "nesting": random.randint(0, 6),
                "loc": random.randint(50, 500),
                "security_critical": is_security,
                "public_api": is_public,
                "days_since_modified": random.randint(0, 90),
            },
        }

        mutants.append(mutant)

    return mutants


def generate_historical_data() -> dict:
    """Generate historical effectiveness data"""

    operators = [
        "ARITHMETIC",
        "BOUNDARY",
        "CONDITIONAL",
        "NEGATE",
        "RETURN",
        "INCREMENT",
        "LOGICAL",
        "VOID_CALL",
    ]

    history = {}

    for operator in operators:
        # Realistic kill rates based on research
        if operator == "BOUNDARY":
            kill_rate = 0.85
        elif operator == "ARITHMETIC":
            kill_rate = 0.75
        elif operator == "CONDITIONAL":
            kill_rate = 0.70
        elif operator == "NEGATE":
            kill_rate = 0.80
        elif operator == "RETURN":
            kill_rate = 0.65
        elif operator == "INCREMENT":
            kill_rate = 0.72
        elif operator == "LOGICAL":
            kill_rate = 0.78
        else:
            kill_rate = 0.50

        generated = random.randint(80, 150)
        killed = int(generated * kill_rate)
        survived = generated - killed

        history[operator] = {
            "generated": generated,
            "killed": killed,
            "survived": survived,
            "avg_time": round(random.uniform(1.5, 4.5), 2),
        }

    return history


def generate_bug_history() -> dict:
    """Generate bug tracking data"""

    files = [
        "src/auth/Login.java",
        "src/auth/Register.java",
        "src/auth/PasswordReset.java",
        "src/service/UserService.java",
        "src/service/PaymentService.java",
        "src/service/OrderService.java",
        "src/utils/Validator.java",
        "src/utils/StringHelper.java",
        "src/model/User.java",
        "src/model/Order.java",
    ]

    bug_types = [
        "NullPointerException",
        "ArrayIndexOutOfBoundsException",
        "Logic Error",
        "Off-by-one Error",
        "Boundary Condition Bug",
        "Authentication Bypass",
        "SQL Injection",
        "XSS Vulnerability",
    ]

    severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

    bugs = []

    # Generate 30 historical bugs
    for i in range(30):
        bug = {
            "id": f"BUG-{1000 + i}",
            "file": random.choice(files),
            "line": random.randint(10, 300),
            "type": random.choice(bug_types),
            "severity": random.choice(severities),
            "date_found": (
                datetime.now() - timedelta(days=random.randint(1, 365))
            ).isoformat(),
            "date_fixed": (
                datetime.now() - timedelta(days=random.randint(0, 30))
            ).isoformat(),
        }
        bugs.append(bug)

    return {"bugs": bugs}


def generate_project_metadata() -> dict:
    """Generate project metadata"""

    return {
        "project_name": "SampleJavaApp",
        "language": "Java",
        "framework": "Maven",
        "version": "1.2.3",
        "created": "2023-06-15",
        "last_modified": datetime.now().isoformat(),
        "statistics": {
            "source_files": 10,
            "test_files": 15,
            "source_loc": 3500,
            "test_loc": 2100,
            "test_count": 234,
            "code_coverage": 82.5,
        },
    }


def generate_test_coverage() -> dict:
    """Generate test coverage data"""

    files = [
        "src/auth/Login.java",
        "src/auth/Register.java",
        "src/service/UserService.java",
        "src/service/PaymentService.java",
        "src/utils/Validator.java",
    ]

    coverage = {}

    for file in files:
        # Generate 10-30 test names that cover this file
        num_tests = random.randint(10, 30)
        tests = [
            f"Test{file.split('/')[-1].replace('.java', '')}.test{j:02d}"
            for j in range(num_tests)
        ]

        # Add line coverage information
        total_lines = random.randint(50, 300)
        covered_lines = int(total_lines * random.uniform(0.6, 0.95))

        coverage[file] = {
            "tests": tests,
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "coverage_percent": round((covered_lines / total_lines) * 100, 1),
        }

    return coverage


def generate_duplicate_mutants() -> list[dict]:
    """Generate some intentional duplicates for subsumption testing"""

    duplicates = []

    # Create 5 sets of duplicates (3 mutants each)
    for i in range(5):
        base_id = 200 + (i * 10)
        line = 50 + (i * 20)

        for j in range(3):
            mutant = {
                "id": f"MUT_DUP_{base_id + j}",
                "framework_id": f"dup_{base_id + j}",
                "location": {
                    "file": "src/utils/Validator.java",
                    "line": line,  # Same line!
                    "column": 10,
                },
                "operator": "BOUNDARY",
                "original": "x < 10",
                "mutated": "x <= 10",  # Same mutation!
                "description": "Duplicate for testing",
                "metrics": {
                    "complexity": 8,
                    "nesting": 2,
                    "loc": 150,
                    "security_critical": False,
                    "public_api": True,
                    "days_since_modified": 5,
                },
            }
            duplicates.append(mutant)

    return duplicates


def main():
    """Generate all test data files"""

    print("🗂️  Generating Test Data for IMPT System Demo")
    print("=" * 60)

    # Updated: Use sample_data directory in new structure
    output_dir = Path(__file__).parent / "sample_data"
    output_dir.mkdir(exist_ok=True)

    # Generate mutants
    print("\n🔬 Generating mutants...")
    mutants = generate_sample_mutants(100)

    # Add some duplicates for subsumption testing
    duplicates = generate_duplicate_mutants()
    all_mutants = mutants + duplicates
    random.shuffle(all_mutants)

    with open(output_dir / "mutants.json", "w") as f:
        json.dump(all_mutants, f, indent=2)
    print(
        f"   ✓ Generated {len(all_mutants)} mutants "
        f"(including {len(duplicates)} intentional duplicates)"
    )

    # Generate historical data
    print("\n📊 Generating historical effectiveness data...")
    history = generate_historical_data()
    with open(output_dir / "historical_data.json", "w") as f:
        json.dump(history, f, indent=2)
    print(f"   ✓ Generated history for {len(history)} mutation operators")

    # Generate bug history
    print("\n🐛 Generating bug tracking data...")
    bugs = generate_bug_history()
    with open(output_dir / "bug_history.json", "w") as f:
        json.dump(bugs, f, indent=2)
    print(f"   ✓ Generated {len(bugs['bugs'])} historical bugs")

    # Generate project metadata
    print("\n📦 Generating project metadata...")
    metadata = generate_project_metadata()
    with open(output_dir / "project_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✓ Generated metadata for {metadata['project_name']}")

    # Generate test coverage
    print("\n🧪 Generating test coverage data...")
    coverage = generate_test_coverage()
    with open(output_dir / "test_coverage.json", "w") as f:
        json.dump(coverage, f, indent=2)
    print(f"   ✓ Generated coverage for {len(coverage)} files")

    # Create README
    print("\n📄 Creating README...")
    readme_content = (
        """# IMPT Sample Data

This directory contains sample test data for demonstrating the IMPT system.

## Files:

- **mutants.json**: 115 sample mutants (100 unique + 15 duplicates for testing)
- **historical_data.json**: Historical effectiveness rates for mutation
  operators
- **bug_history.json**: 30 historical bugs for bug density analysis
- **project_metadata.json**: Sample project information
- **test_coverage.json**: Test coverage data for files

## Usage:

Run the demo script to see these datasets in action:
```bash
cd backend
python demo_30_percent.py
```

## Data Statistics:

- Total Mutants: 115
- Unique Locations: ~100
- Intentional Duplicates: 15 (for subsumption testing)
- Historical Bugs: 30
- Files Covered: 10
- Mutation Operators: 8

Generated: """
        + datetime.now().isoformat()
    )

    with open(output_dir / "README.md", "w") as f:
        f.write(readme_content)
    print("   ✓ Created README.md")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Test Data Generation Complete!")
    print(f"\n📂 Output Directory: {output_dir.absolute()}")
    print("\nGenerated Files:")
    for file in sorted(output_dir.glob("*.json")):
        size_kb = file.stat().st_size / 1024
        print(f"   • {file.name:<30} ({size_kb:.1f} KB)")
    print("   • README.md")

    print("\n🚀 Ready to run demo:")
    print("   cd backend")
    print("   python demo_30_percent.py")
    print()


if __name__ == "__main__":
    main()
