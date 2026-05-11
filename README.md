# RPM Spec Editor

A desktop application for creating, editing, and analyzing RPM `.spec` files with structured navigation, syntax highlighting, and semantic validation support.

## Features

- Create, open, edit, and save RPM spec files
- Structured tree view of spec file components
- Syntax highlighting for RPM spec format
- Metadata and section-aware editor
- Settings persistence (paths, logging, automation options)
- Modular architecture (MVC-style separation)

## Technology Stack

- Python 3.10+
- PyQt6 (or PySide6 depending on build)
- RPM spec parsing logic (custom)
- Settings management system (JSON-based)

## Project Structure

rpm-spec-editor/
├── src/rpm_spec_editor/
│ ├── gui/ # UI components
│ ├── core/ # business logic / controller
│ ├── models/ # data models
│ ├── services/ # parsing, IO, analysis
│ ├── config/ # settings management
│ └── app.py # entry point
├── docs/
├── tests/
├── pyproject.toml
└── README.md

## Installation

```bash
git clone https://github.com/xewca/RPM-Spec-Editor.git
cd RPM-Spec-Editor
pip install -e .
```

## MIT License

---

# 📦 `pyproject.toml` (modern setuptools-based)

This assumes a standard Python packaging approach.

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "rpm-spec-editor"
version = "0.1.0"
description = "GUI tool for editing and analyzing RPM spec files"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "RPM Spec Editor Contributors"}
]
requires-python = ">=3.10"

dependencies = [
    "PyQt6",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
    "mypy"
]

[project.scripts]
rpm-spec-editor = "rpm_spec_editor.app:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```
