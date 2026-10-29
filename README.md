# IgnitionAI Virtual Sensor Engine (VSE)

## 1. Introduction

The IgnitionAI Virtual Sensor Engine (VSE) is a Python-based engine designed to manage virtual sensor providers, resolve dependencies between sensors, plan execution, process sensor data, and track the quality and provenance of generated outputs.

A **virtual sensor** derives a value from existing sensor readings, other virtual sensors, mathematical expressions, or trained models rather than requiring a dedicated physical sensor for every measurement.

For example, a virtual sensor may estimate acceleration using successive vehicle speed readings.

> **Development status:** The repository scaffold, dependency configuration, initial architecture checks, and CI configuration are in place. Engine modules are being implemented incrementally; not all features described by the architecture are operational yet.

---

## 2. Prerequisites

Install the following before starting:

- Python 3.11 or newer
- Git
- pip, included with standard Python installations
- A terminal such as macOS Terminal, Linux shell, or Windows PowerShell

Check your installations:

```bash
python3 --version
git --version
python3 -m pip --version
```

Use Python 3.11 or newer. If your system has multiple Python versions, ensure that the version used to create the virtual environment meets this requirement.

---

## 3. Clone the repository

Open a terminal and run:

```bash
git clone https://github.com/Rahul252006/IgnitionAI-VSE.git
cd IgnitionAI-VSE
```

If you have already cloned the repository, navigate directly into its project directory.

---

## 4. Create and activate a virtual environment

A virtual environment keeps this project's Python dependencies separate from other projects on your computer.

### macOS and Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Once activated, your terminal should display `(.venv)`.

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Whenever you reopen your terminal to work on the project, navigate to the repository and activate the virtual environment again.

---

## 5. Install project dependencies

Install the project in editable mode with all development dependencies:

```bash
python -m pip install -e ".[dev]"
```

The editable installation makes the local `vse` package importable while you develop it. The `[dev]` extra installs the testing and architecture-checking tools.

### Dependency reference

| Dependency | Purpose |
|---|---|
| Pydantic v2 | Validating structured data and configuration contracts |
| SymPy | Symbolic mathematical expressions and expression processing |
| Pint | Physical units and unit conversions |
| NumPy | Numerical arrays and mathematical operations |
| ONNX Runtime | Running compatible trained models in ONNX format |
| LightGBM | Gradient-boosted machine learning models |
| PyYAML | Reading YAML-based configuration and provider definitions |
| pytest | Running automated tests |
| Hypothesis | Property-based testing with generated inputs |
| import-linter | Checking architectural import boundaries |

Exact dependency versions are pinned in `pyproject.toml`. Avoid installing arbitrary versions manually; use the project's dependency configuration.

**Note:** Installing a dependency makes its library available. It does not mean that the corresponding VSE feature has already been implemented.

---

## 6. Repository structure

The code is organized into modules with separate responsibilities. This separation helps developers implement and test each part without tightly coupling the entire engine.

```text
IgnitionAI-VSE/
├── .github/
│   └── workflows/
│       └── ci.yml
├── tests/
│   ├── test_smoke.py
│   ├── test_architecture_boundaries.py
│   └── ... package-specific tests
├── vse/
│   ├── __init__.py
│   ├── api.py
│   ├── contracts/
│   ├── registry/
│   ├── compiler/
│   ├── planner/
│   ├── alignment/
│   ├── arena/
│   ├── executor/
│   ├── runners/
│   ├── quality/
│   ├── residuals/
│   ├── provenance/
│   ├── observers/
│   │   ├── kinematics/
│   │   ├── air_path/
│   │   ├── thermal/
│   │   └── battery/
│   └── testing/
├── pyproject.toml
└── README.md
```

### Purpose of each module

