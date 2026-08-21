# FileManagerAI

A Python project that analyzes a folder and understands its file and folder structure.

## Phase 1

Phase 1 is only for **scanning and analyzing**.

It does not move, rename, delete, or change any files.

### What it does

* Scans folders recursively
* Builds a folder tree
* Collects file information
* Calculates folder statistics
* Detects empty folders
* Detects unnecessary folder nesting
* Detects deep folder structures
* Detects possible project folders
* Checks folder health
* Creates an analysis report

### Basic Flow

```text
Select Folder
     ↓
Scan Files & Folders
     ↓
Build Folder Tree
     ↓
Analyze Structure
     ↓
Find Problems
     ↓
Generate Report
```

## Project Structure

```text
FileManagerAI/
├── app.py
├── core/
├── models/
├── config/
├── logs/
├── reports/
└── tests/
```

## Technologies

* Python
* pathlib
* dataclasses
* PyYAML
* pytest

## Important

Phase 1 is **read-only**.

The application will not:

* Move files
* Rename files
* Delete files
* Create folders
* Modify existing files

These features will be added in later phases.

## Future

The next phases will add:

* File and folder organization
* Structure optimization
* Content analysis
* AI
* Safe file operations
* GUI
* Automation
