import ast
from pathlib import Path

VSE_ROOT = Path(__file__).resolve().parents[1] / "vse"

FILESYSTEM_METHODS = {
    "open",
    "read_text",
    "read_bytes",
    "read",
    "readline",
    "readlines",
    "iterdir",
    "glob",
    "rglob",
    "exists",
    "is_file",
    "is_dir",
    "listdir",
    "scandir",
    "walk",
}

OPEN_IMPORT_MODULES = {"builtins", "io", "os"}


def find_filesystem_access(source: str, filename: str = "<source>") -> list[str]:
    """Find common filesystem-access calls in Python source."""
    tree = ast.parse(source, filename=filename)
    open_names = {"open"}

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module in OPEN_IMPORT_MODULES:
                for alias in node.names:
                    if alias.name == "open":
                        open_names.add(alias.asname or alias.name)

    violations = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        function = node.func

        if isinstance(function, ast.Name) and function.id in open_names:
            violations.append(f"{filename}:{node.lineno}: {function.id}()")
        elif (
            isinstance(function, ast.Attribute)
            and function.attr in FILESYSTEM_METHODS
        ):
            violations.append(f"{filename}:{node.lineno}: {function.attr}()")

    return violations


def test_only_registry_performs_filesystem_access():
    violations = []

    for source_file in VSE_ROOT.rglob("*.py"):
        relative_path = source_file.relative_to(VSE_ROOT)

        # The registry owns provider and configuration file access.
        if relative_path.parts[0] == "registry":
            continue

        violations.extend(
            find_filesystem_access(
                source_file.read_text(encoding="utf-8"),
                filename=str(relative_path),
            )
        )

    assert not violations, (
        "Filesystem access is restricted to vse.registry:\n"
        + "\n".join(violations)
    )


def test_detects_builtin_open():
    assert find_filesystem_access('open("config.yaml")')


def test_detects_aliased_open():
    source = "from pathlib import Path as P\nP('config.yaml').read_text()"
    assert find_filesystem_access(source)


def test_detects_os_directory_reads():
    assert find_filesystem_access("import os\nos.listdir('/tmp')")


def test_allows_source_without_filesystem_access():
    source = "def add(a, b):\n    return a + b\n"
    assert find_filesystem_access(source) == []
