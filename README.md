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

## Phase 2 — Organization & Safety

Phase 2 adds intelligent, safe organization planning and execution.

### Absolute Safety Rules
- **DELETE = NEVER**: The application never deletes files or folders.
- **Dry-Run by Default**: Simulates planning operations without altering the filesystem.
- **Review Area**: Candidate duplicates and uncertain files are moved to `_FileManagerAI_Review/{Duplicates, Similar, Uncertain}` with reasons for human verification.
- **Zero Silent Overwrites**: Collision resolution with non-destructive version numbering (`_1`, `_2`).
- **Project Protection**: Recognizes standalone projects and keeps internal subdirectories intact.
- **Streaming Hasher**: Memory-bounded chunked hashing ($O(1)$ RAM) for handling large files safely.

## CLI Usage

```powershell
# Dry-run analysis and plan preview (safe, no changes)
python app.py --path "path/to/folder"

# Apply plan safely to disk
python app.py --path "path/to/folder" --apply
```

## Development Progress

### Phase 1 (Scanning & Analysis)
- [x] **Part 1 — Data Models**: `FileNode`, `FolderNode`, and `ScanResult`
- [x] **Part 2 — Path Handling**: Path utilities in `core/path_utils.py`
- [x] **Part 3 — Basic Scanner**: Scanning directories with `FileScanner`
- [x] **Part 4 — Recursive Scanner & Config**: Config-driven nested tree scanning
- [x] **Part 5 — Tree Builder & Traversal**: Integrity validation & generator traversal
- [x] **Part 6 — Statistics & Metrics**: `core/statistics.py`
- [x] **Part 7 — Structural Detection**: `core/detector.py`
- [x] **Part 8 — Health Checking & Reporting**: `core/health.py`, `core/report.py`, `core/analyzer.py`

### Phase 2 (Organization & Safety Engine)
- [x] **Streaming Hasher**: `core/hashing.py` (chunked SHA-256)
- [x] **Duplicate Candidate Detection**: `core/duplicate_detector.py` ($O(n)$ candidate grouping)
- [x] **Extensible Category Rules**: `core/rules.py` (Code, Images, Documents, Data, Archives)
- [x] **Review Area Manager**: `core/review.py`
- [x] **Organization Planner**: `core/planner.py` (Generates non-destructive plans)
- [x] **Safety Validator & Collision Handling**: `core/safety.py`
- [x] **Transaction Logging & Execution Engine**: `core/transaction.py` and `core/executor.py`
- [x] **Future Similarity Documentation**: `docs/future_similarity.md`

## Running Tests

Run the test suite using pytest:

```powershell
python -m pytest
```

Currently passing: **39 tests**


