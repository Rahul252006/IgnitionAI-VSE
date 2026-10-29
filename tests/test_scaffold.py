import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PACKAGES = {
    "alignment", "arena", "compiler", "contracts", "executor",
    "observers", "planner", "provenance", "quality", "registry",
    "residuals", "runners", "testing",
}

REQUIRED_DEPENDENCIES = {
    "pydantic", "sympy", "pint", "numpy", "onnxruntime",
    "lightgbm", "pyyaml", "pytest", "hypothesis", "import_linter",
}


def test_required_package_layout_exists():
    assert (ROOT / "vse" / "api.py").is_file()

    for package in PACKAGES:
        assert (ROOT / "vse" / package / "__init__.py").is_file()
        assert (ROOT / "tests" / package).is_dir()


def test_python_version_and_dependencies_are_pinned():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())
    project = config["project"]

    assert project["requires-python"] == ">=3.11"

    dependencies = project.get("dependencies", []) + (
        project.get("optional-dependencies", {}).get("dev", [])
    )

    names = set()
    for dependency in dependencies:
        name = re.split(r"[<=>!~\[]", dependency, maxsplit=1)[0]
        names.add(name.lower().replace("-", "_"))
        assert "==" in dependency, f"Dependency is not pinned: {dependency}"

    assert REQUIRED_DEPENDENCIES <= names


def test_ci_runs_tests_and_linter_on_push():
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    assert workflow.is_file()

    content = workflow.read_text()
    assert "push:" in content
    assert "python -m pytest" in content
    assert "lint-imports" in content
