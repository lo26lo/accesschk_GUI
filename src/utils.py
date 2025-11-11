#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utility functions for AccessChk GUI.

This module provides various helper functions for encoding, path extraction,
user information, and text processing.

Functions:
    current_user_principal: Get current user in DOMAIN\\User format
    decode_bytes_with_fallback: Decode bytes with multiple encoding fallbacks
    extract_first_path: Extract first Windows/UNC path from text
    bundled_accesschk_path: Get path to accesschk.exe
    default_targets_string: Get default scan targets
    matches_suppressed_error: Check if text matches known error messages
"""

import os
import sys
import re
import unicodedata
import getpass
import logging
from pathlib import Path
from typing import Optional

from src.config import AppConfig

__all__ = [
    'current_user_principal',
    'decode_bytes_with_fallback',
    'extract_first_path',
    'bundled_accesschk_path',
    'default_targets_string',
    'matches_suppressed_error',
]

logger = logging.getLogger(__name__)

# Regex patterns
LINE_RW_PREFIX = re.compile(r"^\s*RW\s+", re.I)
WRITE_REGEX = re.compile(r"(?:^|\s)(rw|w|write|write_data|file_write_data|file_write|:w|W:|WriteData|FILE_WRITE_DATA)\b", re.I)
PATH_EXTRACT = re.compile(r"(?:[A-Za-z]:\\|\\\\[^\\]+\\)[^\r\n]*")
ASCII_ALNUM = re.compile(r"[A-Za-z0-9]")
CJK_CHARS = re.compile(r"[\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\uAC00-\uD7AF]")

# Suppressed error messages (normalized)
SUPPRESSED_ERROR_FOLDED_SNIPPETS = (
    "error getting security",
    "la syntaxe du nom de fichier",
    "repertoire ou de volume est incorrecte",
    "has a non-canonical dacl",
    "explicit deny after explicit allow", 
    "explicit allow after inherited allow",
    "access denied",
    "path not found",
    "fichier introuvable",
    "acces refuse",
    "the system cannot find",
    "le systeme ne peut pas localiser",
    "error:",
    "erreur:",
)


def current_user_principal() -> str:
    """Get current user in DOMAIN\\User format.
    
    Best-effort resolution of the current user. On Windows, attempts to
    get the domain and username. Falls back to username only if domain
    is unavailable.
    
    Returns:
        str: User principal in DOMAIN\\User format, or just username
        
    Example:
        >>> user = current_user_principal()
        >>> print(user)  # "WORKGROUP\\john" or "john"
    """
    try:
        user_env = os.environ.get("USERNAME")
    except (KeyError, OSError) as e:
        logger.warning(f"Impossible de récupérer USERNAME depuis l'environnement: {e}")
        user_env = None
    
    try:
        user = user_env or getpass.getuser()
    except (OSError, KeyError, ImportError) as e:
        logger.warning(f"Impossible de récupérer l'utilisateur courant: {e}")
        user = user_env or ""
    
    if os.name == "nt":
        try:
            domain = os.environ.get("USERDOMAIN")
            if domain and user:
                return f"{domain}\\{user}"
        except (KeyError, OSError) as e:
            logger.warning(f"Impossible de récupérer le domaine: {e}")
    
    return user


def _normalize_for_error_matching(text: str) -> str:
    """Return a lower-cased ASCII approximation of text for robust matching.
    
    This function normalizes Unicode text to make it easier to match
    against known error messages, handling accented characters and
    various Unicode forms.
    
    Args:
        text: Text to normalize
        
    Returns:
        str: Normalized lowercase text
    """
    try:
        normalized = unicodedata.normalize("NFKD", text)
    except (ValueError, TypeError) as e:
        logger.warning(f"Erreur de normalisation Unicode: {e}")
        normalized = text
    
    try:
        stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return stripped.casefold()
    except (ValueError, TypeError) as e:
        logger.warning(f"Erreur lors du traitement des caractères: {e}")
        return text.lower()


def matches_suppressed_error(text: str) -> bool:
    """Check if text matches a known noisy AccessChk error message.
    
    This function identifies common AccessChk error messages that
    should be filtered out from the display (syntax errors, access
    denied, file not found, etc.).
    
    Args:
        text: Error message text to check
        
    Returns:
        bool: True if this is a known error to suppress
        
    Example:
        >>> if matches_suppressed_error(line):
        ...     continue  # Skip this line
    """
    # Fast keyword-based checks (faster than regex)
    text_lower = text.lower()
    fast_keywords = [
        'syntaxe', 'répertoire', 'repertoire', 'incorrecte',
        'canonical', 'explicit', 'denied', 'security',
        'introuvable', 'refusé', 'refuse', 'cannot find', 'error:', 'erreur:'
    ]
    
    if any(keyword in text_lower for keyword in fast_keywords):
        return True
    
    # Fallback to normalized matching for edge cases
    folded = _normalize_for_error_matching(text)
    return any(snippet in folded for snippet in SUPPRESSED_ERROR_FOLDED_SNIPPETS)


def extract_first_path(s: str) -> Optional[str]:
    """Extract first Windows/UNC path from text.
    
    Extracts the first occurrence of a Windows path (C:\\...) or
    UNC path (\\\\server\\share\\...) from the given text.
    
    Args:
        s: Text potentially containing a path
        
    Returns:
        Optional[str]: First path found, or None
        
    Example:
        >>> path = extract_first_path("RW C:\\Windows\\System32")
        >>> print(path)  # "C:\\Windows\\System32"
    """
    if not s or not isinstance(s, str):
        return None
    
    try:
        m = PATH_EXTRACT.search(s)
        return m.group(0).strip().rstrip('"') if m else None
    except (AttributeError, IndexError) as e:
        logger.debug(f"Erreur lors de l'extraction du chemin: {e}")
        return None


def bundled_accesschk_path() -> str:
    """Get path to accesschk.exe bundled with the application.
    
    Returns the path to accesschk.exe located in the tools/ directory
    relative to the application root.
    
    Returns:
        str: Absolute path to accesschk.exe
        
    Example:
        >>> path = bundled_accesschk_path()
        >>> print(path)  # "C:\\...\\accesschk_GUI\\tools\\accesschk.exe"
    """
    # Running as script - go up from src/ to project root
    base = Path(__file__).parent.parent
    
    # Look for accesschk.exe in tools/ subdirectory
    tools_path = base / "tools" / "accesschk.exe"
    if tools_path.exists():
        return str(tools_path)
    
    # Fallback to project root (backward compatibility)
    return str(base / "accesschk.exe")


def decode_bytes_with_fallback(b: bytes) -> str:
    """Decode bytes with optimized encoding detection.
    
    Attempts to decode bytes using accesschk.exe's typical encodings:
    UTF-16 LE (with BOM), CP850, then UTF-8. This optimized order reflects
    the actual behavior of accesschk.exe on Windows systems.
    
    Args:
        b: Bytes to decode
        
    Returns:
        str: Decoded string
        
    Example:
        >>> output = decode_bytes_with_fallback(process.stdout)
        >>> print(output)
    """
    if not isinstance(b, bytes):
        logger.warning(f"Type inattendu pour le décodage: {type(b)}")
        return str(b)
    
    # Fast path: UTF-16 LE with BOM (common for accesschk.exe)
    if b.startswith(b'\xff\xfe'):
        try:
            return b.decode("utf-16-le", errors="strict")
        except (UnicodeDecodeError, LookupError):
            pass
    
    # Try most common encodings for accesschk.exe
    for enc in ("cp850", "utf-8", "latin-1"):
        try:
            return b.decode(enc, errors="strict")
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Fallback with replacement
    return b.decode("latin-1", errors="replace")


def default_targets_string() -> str:
    """Get default scan targets based on platform.
    
    Returns:
        str: Default target path (C:\\ on Windows, / on Unix)
        
    Example:
        >>> targets = default_targets_string()
        >>> print(targets)  # "C:\\" on Windows
    """
    if os.name == "nt":
        return "C:\\"
    return os.path.sep
