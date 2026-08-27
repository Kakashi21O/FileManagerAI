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

## Development Progress (Phase 1)

- [x] **Part 1 — Data Models**: `FileNode`, `FolderNode`, and `ScanResult` defined with dataclasses.
- [x] **Part 2 — Path Handling**: Path utility functions in `core/path_utils.py`.
- [x] **Part 3 — Basic Scanner**: Directory scanning with `FileScanner` in `core/scanner.py`.
- [x] **Part 4 — Recursive Scanner & Config**: Recursive directory walking with YAML config loading in `core/config_loader.py`.
- [x] **Part 5 — Tree Builder & Traversal**: Tree integrity validation and recursive in-memory traversal generator in `core/tree_builder.py`.
- [ ] **Part 6 — Statistics & Metrics**: Calculating file counts, total sizes, and folder depth metrics.
- [ ] **Part 7 — Structural Detection**: Detecting empty folders, redundant nesting, deep paths, and project folders.
- [ ] **Part 8 — Health Checking & Reporting**: Summary health scoring and generating readable reports.

## Running Tests

Run the test suite using pytest:

```powershell
python -m pytest
```

Currently passing: **15 tests**

## Future

The next phases will add:

* File and folder organization
* Structure optimization
* Content analysis
* AI
* Safe file operations
* GUI
* Automation

