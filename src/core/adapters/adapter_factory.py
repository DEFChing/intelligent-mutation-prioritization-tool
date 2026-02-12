from typing import Optional
from pathlib import Path
from .base_adapter import MutationFrameworkAdapter


class AdapterFactory:
    """
    Factory for creating appropriate framework adapter.

    Auto-detects project type and returns correct adapter.
    """

    @staticmethod
    def create_adapter(project_path: str,
                       framework: Optional[str] = None) -> MutationFrameworkAdapter:
        """
        Create appropriate adapter for project.

        Args:
            project_path: Path to project
            framework: Force specific framework ("pit" or "stryker"), or None for auto-detect

        Returns:
            Appropriate adapter instance

        Raises:
            ValueError: If project type cannot be determined or unsupported
        """
        project = Path(project_path)

        if framework:
            framework = framework.lower()
            if framework == "pit":
                return AdapterFactory._create_pit_adapter(project)
            elif framework == "stryker":
                return AdapterFactory._create_stryker_adapter(project)
            else:
                raise ValueError(f"Unknown framework: {framework}")

        # Auto-detect
        if AdapterFactory._is_java_project(project):
            return AdapterFactory._create_pit_adapter(project)
        elif AdapterFactory._is_javascript_project(project):
            return AdapterFactory._create_stryker_adapter(project)
        else:
            raise ValueError(f"Cannot determine project type at {project_path}")

    @staticmethod
    def _is_java_project(project_path: Path) -> bool:
        """Check if project is a Java project"""
        # Look for Maven or Gradle files
        has_maven = (project_path / "pom.xml").exists()
        has_gradle = (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists()

        # Look for Java source files
        has_java_src = any(project_path.rglob("*.java"))

        return (has_maven or has_gradle) and has_java_src

    @staticmethod
    def _is_javascript_project(project_path: Path) -> bool:
        """Check if project is a JavaScript/TypeScript project"""
        # Look for package.json
        has_package_json = (project_path / "package.json").exists()

        # Look for JS/TS files
        has_js_src = any(project_path.rglob("*.js")) or any(project_path.rglob("*.ts"))

        return has_package_json and has_js_src

    @staticmethod
    def _create_pit_adapter(project_path: Path):
        """Create PIT adapter (implementation in Week 11-12)"""
        # This will be implemented later
        # For now, raise NotImplementedError
        raise NotImplementedError("PIT adapter will be implemented in Week 11-12")

    @staticmethod
    def _create_stryker_adapter(project_path: Path):
        """Create Stryker adapter (implementation in Week 11-12)"""
        # This will be implemented later
        # For now, raise NotImplementedError
        raise NotImplementedError("Stryker adapter will be implemented in Week 11-12")

    @staticmethod
    def get_supported_frameworks() -> list[str]:
        """Get list of supported frameworks"""
        return ["pit", "stryker"]