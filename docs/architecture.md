# Architecture Overview

## Design Goals

The RPM Spec Editor is designed to:

- Separate UI, logic, and data layers
- Provide extensibility for spec analysis features
- Maintain testability of core parsing logic

---

## High-Level Architecture

UI Layer (PyQt)
↓
Controller Layer (AppController)
↓
Service Layer (Parser / Analyzer / IO)
↓
Model Layer (Spec representation)

---

## Components

### 1. GUI Layer (`gui/`)

Responsible for:

- Main window
- Tree views of spec structure
- Text editor widget
- Settings dialog

Does NOT contain business logic.

---

### 2. Controller (`core/app_controller.py`)

Acts as mediator:

- Handles UI events
- Coordinates services
- Maintains application state

---

### 3. Services (`services/`)

Core logic:

- Spec parser (tokenizes RPM spec file)
- Analyzer (validates structure, dependencies)
- File I/O handler

---

### 4. Models (`models/`)

Structured representation of spec files:

- SpecFile
- Section
- Macro
- Dependency nodes

---

### 5. Settings System

- Stored in JSON
- Loaded at startup
- Applied dynamically in runtime

---

## Data Flow Example

1. User opens `.spec` file
2. Controller sends file to parser
3. Parser returns structured model
4. GUI renders tree + text editor
5. User edits → changes propagate back to model

---

## Extension Points

- Plugin system for analyzers
- Custom macro interpreters
- External linting tools integration