| Module | Responsibility |
|---|---|
| `vse/api.py` | Intended public entry point for interacting with the engine and coordinating external calls |
| `vse/contracts/` | Shared data structures, identifiers, phases, grades, manifests, frames, and provenance contracts |
| `vse/registry/` | Loading provider definitions, validating configurations, managing units, parsing expressions, maintaining the signal catalog, and handling quarantined providers |
| `vse/compiler/` | Building dependency graphs, detecting strongly connected components, determining execution levels, preparing kernels, and compiling the master execution plan |
| `vse/planner/` | Selecting providers, considering availability and execution context, and reporting skipped providers |
| `vse/alignment/` | Aligning sensor data to a common time grid and handling stale readings |
| `vse/arena/` | Managing data storage, views, and chunking for execution |
| `vse/executor/` | Scheduling work, organizing execution groups, and managing execution budgets |
| `vse/runners/` | Defining execution interfaces for expression-based, observer-based, and model-based providers |
| `vse/quality/` | Evaluating output quality, uncertainty, confidence, and gating decisions |
| `vse/residuals/` | Supporting residual calculations and twin-related functionality |
| `vse/provenance/` | Recording and emitting information about how outputs were produced |
| `vse/observers/` | Holding Tier B observer implementations, grouped by domain |
| `vse/testing/` | Providing test harnesses, golden-case utilities, synthetic inputs, and conformance-testing support |
| `tests/` | Automated tests for package behavior and architectural constraints |
| `.github/workflows/ci.yml` | Running automated tests and architecture checks in GitHub Actions |
| `pyproject.toml` | Project metadata, supported Python versions, pinned dependencies, and tool configuration |

These descriptions reflect the intended architecture. A module's presence does not guarantee that its functionality is complete.

---

## 7. Architectural rules

The engine follows explicit dependency boundaries:

1. **Contracts remain independent:** `vse/contracts/` must not depend on other VSE implementation modules.
2. **Observers depend only on contracts:** observer implementations must not directly depend on the registry, planner, executor, or other engine internals.
3. **Registry owns file access:** provider and configuration file-reading responsibilities belong in the registry.
4. **Runners remain independent of planning and registry internals:** runners execute work through defined interfaces rather than directly accessing those layers.
5. **The API coordinates external engines:** only the API layer should communicate directly with other engines, according to the architecture specification.

These boundaries make individual components easier to test, maintain, and replace.

---

## 8. Run the automated tests

Ensure your virtual environment is active, then run:

```bash
python -m pytest
```

To run a particular test file:

```bash
python -m pytest tests/test_smoke.py
```

To run tests with more detailed output:

```bash
python -m pytest -v
```

The test suite currently includes a package-import smoke test and an architecture-boundary test. Additional behavioral tests should be added as the engine's modules are implemented.

A passing test suite only confirms the behavior covered by the existing tests; it does not establish that every planned engine feature works.

---

## 9. Check architecture boundaries

Run import-linter from the activated virtual environment:

```bash
lint-imports
```

This checks the configured import contracts and reports whether they are kept or broken.

If the command is not found, activate `.venv` and reinstall the development dependencies:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

The file-access boundary also has a basic AST-based test in `tests/test_architecture_boundaries.py`. It is an initial safeguard, not a complete detector of every possible filesystem operation.

---

## 10. Continuous integration

The GitHub Actions workflow is configured to run on pushes and pull requests.

It performs the following steps:

1. Checks out the repository.
2. Sets up Python.
3. Installs the project and development dependencies.
4. Runs pytest.
5. Runs import-linter.

Before submitting changes, run the test and architecture checks locally. Also check the Actions tab on GitHub to confirm that the workflow completed successfully for your branch.

---

## 11. Development workflow

When adding or modifying functionality:

1. Read the relevant module and its architecture responsibilities.
2. Define or reuse shared contracts in `vse/contracts/`.
3. Implement functionality in the appropriate package without violating dependency boundaries.
4. Add behavioral tests under the matching `tests/` subdirectory.
5. Run pytest and import-linter.
6. Review the changes with `git diff`.
7. Commit and push the changes to your working branch.

Useful Git commands:

```bash
git status
git diff
git add .
git commit -m "Describe the change"
git push
```

Review `git status` and `git diff` before staging files to avoid committing temporary files, virtual environments, or unrelated changes.

---

## 12. Troubleshooting

### `ModuleNotFoundError`

Activate the virtual environment and install the project:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

### `lint-imports: command not found`

Ensure the development dependencies are installed in the active virtual environment:

```bash
python -m pip install -e ".[dev]"
```

### Tests fail after changing a module

Read the failure traceback, identify the affected contract or test, and fix the underlying issue. Do not weaken an architecture rule simply to make the tests pass.

### Dependency installation fails

Check the Python version and pip output. Some dependency versions may not provide compatible wheels for every Python version or platform. Follow the project's pinned configuration and investigate compatibility before changing versions.

---

## 13. Current development status

The initial repository scaffold, pinned dependency configuration, import-linter contracts, basic tests, and GitHub Actions workflow have been established.

The next development work is to implement the engine's contracts and behavior, expand meaningful tests, strengthen the registry-only file-access enforcement, and verify CI results on GitHub.

Contributors should consult the architecture specification, especially §13, before adding modules or changing dependency boundaries.
