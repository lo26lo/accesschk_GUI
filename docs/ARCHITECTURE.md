# Architecture Documentation - AccessChk GUI

**Version**: 1.10  
**Date**: 2025-01-XX  
**Status**: Production

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Project Structure](#project-structure)
4. [Module Descriptions](#module-descriptions)
5. [Dependency Graph](#dependency-graph)
6. [Data Flow](#data-flow)
7. [Design Patterns](#design-patterns)
8. [Security Architecture](#security-architecture)
9. [Performance Considerations](#performance-considerations)
10. [Testing Strategy](#testing-strategy)

---

## Overview

AccessChk GUI est une application Python/Tkinter structurée en modules indépendants pour faciliter la maintenance, les tests et l'évolution. L'architecture suit les principes SOLID avec une séparation claire entre configuration, validation, logique métier et interface utilisateur.

### Key Characteristics

- **Language**: Python 3.10+
- **GUI Framework**: Tkinter (stdlib)
- **Platform**: Windows-only (uses accesschk.exe from Sysinternals)
- **Pattern**: MVC-inspired with separated concerns
- **Threading**: Background scanner thread + main GUI thread
- **Persistence**: JSON-based history storage

---

## Architecture Principles

### 1. Separation of Concerns

Chaque module a une responsabilité unique :
- **config.py** : Configuration centralisée
- **validation.py** : Validation et sécurité
- **utils.py** : Utilitaires génériques
- **scanner.py** : Logique de scan AccessChk
- **export.py** : Exports multi-formats
- **history.py** : Persistance de l'historique
- **gui.py** : Interface utilisateur

### 2. Single Responsibility Principle (SRP)

Chaque classe/fonction a une seule raison de changer :
- `AppConfig` : Centralise les constantes
- `AccessChkRunner` : Exécute les scans
- `ExportManager` : Gère les exports
- `ScanHistoryManager` : Gère l'historique
- `AccessChkGUI` : Orchestre l'interface

### 3. Dependency Injection

Les dépendances sont injectées via constructeurs :
```python
runner = AccessChkRunner(config, queue)
history_mgr = ScanHistoryManager(storage_dir)
```

### 4. Fail-Safe Design

- Validation stricte des entrées utilisateur
- Gestion d'erreurs exhaustive avec logging
- Graceful degradation (cache de détection de répertoires)
- Cleanup automatique des ressources

---

## Project Structure

```
accesschk_GUI/
├── AccessChkGUI.py              # 🚀 Main entry point (launcher)
├── accesschk_gui_tk.py          # 🗂️ [LEGACY] Monolithic original (1852 lines)
│
├── src/                         # 📦 Source code modules
│   ├── __init__.py             # Package initialization
│   ├── config.py               # ⚙️ Configuration (AppConfig class)
│   ├── validation.py           # 🛡️ Input validation & security
│   ├── utils.py                # 🔧 Utility functions
│   ├── scanner.py              # 🔍 AccessChk scan execution
│   ├── export.py               # 📤 Multi-format export manager
│   ├── history.py              # 📊 Scan history persistence
│   └── gui.py                  # 🖥️ Tkinter GUI (main window)
│
├── tests/                       # 🧪 Unit tests
│   ├── __init__.py
│   ├── test_basic.py           # Basic functionality tests
│   ├── test_validation.py      # Validation tests
│   ├── test_filtering.py       # Filter logic tests
│   ├── test_features.py        # Feature integration tests
│   └── test_*.py               # Other test modules
│
├── docs/                        # 📚 Documentation
│   ├── ARCHITECTURE.md         # This file
│   ├── AMELIORATIONS.md        # Improvements & optimizations
│   └── NOUVELLES_FONCTIONNALITES.md  # New features
│
├── scripts/                     # 🛠️ Utility scripts
│   ├── build_gui.ps1           # PowerShell build script
│   ├── diagnostic_scan.py      # Diagnostic utility
│   └── simple_test.py          # Simple test runner
│
├── tools/                       # 🔨 External tools
│   ├── accesschk.exe           # Microsoft Sysinternals AccessChk
│   └── README.md               # Tool documentation
│
├── .gitignore                   # Git ignore rules
├── README.md                    # 📖 User documentation
├── MIGRATION.md                 # Migration guide
└── ETAT_MIGRATION.md            # Migration status

```

---

## Module Descriptions

### 📦 `src/__init__.py`
**Purpose**: Package initialization  
**Exports**: None (used for package detection)  
**Dependencies**: None

---

### ⚙️ `src/config.py`
**Purpose**: Centralized configuration constants

**Key Elements**:
- `AppConfig` class (Singleton pattern)
- UI dimensions and colors
- Performance tuning parameters
- File naming constants

**Configuration Categories**:
```python
# UI Layout
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
MIN_WIDTH = 800
MIN_HEIGHT = 600

# Performance
BATCH_SIZE = 100                    # Lines per UI update
BATCH_TIMEOUT_MS = 16               # ~60 FPS target
UI_UPDATE_INTERVAL_MS = 50          # Poll queue every 50ms
MAX_DISPLAYED_LINES = 10000         # Memory limit
PROGRESS_BAR_SPEED = 10             # Indeterminate animation

# Export
EXPORT_DEFAULT = "accesschk_filtered.txt"
DIFF_EXPORT_DEFAULT = "accesschk_diff.txt"
```

**Dependencies**: None (base module)

---

### 🛡️ `src/validation.py`
**Purpose**: Security validation and input sanitization

**Key Functions**:
- `is_running_elevated()` : Détecte les privilèges administrateur
- `validate_executable_path(path)` : Valide accesschk.exe
- `validate_target_paths(raw)` : Valide les cibles de scan
- `sanitize_command_args(args)` : Nettoie les arguments CLI

**Security Checks**:
1. **Executable validation**:
   - Path existence
   - .exe extension
   - Absolute path requirement
   - Size sanity check (<50MB)

2. **Target validation**:
   - Path existence
   - Forbidden patterns (`.`, `..`)
   - Absolute path requirement

3. **Command sanitization**:
   - Remove shell metacharacters
   - Quote dangerous characters
   - Prevent command injection

**Dependencies**: `src.config`

---

### 🔧 `src/utils.py`
**Purpose**: Generic utility functions

**Categories**:

1. **User Information**:
   - `current_user_principal()` : Get DOMAIN\\User format

2. **Encoding**:
   - `decode_bytes_with_fallback(bytes)` : Multi-encoding decoder (UTF-8/UTF-16/CP850/CP437/CP1252/Latin-1)

3. **Path Extraction**:
   - `extract_first_path(text)` : Extract Windows/UNC paths via regex

4. **Text Processing**:
   - `contains_cjk(text)` : Detect Chinese/Japanese/Korean characters
   - `matches_suppressed_error(text)` : Filter known error messages
   - `_normalize_for_error_matching(text)` : Unicode normalization

5. **Path Resolution**:
   - `bundled_accesschk_path()` : Find accesschk.exe in tools/
   - `default_targets_string()` : Platform-specific default (C:\\ or /)

**Regex Patterns**:
```python
LINE_RW_PREFIX = r"^\s*RW\s+"          # Detect RW lines
WRITE_REGEX = r"(rw|w|write|...)\b"    # Detect write permissions
PATH_EXTRACT = r"[A-Za-z]:\\|\\\\..."  # Extract file paths
CJK_CHARS = r"[\u3040-\u30FF...]"      # CJK character ranges
```

**Dependencies**: `src.config`

---

### 🔍 `src/scanner.py`
**Purpose**: AccessChk scan execution in background thread

**Key Class**: `AccessChkRunner`

**Responsibilities**:
- Spawn scan thread (daemon)
- Execute accesschk.exe with subprocess.Popen
- Process stdout/stderr line-by-line
- Handle multiple principals (fallback on invalid account)
- Throttle output when queue is full
- Thread-safe communication via queue.Queue

**Scan Lifecycle**:
```
start_scan() → _run_scan() → [for each target]
    → [for each principal]
        → _create_process()
        → _process_output()
            → [stdout/stderr readers threads]
            → queue.put({"line": ..., "write": ..., "err": ...})
    → queue.put({"_finished": True, "returncode": ...})
```

**Error Handling**:
- Invalid account → Try next principal (return code -2)
- Process errors → Log and report via queue
- Keyboard interrupt → Kill process gracefully

**Dependencies**: `src.config`, `src.validation`, `src.utils`

---

### 📤 `src/export.py`
**Purpose**: Multi-format export of scan results

**Key Class**: `ExportManager` (static methods)

**Supported Formats**:

1. **CSV**:
   ```csv
   timestamp,type,permissions,path,user
   2024-01-15T10:30:00,write,RW C:\Windows,C:\Windows,current_user
   ```

2. **JSON**:
   ```json
   {
     "export_timestamp": "2024-01-15T10:30:00",
     "total_entries": 42,
     "entries": [
       {
         "line": "RW C:\\Windows",
         "has_write": true,
         "is_error": false,
         "path": "C:\\Windows",
         "timestamp": "2024-01-15T10:30:00"
       }
     ]
   }
   ```

3. **XML**:
   ```xml
   <?xml version='1.0' encoding='utf-8'?>
   <accesschk_scan timestamp="2024-01-15T10:30:00" total_entries="42">
     <entry has_write="True" is_error="False">
       <line>RW C:\Windows</line>
       <path>C:\Windows</path>
     </entry>
   </accesschk_scan>
   ```

**Dependencies**: `src.utils`

---

### 📊 `src/history.py`
**Purpose**: Persistent scan history management

**Key Class**: `ScanHistoryManager`

**Storage Format**: JSON file (`scan_history.json`)

**Data Structure**:
```json
[
  {
    "timestamp": "2024-01-15T10:30:00",
    "scan_type": "baseline",
    "targets": ["C:\\Windows", "C:\\Program Files"],
    "principal": "Users",
    "result_count": 42
  }
]
```

**Features**:
- Auto-limit to 20 most recent entries
- Graceful error handling (no crash if corrupted)
- Atomic writes with JSON indentation

**Dependencies**: None (stdlib only)

---

### 🖥️ `src/gui.py`
**Purpose**: Main Tkinter GUI window

**Key Class**: `AccessChkGUI(tk.Tk)`

**Components**:

1. **Menu Bar**:
   - Fichier : Scans, Exclusions, Export, Historique, Quitter
   - Edition : Copier, Sélectionner tout, Effacer logs
   - Vue : Filtres, Recherche
   - Aide : Raccourcis, À propos

2. **Configuration Group**:
   - accesschk.exe path selector
   - Current user display

3. **Targets & Exclusions Group**:
   - Target input field (semicolon-separated)
   - Browse button
   - Exclusions manager

4. **Actions Group**:
   - Scan initial button
   - Scan comparison button
   - Stop button

5. **Filters Group**:
   - Text filter input
   - Folders-only checkbox
   - Export button

6. **Information Group**:
   - Command display
   - Progress bar (indeterminate)
   - Status label

7. **Log Display**:
   - Text widget with horizontal/vertical scrollbars
   - Color-coded tags (write=red, err=orange, normal=black)

**Event Loop**:
```
_poll_queue() (every 50ms)
    → queue.get_nowait() (batch processing)
    → Process items:
        - "_status" → Update status label
        - "_finished" → _finish_scan()
        - "line" → Parse, filter, append to logs
    → _update_display_batch() (render text widget)
    → after(50ms, _poll_queue)
```

**Scan Flow**:
```
_on_scan()
    → Validate inputs (executable, targets)
    → Filter exclusions
    → Reset state (logs, counters)
    → runner.start_scan()
    → Enable stop button
    → Start progress bar
```

**Dependencies**: `src.config`, `src.validation`, `src.utils`, `src.scanner`, `src.export`, `src.history`

---

## Dependency Graph

```
┌─────────────────┐
│ AccessChkGUI.py │  ◄── Main entry point
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ gui.py │  ◄── Main GUI window
    └───┬────┘
        │
        ├──► config.py        (Configuration)
        ├──► validation.py    (Security)
        ├──► utils.py         (Utilities)
        ├──► scanner.py       (Scan execution)
        │       └──► config.py
        │       └──► validation.py
        │       └──► utils.py
        ├──► export.py        (Export manager)
        │       └──► utils.py
        └──► history.py       (History manager)

Dependency Layers:
Layer 0: config.py (no dependencies)
Layer 1: validation.py, utils.py (depend on config)
Layer 2: scanner.py, export.py, history.py (depend on Layer 0-1)
Layer 3: gui.py (depends on all)
```

**Circular Dependencies**: None ✅

---

## Data Flow

### 1. Scan Initialization

```
User clicks "Scan initial"
    → GUI._on_scan()
        → validate_executable_path()
        → validate_target_paths()
        → Filter exclusions
        → runner.start_scan(accesschk, targets, principal)
            → Thread: _run_scan()
                → For each target:
                    → For each principal:
                        → _create_process() → subprocess.Popen
                        → _process_output()
                            → reader(stdout) → queue.put({"line": ..., "write": True/False})
                            → reader(stderr) → queue.put({"line": ..., "err": True})
```

### 2. Output Processing

```
GUI._poll_queue() (every 50ms)
    → Batch process queue items:
        1. Extract pending path (optimization)
        2. Check exclusions
        3. Filter suppressed errors
        4. Detect write permissions (WRITE_REGEX)
        5. Append to self.logs[]
        6. Buffer for display (buf_normal, buf_write, buf_err)
    → _update_display_batch()
        → txt.insert() with color tags
        → Smart scrolling (only if near bottom)
```

### 3. Scan Completion

```
scanner._process_output() finishes
    → queue.put({"_finished": True, "returncode": rc})
    → GUI._poll_queue() detects "_finished"
        → _finish_scan(rc)
            → history_manager.add_scan(...)
            → _persist_scan_results()
                → Save to scan_initial.txt or scan_comparatif.txt
                → If compare mode: _handle_compare_diff()
```

### 4. Comparison Diff

```
_handle_compare_diff()
    → Load scan_initial.txt
    → Load scan_comparatif.txt
    → _filter_lines_for_diff() (keep only directories and RW lines)
    → difflib.unified_diff()
    → Filter to keep only TRUE new RW rights:
        - Collect added (+) and removed (-) RW lines
        - Keep added lines NOT in removed (deduplicate moves)
    → _show_diff_window()
```

---

## Design Patterns

### 1. Singleton Pattern
**Where**: `AppConfig`  
**Why**: Single source of truth for configuration  
**Implementation**: Class with static attributes

### 2. Thread Pool Pattern
**Where**: `AccessChkRunner`  
**Why**: Non-blocking scan execution  
**Implementation**: `threading.Thread` with daemon flag

### 3. Producer-Consumer Pattern
**Where**: Scanner (producer) → GUI (consumer)  
**Why**: Thread-safe communication  
**Implementation**: `queue.Queue` with `get_nowait()`

### 4. Strategy Pattern
**Where**: `ExportManager` (CSV/JSON/XML)  
**Why**: Multiple export formats  
**Implementation**: Static methods with format-specific logic

### 5. Observer Pattern (implicit)
**Where**: GUI polling queue  
**Why**: React to scanner events  
**Implementation**: `after()` loop checking queue

### 6. Facade Pattern
**Where**: `AccessChkGUI`  
**Why**: Simplify complex subsystem interactions  
**Implementation**: High-level methods orchestrating modules

---

## Security Architecture

### Threat Model

**Assets**:
- User file system
- Scan results (may contain sensitive paths)
- Application integrity

**Threats**:
1. **Command Injection** : Malicious target paths
2. **Path Traversal** : Access outside intended directories
3. **Privilege Escalation** : Running as admin
4. **Information Disclosure** : Exposing sensitive system info

### Security Controls

1. **Input Validation** (`validation.py`):
   - Whitelist approach for executable paths
   - Forbidden characters/patterns (`.`, `..`, `|`, `&`, `;`)
   - Absolute path requirement

2. **Command Sanitization**:
   - `sanitize_command_args()` removes shell metacharacters
   - Arguments passed as list (not shell string)
   - `subprocess.Popen()` with `shell=False`

3. **Privilege Restriction**:
   - `is_running_elevated()` detects admin rights
   - Application exits if elevated
   - Rationale: Prevent scanning as admin (security audit requirement)

4. **Error Filtering**:
   - `matches_suppressed_error()` hides sensitive errors
   - Prevents information leakage via error messages

5. **Resource Limits**:
   - `MAX_DISPLAYED_LINES` prevents memory exhaustion
   - Queue throttling when backlog >500 items
   - Subprocess timeout (implicit via poll)

---

## Performance Considerations

### Optimizations

1. **Batch Processing**:
   ```python
   BATCH_SIZE = 100  # Process 100 lines per UI update
   BATCH_TIMEOUT_MS = 16  # ~60 FPS target
   ```
   **Impact**: Reduces Tkinter redraws, smoother UI

2. **Queue Throttling**:
   ```python
   if self.queue.qsize() > 500:
       time.sleep(0.001)
   ```
   **Impact**: Prevents queue from growing unbounded

3. **Directory Cache**:
   ```python
   self._isdir_cache = {}  # Cache os.path.isdir() results
   ```
   **Impact**: Avoids redundant filesystem calls

4. **Smart Scrolling**:
   ```python
   # Only scroll if user is viewing bottom 5 lines
   if (total_lines - visible_end) < 5:
       self.txt.see(tk.END)
   ```
   **Impact**: Preserves user scroll position

5. **Memory Management**:
   ```python
   if len(self.logs) >= MAX_DISPLAYED_LINES:
       # Keep important lines (RW) + recent sample
       important_lines = [... if item["write"]][-500:]
       recent_lines = self.logs[-300:]
   ```
   **Impact**: Caps memory usage at ~10k lines

### Bottlenecks

1. **Tkinter Text Widget**:
   - Inserting 10k+ lines is slow
   - Mitigation: Batch inserts, limit display

2. **Subprocess Output**:
   - accesschk.exe can generate MB of output
   - Mitigation: Stream processing, regex filtering

3. **os.path.isdir()**:
   - Called for every path in filters
   - Mitigation: `_isdir_cache` dictionary

---

## Testing Strategy

### Unit Tests (`tests/`)

**Coverage Goals**: >80% for core modules

**Test Categories**:

1. **Validation Tests** (`test_validation.py`):
   - Valid/invalid executable paths
   - Target path validation
   - Sanitization edge cases
   - Elevation detection

2. **Filtering Tests** (`test_filtering.py`):
   - Text filter matching
   - Folders-only logic
   - Exclusion patterns
   - Diff generation

3. **Feature Tests** (`test_features.py`):
   - Export to CSV/JSON/XML
   - History management
   - Path extraction
   - Error suppression

4. **Integration Tests** (`test_suite.py`):
   - End-to-end scan workflow
   - GUI state transitions
   - Thread safety

**Test Fixtures**:
```python
@pytest.fixture
def sample_logs():
    return [
        {"line": "RW C:\\Windows", "write": True, "err": False},
        {"line": "R  C:\\Program Files", "write": False, "err": False},
        {"line": "[ERROR] Access denied", "write": False, "err": True}
    ]
```

### Manual Testing Checklist

- [ ] Launch with standard user (non-admin)
- [ ] Launch with admin (should exit with error)
- [ ] Select accesschk.exe via Browse
- [ ] Add/remove exclusions
- [ ] Scan single target (C:\\Windows)
- [ ] Scan multiple targets (C:\\;D:\\)
- [ ] Stop scan mid-execution
- [ ] Filter results (text + folders-only)
- [ ] Export to TXT/CSV/JSON/XML
- [ ] Baseline scan → Compare scan → View diff
- [ ] View history
- [ ] Clear history
- [ ] Keyboard shortcuts (Ctrl+N, Ctrl+R, Ctrl+F, etc.)
- [ ] Context menu (right-click)

---

## Future Architecture Improvements

### Short-Term (v1.11)

1. **Async/Await Refactoring**:
   - Replace threading with `asyncio`
   - Use `asyncio.Queue` for cleaner async code

2. **Plugin System**:
   - Abstract export formats as plugins
   - Allow custom exporters without modifying core

3. **Configuration File**:
   - Replace hardcoded `AppConfig` with YAML/TOML
   - Allow user customization

### Medium-Term (v2.0)

1. **Web Interface**:
   - Flask/FastAPI backend
   - React/Vue frontend
   - WebSocket for real-time updates

2. **Database Backend**:
   - SQLite for history and results
   - Full-text search on scan data

3. **Multi-Platform Support**:
   - Linux: Use `getfacl` instead of accesschk.exe
   - macOS: Use `ls -le` for ACLs

### Long-Term (v3.0)

1. **Microservices Architecture**:
   - Scanner service
   - Export service
   - History service
   - API gateway

2. **Machine Learning**:
   - Anomaly detection in permission changes
   - Recommendation engine for exclusions

---

## Appendix

### A. Module Size

| Module | Lines | Classes | Functions |
|--------|-------|---------|-----------|
| config.py | 77 | 1 | 0 |
| validation.py | 213 | 0 | 4 |
| utils.py | 292 | 0 | 8 |
| scanner.py | 265 | 1 | 0 |
| export.py | 179 | 1 | 0 |
| history.py | 167 | 1 | 0 |
| gui.py | 1223 | 1 | 0 |
| **TOTAL** | **2416** | **5** | **12** |

### B. External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| Tkinter | stdlib | GUI framework |
| accesschk.exe | Latest | Microsoft Sysinternals tool |

**Zero external PyPI dependencies** ✅

### C. Key Metrics

- **Cyclomatic Complexity**: <10 for most functions
- **Maintainability Index**: >60 (Good)
- **Code Coverage**: 75% (target: 80%)
- **Technical Debt**: Low (recent refactoring)

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Maintainers**: AccessChk GUI Development Team
