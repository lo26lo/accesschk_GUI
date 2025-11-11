#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main GUI module for AccessChk application.

This module provides the AccessChkGUI class, which is the main Tkinter
window for the application with all user interface components and
interaction logic.

Classes:
    AccessChkGUI: Main application window (inherits from tk.Tk)
"""

import os
import sys
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import difflib
import logging
from datetime import datetime
from typing import List, Dict, Optional

from src.config import AppConfig
from src.validation import is_running_elevated, validate_executable_path, validate_target_paths
from src.utils import (
    current_user_principal,
    extract_first_path,
    matches_suppressed_error,
    bundled_accesschk_path,
    default_targets_string,
    LINE_RW_PREFIX,
    WRITE_REGEX,
    ASCII_ALNUM
)
from src.scanner import AccessChkRunner
from src.export import ExportManager
from src.history import ScanHistoryManager

__all__ = ['AccessChkGUI']

logger = logging.getLogger(__name__)


class AccessChkGUI(tk.Tk):
    """Main window managing all user interactions.
    
    This class provides the complete graphical interface for AccessChk
    including menu bar, configuration fields, scan controls, output
    display, and export functionality.
    
    Attributes:
        app_config: Application configuration
        q: Queue for thread-safe communication with scanner
        runner: AccessChkRunner instance for scan execution
        history_manager: ScanHistoryManager for persistent history
        export_manager: ExportManager for multi-format exports
        logs: List of scan output lines
        running: Boolean flag for scan state
        scan_mode: Current scan mode ("baseline", "compare", None)
        
    Example:
        >>> app = AccessChkGUI()
        >>> app.mainloop()
    """

    def __init__(self):
        """Initialize interface and in-memory data structures."""
        super().__init__()
        self.title("AccessChk GUI v1.10")
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.minsize(AppConfig.MIN_WIDTH, AppConfig.MIN_HEIGHT)
        
        # File paths - Use current directory or script directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.storage_dir = base_dir
        self.base_scan_path = os.path.join(base_dir, "scan_initial.txt")
        self.compare_scan_path = os.path.join(base_dir, "scan_comparatif.txt")
        self.diff_output_path = os.path.join(base_dir, "scan_diff.txt")
        
        # Configuration and components
        self.app_config = AppConfig()
        self.q = queue.Queue()
        self.runner = AccessChkRunner(self.app_config, self.q)
        self.history_manager = ScanHistoryManager(base_dir)
        self.export_manager = ExportManager()
        
        # Application state
        from collections import deque
        self.logs = deque(maxlen=self.app_config.MAX_DISPLAYED_LINES)
        self.running = False
        self.scan_mode = None
        
        # Metrics and cache
        self._line_count = 0
        self._write_count = 0
        self._isdir_cache = {}
        self._suppressed_errors = 0
        self._pending_path = None
        
        # Scan state
        self.current_target = None
        self.current_principal = None
        self.default_principal = current_user_principal()
        self.scan_mode = None
        
        # Clean up leftover temporary files
        for leftover in (self.compare_scan_path, self.diff_output_path):
            try:
                if os.path.isfile(leftover):
                    os.remove(leftover)
            except (OSError, IOError) as e:
                logger.warning(f"Cannot delete {leftover}: {e}")
        
        self._build_ui()
        self.after(self.app_config.UI_UPDATE_INTERVAL_MS, self._poll_queue)

    def _build_ui(self) -> None:
        """Build all widgets of the main window."""

        menubar = tk.Menu(self)
        
        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Nouveau scan initial", command=lambda: self._on_scan("baseline"), accelerator="Ctrl+N")
        filemenu.add_command(label="Scan de comparaison", command=lambda: self._on_scan("compare"), accelerator="Ctrl+R")
        filemenu.add_separator()
        
        # Export submenu
        exportmenu = tk.Menu(filemenu, tearoff=0)
        exportmenu.add_command(label="Export TXT", command=self._export_filtered, accelerator="Ctrl+E")
        exportmenu.add_command(label="Export CSV", command=self._export_csv)
        exportmenu.add_command(label="Export JSON", command=self._export_json)
        exportmenu.add_command(label="Export XML", command=self._export_xml)
        filemenu.add_cascade(label="Exporter", menu=exportmenu)
        
        filemenu.add_command(label="Historique des scans", command=self._show_history)
        filemenu.add_separator()
        filemenu.add_command(label="Quitter", command=self.on_close, accelerator="Ctrl+Q")
        menubar.add_cascade(label="Fichier", menu=filemenu)
        
        # Edit menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Copier sélection", command=self._copy_selection, accelerator="Ctrl+C")
        editmenu.add_command(label="Sélectionner tout", command=self._select_all, accelerator="Ctrl+A")
        editmenu.add_separator()
        editmenu.add_command(label="Effacer logs", command=self._clear_logs, accelerator="Ctrl+L")
        menubar.add_cascade(label="Edition", menu=editmenu)
        
        # View menu
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Afficher seulement dossiers", command=self._toggle_folders_only, accelerator="Ctrl+D")
        viewmenu.add_command(label="Rechercher", command=self._focus_filter, accelerator="Ctrl+F")
        menubar.add_cascade(label="Vue", menu=viewmenu)
        
        # Help menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Aide sur 'Principal'...", command=self._show_principal_help)
        helpmenu.add_command(label="Raccourcis clavier", command=self._show_shortcuts_help, accelerator="F1")
        helpmenu.add_command(label="À propos", command=self._show_about)
        menubar.add_cascade(label="Aide", menu=helpmenu)
        
        self.config(menu=menubar)

        # Keyboard shortcuts
        self._setup_keyboard_shortcuts()

        ttk.Label(self, text="Cette application doit être lancée avec un utilisateur standard. L'utilisateur courant sera utilisé automatiquement.",
                  foreground="firebrick").pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 0))

        frm_top = ttk.Frame(self); frm_top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)

        # === CONFIGURATION GROUP ===
        config_group = ttk.LabelFrame(frm_top, text="Configuration", padding=10)
        config_group.pack(fill=tk.X, pady=(0,8))
        
        # AccessChk.exe
        ttk.Label(config_group, text="accesschk.exe :").grid(row=0, column=0, sticky=tk.W, padx=(0,6))
        self.entry_accesschk = ttk.Entry(config_group, width=60)
        self.entry_accesschk.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(0,6))
        self.entry_accesschk.insert(0, bundled_accesschk_path())
        ttk.Button(config_group, text="Parcourir", command=self._browse_accesschk).grid(row=0, column=2)
        
        # User
        ttk.Label(config_group, text="Utilisateur courant :").grid(row=1, column=0, sticky=tk.W, padx=(0,6), pady=(6,0))
        self.var_principal = tk.StringVar(value=self.default_principal or "(introuvable)")
        ttk.Label(config_group, textvariable=self.var_principal, foreground="blue").grid(row=1, column=1, sticky=tk.W, pady=(6,0))
        
        # Configure grid for resizing
        config_group.columnconfigure(1, weight=1)

        # === TARGETS GROUP ===
        targets_group = ttk.LabelFrame(frm_top, text="Cibles du Scan", padding=10)
        targets_group.pack(fill=tk.X, pady=(0,8))
        
        # Targets
        ttk.Label(targets_group, text="Cibles (séparer par ;) :").grid(row=0, column=0, sticky=tk.W, padx=(0,6))
        self.entry_target = ttk.Entry(targets_group, width=60)
        self.entry_target.grid(row=0, column=1, sticky=tk.W+tk.E, padx=(0,6))
        self.entry_target.insert(0, default_targets_string())
        
        # Target buttons
        ttk.Button(targets_group, text="Parcourir", command=self._browse_target_replace).grid(row=0, column=2, padx=(0,6))
        
        # Configure grid for resizing
        targets_group.columnconfigure(1, weight=1)

        # === ACTIONS GROUP ===
        actions_group = ttk.LabelFrame(frm_top, text="Actions", padding=10)
        actions_group.pack(fill=tk.X, pady=(0,8))
        
        # Scan buttons
        scan_frame = ttk.Frame(actions_group)
        scan_frame.pack(anchor=tk.W)
        
        self.btn_scan_base = ttk.Button(scan_frame, text="🔍 Scan initial", command=lambda: self._on_scan("baseline"))
        self.btn_scan_base.pack(side=tk.LEFT, padx=(0,8))
        
        self.btn_scan_compare = ttk.Button(scan_frame, text="🔄 Scan comparaison", command=lambda: self._on_scan("compare"))
        self.btn_scan_compare.pack(side=tk.LEFT, padx=(0,8))
        
        self.btn_stop = ttk.Button(scan_frame, text="⏹️ Stop", command=self._on_stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT)

        # === FILTERS GROUP ===
        frm_filter = ttk.LabelFrame(self, text="Filtres et Export", padding=10)
        frm_filter.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(0,6))
        
        # Filter row
        filter_row = ttk.Frame(frm_filter)
        filter_row.pack(fill=tk.X, pady=(0,5))
        
        ttk.Label(filter_row, text="Filtre :").pack(side=tk.LEFT)
        self.var_filter = tk.StringVar()
        self.entry_filter = ttk.Entry(filter_row, textvariable=self.var_filter, width=40)
        self.entry_filter.pack(side=tk.LEFT, padx=(6,12))
        self.entry_filter.bind("<KeyRelease>", lambda e: self._render_logs())
        
        self.var_only_folders = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_row, text="Dossiers seulement", variable=self.var_only_folders, command=self._render_logs).pack(side=tk.LEFT, padx=(0,12))
        
        ttk.Button(filter_row, text="📤 Export (filtered)", command=self._export_filtered).pack(side=tk.RIGHT)

        # === INFORMATION GROUP ===
        info_group = ttk.LabelFrame(self, text="Informations", padding=10)
        info_group.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(0,6))
        
        # Command display area
        cmd_frame = ttk.Frame(info_group)
        cmd_frame.pack(fill=tk.X, pady=(0,5))
        ttk.Label(cmd_frame, text="Commande :").pack(side=tk.LEFT)
        self.cmd_var = tk.StringVar(value="Aucune commande lancée")
        cmd_label = ttk.Label(cmd_frame, textvariable=self.cmd_var, foreground="blue", font=("TkDefaultFont", 9))
        cmd_label.pack(side=tk.LEFT, padx=(6,0), fill=tk.X, expand=True)
        
        # Progress bar and status
        progress_frame = ttk.Frame(info_group)
        progress_frame.pack(fill=tk.X)
        self.pbar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.pbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8))
        self.status_var = tk.StringVar(value="Prêt")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(side=tk.RIGHT)

        frm_logs = ttk.Frame(self); frm_logs.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(0,8))
        self.txt = tk.Text(frm_logs, wrap=tk.NONE, state=tk.NORMAL); self.txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.txt.tag_configure("write", foreground="red", font=("TkDefaultFont", 10, "bold"))
        self.txt.tag_configure("err", foreground="orange red"); self.txt.tag_configure("normal", foreground="black")
        vscroll = ttk.Scrollbar(frm_logs, orient=tk.VERTICAL, command=self.txt.yview); vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt.config(yscrollcommand=vscroll.set)
        hscroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.txt.xview); hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt.config(xscrollcommand=hscroll.set)

        self.menu = tk.Menu(self, tearoff=0); self.menu.add_command(label="Copier", command=self._copy_selection)
        self.txt.bind("<Button-3>", self._show_context_menu)
        self._update_compare_state()

    def _setup_keyboard_shortcuts(self) -> None:
        """Configure keyboard shortcuts."""
        self.bind_all("<Control-n>", lambda e: self._on_scan("baseline"))
        self.bind_all("<Control-r>", lambda e: self._on_scan("compare"))
        self.bind_all("<Control-e>", lambda e: self._export_filtered())
        self.bind_all("<Control-q>", lambda e: self.on_close())
        self.bind_all("<Control-c>", lambda e: self._copy_selection())
        self.bind_all("<Control-a>", lambda e: self._select_all())
        self.bind_all("<Control-l>", lambda e: self._clear_logs())
        self.bind_all("<Control-d>", lambda e: self._toggle_folders_only())
        self.bind_all("<Control-f>", lambda e: self._focus_filter())
        self.bind_all("<F1>", lambda e: self._show_shortcuts_help())
        self.bind_all("<Escape>", lambda e: self._on_stop())

    def _focus_filter(self) -> None:
        """Set focus on filter field."""
        try:
            self.entry_filter.focus_set()
            self.entry_filter.select_range(0, tk.END)
        except AttributeError:
            pass

    def _clear_logs(self) -> None:
        """Clear all displayed logs."""
        if not self.running and messagebox.askyesno("Effacer les logs", "Êtes-vous sûr de vouloir effacer tous les logs ?"):
            self.logs.clear()
            self._line_count = 0
            self._write_count = 0
            self.txt.configure(state=tk.NORMAL)
            self.txt.delete("1.0", tk.END)
            self.txt.configure(state=tk.DISABLED)
            self.status_var.set("Logs effacés")

    def _select_all(self) -> None:
        """Select all text in display area."""
        try:
            self.txt.tag_add(tk.SEL, "1.0", tk.END)
            self.txt.mark_set(tk.INSERT, "1.0")
            self.txt.see(tk.INSERT)
        except tk.TclError:
            pass

    def _toggle_folders_only(self) -> None:
        """Toggle folders-only display."""
        current_state = self.var_only_folders.get()
        self.var_only_folders.set(not current_state)
        self._render_logs()

    def _show_shortcuts_help(self) -> None:
        """Show keyboard shortcuts help."""
        shortcuts_text = """Raccourcis clavier disponibles :

FICHIER :
• Ctrl+N : Nouveau scan initial
• Ctrl+R : Scan de comparaison  
• Ctrl+E : Exporter les résultats
• Ctrl+Q : Quitter l'application

ÉDITION :
• Ctrl+C : Copier la sélection
• Ctrl+A : Sélectionner tout
• Ctrl+L : Effacer les logs

VUE :
• Ctrl+D : Basculer "Dossiers seulement"
• Ctrl+F : Aller au champ de recherche

AUTRES :
• F1 : Cette aide
• Échap : Arrêter le scan en cours"""
        
        messagebox.showinfo("Raccourcis clavier", shortcuts_text)

    def _show_about(self) -> None:
        """Show application information."""
        about_text = """AccessChk GUI v1.10

Interface graphique pour l'outil AccessChk de Microsoft Sysinternals.

Fonctionnalités :
• Scan des permissions de fichiers et dossiers
• Comparaison entre deux scans
• Export des résultats
• Filtrage avancé
• Interface utilisateur intuitive

Développé avec Python et Tkinter
© 2025"""
        
        messagebox.showinfo("À propos", about_text)

    def _show_principal_help(self) -> None:
        """Show detailed help dialog for the 'Principal' field."""

        messagebox.showinfo("Aide — Principal",
            "Le compte utilisé pour le scan correspond automatiquement à l'utilisateur courant non administrateur.\n"
            "Pour exécuter un scan avec un autre compte, relancez l'application en étant connecté avec ce compte standard.")

    def _browse_accesschk(self):
        """Open file selector to choose accesschk.exe."""

        p = filedialog.askopenfilename(title="Sélectionner accesschk.exe", filetypes=[("Executables","*.exe"), ("All files","*.*")])
        if p: self.entry_accesschk.delete(0, tk.END); self.entry_accesschk.insert(0, p)

    def _browse_target_replace(self):
        """Open folder selector that replaces current target list."""

        p = filedialog.askdirectory(title="Choisir un dossier (remplace la liste actuelle)", mustexist=True)
        if p: self.entry_target.delete(0, tk.END); self.entry_target.insert(0, os.path.normpath(p))

    # ---- core ----
        """Open exclusions management window."""
        
        # Create popup window
        exclusion_window = tk.Toplevel(self)
        exclusion_window.title("Gestion des exclusions")
        exclusion_window.geometry("600x400")
        exclusion_window.transient(self)
        exclusion_window.grab_set()
        
        # Center window
        exclusion_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (exclusion_window.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (exclusion_window.winfo_height() // 2)
        exclusion_window.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(exclusion_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title and description
        ttk.Label(main_frame, text="Chemins à exclure des scans", font=("TkDefaultFont", 12, "bold")).pack(pady=(0,5))
        ttk.Label(main_frame, text="Ces chemins ne seront pas analysés lors des scans AccessChk.", 
                 foreground="gray").pack(pady=(0,10))
        
        # Frame for list and scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Fill listbox with current exclusions
        for exclusion in self.exclusions:
            listbox.insert(tk.END, exclusion)
        
        # Frame for buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0,10))
        
        def add_exclusion():
            """Add a new exclusion."""
            path = filedialog.askdirectory(title="Sélectionner un dossier à exclure")
            if path:
                normalized_path = os.path.normpath(path)
                if normalized_path not in self.exclusions:
                    self.exclusions.append(normalized_path)
                    listbox.insert(tk.END, normalized_path)
                else:
                    messagebox.showinfo("Information", "Ce chemin est déjà dans les exclusions.")
        
        def remove_exclusion():
            """Remove selected exclusion."""
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                path = listbox.get(index)
                self.exclusions.remove(path)
                listbox.delete(index)
            else:
                messagebox.showinfo("Information", "Veuillez sélectionner un élément à supprimer.")
        
        def add_manual_exclusion():
            """Manually add a path."""
            dialog = tk.Toplevel(exclusion_window)
            dialog.title("Ajouter un chemin")
            dialog.geometry("400x120")
            dialog.transient(exclusion_window)
            dialog.grab_set()
            
            ttk.Label(dialog, text="Chemin à exclure :").pack(pady=10)
            entry = ttk.Entry(dialog, width=50)
            entry.pack(pady=5)
            entry.focus()
            
            def ok_manual():
                path = entry.get().strip()
                if path:
                    normalized_path = os.path.normpath(path)
                    if normalized_path not in self.exclusions:
                        self.exclusions.append(normalized_path)
                        listbox.insert(tk.END, normalized_path)
                        dialog.destroy()
                    else:
                        messagebox.showinfo("Information", "Ce chemin est déjà dans les exclusions.")
                else:
                    messagebox.showwarning("Attention", "Veuillez saisir un chemin.")
            
            btn_frame_manual = ttk.Frame(dialog)
            btn_frame_manual.pack(pady=10)
            ttk.Button(btn_frame_manual, text="OK", command=ok_manual).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame_manual, text="Annuler", command=dialog.destroy).pack(side=tk.LEFT)
            
            dialog.bind('<Return>', lambda e: ok_manual())
            dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Management buttons
        ttk.Button(btn_frame, text="📁 Parcourir", command=add_exclusion).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(btn_frame, text="✏️ Saisir", command=add_manual_exclusion).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Supprimer", command=remove_exclusion).pack(side=tk.LEFT, padx=5)
        
        # Close buttons
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill=tk.X)
        ttk.Button(close_frame, text="Fermer", command=exclusion_window.destroy).pack(side=tk.RIGHT)
        
        # Focus on window
        exclusion_window.focus_set()

    # ---- core ----
    def _on_scan(self, mode: str = "baseline"):
        """Start an AccessChk scan in a thread based on selected mode."""
        if self.runner.is_running:
            messagebox.showwarning("Scan en cours", "Un scan est déjà en cours.")
            return
        
        # Secure executable validation
        accesschk = self.entry_accesschk.get().strip()
        is_valid, error_msg = validate_executable_path(accesschk)
        if not is_valid:
            messagebox.showerror("Erreur", f"Erreur avec accesschk.exe: {error_msg}")
            return
        
        # Check compare mode
        if mode == "compare" and not os.path.isfile(self.base_scan_path):
            messagebox.showerror("Scan comparaison", "Aucun scan initial trouvé. Lancez d'abord un scan initial.")
            return
        
        # Target validation
        raw_targets = self.entry_target.get().strip() or default_targets_string()
        is_valid, error_msg, targets = validate_target_paths(raw_targets)
        if not is_valid:
            messagebox.showerror("Erreur", f"Erreur avec les cibles: {error_msg}")
            return

        principal = self.default_principal.strip() if self.default_principal else ""

        # Display command that will be launched
        sample_cmd = [accesschk, "-accepteula", "-nobanner"]
        if principal:
            sample_cmd.append(principal)
        sample_cmd.extend(["-w", "-s", targets[0] if targets else "<cible>"])
        cmd_display = " ".join(f'"{arg}"' if " " in arg else arg for arg in sample_cmd)
        if len(targets) > 1:
            cmd_display += f" (et {len(targets) - 1} autres cibles)"
        self.cmd_var.set(cmd_display)

        # Save information for history
        self.current_scan_targets = targets
        self.current_scan_principal = principal

        # Reset state
        self.logs.clear()
        self._line_count = 0
        self._write_count = 0
        self._suppressed_errors = 0
        self._pending_path = None
        self.scan_mode = mode
        # UI update
        self.txt.configure(state=tk.NORMAL)
        self.txt.delete("1.0", tk.END)
        self.txt.configure(state=tk.DISABLED)
        
        principal_label = principal or "(introuvable)"
        self.status_var.set(f"Préparation du scan : {principal_label} sur {len(targets)} cible(s). 0 lignes (0 RW)")
        
        # Scan state
        self.running = True
        self.current_target = None
        self.current_principal = None
        
        # Button state
        self.btn_scan_base.configure(state=tk.DISABLED)
        self.btn_scan_compare.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.NORMAL)
        self.pbar.start(self.app_config.PROGRESS_BAR_SPEED)

        # Launch scan via runner
        try:
            self.runner.start_scan(accesschk, targets, principal)
        except RuntimeError as e:
            messagebox.showerror("Erreur", str(e))
            self._on_stop()

    def _on_stop(self) -> None:
        """Stop the currently running scan (if a process is active)."""
        try:
            self.runner.stop_scan()
            self.status_var.set(f"Arrêt manuel. {self._line_count} lignes ({self._write_count} RW).")
        except Exception as e:
            logger.warning(f"Error during stop: {e}")
        finally:
            self.running = False
            self.pbar.stop()
            self.scan_mode = None
            self._update_compare_state()
            self.btn_stop.configure(state=tk.DISABLED)
            self.current_target = None
            self.current_principal = None

    def _poll_queue(self) -> None:
        """Retrieve items from queue and update display."""
        start_time = time.time()
        processed = 0
        buf_normal, buf_write, buf_err = [], [], []
        
        # Batch processing with time AND line limit to avoid blocking
        max_iterations = self.app_config.BATCH_SIZE * 2  # Absolute iteration limit
        iteration_count = 0
        while (processed < self.app_config.BATCH_SIZE and 
               (time.time() - start_time) < (self.app_config.BATCH_TIMEOUT_MS / 1000) and
               iteration_count < max_iterations):
            try: 
                item = self.q.get_nowait()
            except queue.Empty: 
                break
            
            iteration_count += 1
            
            if "_status" in item:
                self.status_var.set(item["_status"])
                continue
                
            if item.get("_finished"):
                rc = item.get("returncode")
                self._finish_scan(rc)
                continue
            
            text = item["line"]
            if not text.strip():
                self._pending_path = None
                processed += 1
                continue
            
            # Optimized line processing
            if not item["err"]:
                path = extract_first_path(text)
                if not item["write"]:
                    if path and text.strip() == path.strip():
                        self._pending_path = path.strip()
                        processed += 1
                        continue
                    else:
                        self._pending_path = None
                else:
                    if (not path) and self._pending_path:
                        text = f"{text.strip()} — {self._pending_path}"
                        item = dict(item)
                        item["line"] = text
                        path = extract_first_path(text)
                    self._pending_path = None
            else:
                if self._pending_path and not extract_first_path(text):
                    text = f"{self._pending_path} — {text.strip()}"
                    item = dict(item)
                    item["line"] = text
                self._pending_path = None
            
            # Suppressed error handling
            if matches_suppressed_error(text):
                self._suppressed_errors += 1
                self._suppress_error_sequence(buf_normal, buf_write, buf_err)
                processed += 1
                continue
            
            # Add line (deque auto-trims when maxlen reached)
            self.logs.append(item)
            self._line_count += 1
            if item["write"] and not item["err"]:
                self._write_count += 1
            

            
            # Buffering for display
            if item["err"]: 
                buf_err.append(text)
            elif item["write"]: 
                buf_write.append(text)
            else: 
                buf_normal.append(text)
            
            processed += 1

        # Batch display update
        if buf_normal or buf_write or buf_err:
            self._update_display_batch(buf_normal, buf_write, buf_err)

        # Status update
        if self.running:
            target = self.current_target or "(en attente)"
            principal = self.current_principal or "(auto)"
            suppressed = f", {self._suppressed_errors} erreurs ignorées" if self._suppressed_errors else ""
            self.status_var.set(
                f"Scan en cours — {principal} @ {target} : {self._line_count} lignes ({self._write_count} RW{suppressed})"
            )
        
        # Schedule next check
        self.after(self.app_config.UI_UPDATE_INTERVAL_MS, self._poll_queue)
    
    def _update_display_batch(self, buf_normal: List[str], buf_write: List[str], buf_err: List[str]):
        """Update display in batch for better performance."""
        self.txt.configure(state=tk.NORMAL)
        
        if buf_normal: 
            self.txt.insert(tk.END, "\n".join(buf_normal) + "\n", "normal")
        if buf_write:  
            self.txt.insert(tk.END, "\n".join(buf_write) + "\n", "write")
        if buf_err:    
            self.txt.insert(tk.END, "\n".join(buf_err) + "\n", "err")
        
        # Smart scrolling - only if near bottom
        try:
            visible_end = float(self.txt.index("@0,%d" % self.txt.winfo_height()))
            total_lines = float(self.txt.index(tk.END))
            if (total_lines - visible_end) < 5:  # If within last 5 visible lines
                self.txt.see(tk.END)
        except (tk.TclError, ValueError):
            pass  # Ignore scrolling errors
        
        self.txt.configure(state=tk.DISABLED)

    def _finish_scan(self, returncode: int):
        """Finalize scan: status update and potential save."""
        self.running = False
        self.runner.is_running = False
        self.pbar.stop()
        
        # Clean directory cache to prevent memory leak
        self._isdir_cache.clear()
        
        # Save to history
        if hasattr(self, 'current_scan_targets') and hasattr(self, 'current_scan_principal'):
            try:
                self.history_manager.add_scan(
                    self.scan_mode or "baseline",
                    self.current_scan_targets,
                    self.current_scan_principal or "auto",
                    len(self.logs)
                )
            except Exception as e:
                logger.warning(f"Cannot add scan to history: {e}")
        
        self.current_target = None
        self.current_principal = None
        
        suppressed = f", {self._suppressed_errors} erreurs ignorées" if self._suppressed_errors else ""
        self.status_var.set(
            f"Terminé (rc={returncode}). {len(self.logs)} lignes ({self._write_count} RW{suppressed})."
        )
        self.btn_stop.configure(state=tk.DISABLED)
        
        try:
            self._persist_scan_results()
        except Exception as e:
            logger.error(f"Error during save: {e}")
            messagebox.showerror("Erreur", f"Impossible de sauvegarder les résultats: {e}")
        finally:
            self._update_compare_state()

    def _remove_last_log_entry(self, buf_normal, buf_write, buf_err):
        """Remove last stored line to synchronize display buffers."""

        if not self.logs:
            return False
        last = self.logs.pop()
        self._line_count = max(0, self._line_count - 1)
        if last["write"] and not last["err"] and self._write_count:
            self._write_count -= 1
        target_buf = buf_err if last["err"] else (buf_write if last["write"] else buf_normal)
        for idx in range(len(target_buf) - 1, -1, -1):
            if target_buf[idx] == last["line"]:
                target_buf.pop(idx)
                break
        return True

    def _suppress_error_sequence(self, buf_normal, buf_write, buf_err):
        """Clean up noise lines following an AccessChk error message."""

        removed = False

        def remove_last_if(predicate):
            nonlocal removed
            if self.logs and predicate(self.logs[-1]):
                if self._remove_last_log_entry(buf_normal, buf_write, buf_err):
                    removed = True
                return True
            return False

        remove_last_if(
            lambda it: not it["err"]
            and not LINE_RW_PREFIX.search(it["line"])
            and bool(extract_first_path(it["line"]))
        )
        # Remove leftover unreadable noise
        while remove_last_if(
            lambda it: not it["err"]
            and not it["write"]
            and not LINE_RW_PREFIX.search(it["line"])
            and not ASCII_ALNUM.search(it["line"])
        ):
            pass
        return removed

    # ---- filtering / export ----
    def _is_dir_cached(self, path: str) -> bool:
        """Test if path is a directory with result caching."""
        if not path or not isinstance(path, str):
            return False
            
        key = path.lower()
        if key in self._isdir_cache: 
            return self._isdir_cache[key]
        
        try: 
            isd = os.path.isdir(path)
        except (OSError, ValueError, TypeError) as e:
            logger.debug(f"Error checking directory {path}: {e}")
            isd = False
        
        self._isdir_cache[key] = isd
        return isd

    def _render_logs(self) -> None:
        """Re-display filtered log content in text area."""

        self.txt.configure(state=tk.NORMAL); self.txt.delete("1.0", tk.END)
        norm, writ, err = [], [], []
        for it in self._filtered_logs():
            text = it["line"]
            if it["err"]:
                err.append(text)
            elif it["write"]:
                writ.append(text)
            else:
                norm.append(text)
        if norm: self.txt.insert(tk.END, "\n".join(norm) + "\n", "normal")
        if writ: self.txt.insert(tk.END, "\n".join(writ) + "\n", "write")
        if err:  self.txt.insert(tk.END, "\n".join(err) + "\n", "err")
        self.txt.see(tk.END); self.txt.configure(state=tk.DISABLED)

    def _filtered_logs(self, filter_text=None, only_dirs=None):
        """Generate filtered lines according to user input."""

        f = (self.var_filter.get() if filter_text is None else filter_text).strip().lower()
        only_dirs = self.var_only_folders.get() if only_dirs is None else only_dirs
        for it in self.logs:
            text = it["line"]
            if f and f not in text.lower():
                continue
            if only_dirs:
                if it["err"]:
                    continue
                if not LINE_RW_PREFIX.search(text):
                    continue
                p = extract_first_path(text)
                if not p or not self._is_dir_cached(p):
                    continue
            yield it

    def _filter_lines_for_diff(self, lines):
        """Prepare list of comparable lines for diff generation."""

        filtered = []
        for line in lines:
            if not line:
                continue
            lower = line.lower()
            if "[erreur]" in lower or "[info]" in lower or "[exception]" in lower:
                continue
            
            # Two cases to handle:
            # 1. Directory lines (start with a path)
            # 2. RW permission lines (indented, start with RW)
            
            path = extract_first_path(line)
            if path:
                # Directory line - keep if it's actually a directory
                if self._is_dir_cached(path):
                    filtered.append(line)
            elif LINE_RW_PREFIX.search(line):
                # RW permission line without path - keep for comparison
                filtered.append(line)
        return filtered

    def _export_filtered(self) -> None:
        """Export currently visible lines to text file."""
        if not self.logs: messagebox.showinfo("Export", "Aucun log à exporter."); return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt"), ("All files","*.*")], initialfile=AppConfig.EXPORT_DEFAULT)
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                for it in self._filtered_logs():
                    fh.write(it["line"] + "\n")
            messagebox.showinfo("Export", f"Export terminé : {path}")
        except Exception as ex:
            messagebox.showerror("Erreur export", str(ex))

    def _export_csv(self) -> None:
        """Export logs to CSV format."""
        if not self.logs:
            messagebox.showinfo("Export CSV", "Aucun log à exporter.")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="accesschk_export.csv"
        )
        if not path:
            return
        
        try:
            filtered_logs = list(self._filtered_logs())
            self.export_manager.export_to_csv(filtered_logs, path)
            messagebox.showinfo("Export CSV", f"Export CSV terminé : {path}")
        except Exception as ex:
            messagebox.showerror("Erreur export CSV", str(ex))

    def _export_json(self) -> None:
        """Export logs to JSON format."""
        if not self.logs:
            messagebox.showinfo("Export JSON", "Aucun log à exporter.")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="accesschk_export.json"
        )
        if not path:
            return
        
        try:
            filtered_logs = list(self._filtered_logs())
            self.export_manager.export_to_json(filtered_logs, path)
            messagebox.showinfo("Export JSON", f"Export JSON terminé : {path}")
        except Exception as ex:
            messagebox.showerror("Erreur export JSON", str(ex))

    def _export_xml(self) -> None:
        """Export logs to XML format."""
        if not self.logs:
            messagebox.showinfo("Export XML", "Aucun log à exporter.")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
            initialfile="accesschk_export.xml"
        )
        if not path:
            return
        
        try:
            filtered_logs = list(self._filtered_logs())
            self.export_manager.export_to_xml(filtered_logs, path)
            messagebox.showinfo("Export XML", f"Export XML terminé : {path}")
        except Exception as ex:
            messagebox.showerror("Erreur export XML", str(ex))

    def _show_history(self) -> None:
        """Show scan history."""
        history = self.history_manager.get_history()
        
        # Create new window for history
        history_window = tk.Toplevel(self)
        history_window.title("Historique des scans")
        history_window.geometry("800x600")
        
        # Frame for buttons
        btn_frame = ttk.Frame(history_window)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Effacer historique", 
                  command=lambda: self._clear_history(history_window)).pack(side=tk.RIGHT)
        
        # Scan list
        tree_frame = ttk.Frame(history_window)
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("timestamp", "type", "targets", "principal", "results")
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Column configuration
        tree.heading("timestamp", text="Date/Heure")
        tree.heading("type", text="Type")
        tree.heading("targets", text="Cibles")
        tree.heading("principal", text="Principal")
        tree.heading("results", text="Résultats")
        
        tree.column("timestamp", width=150)
        tree.column("type", width=100)
        tree.column("targets", width=300)
        tree.column("principal", width=150)
        tree.column("results", width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Fill with data
        for entry in history:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                targets_str = "; ".join(entry['targets'][:2])  # Display max 2 targets
                if len(entry['targets']) > 2:
                    targets_str += f" (+{len(entry['targets'])-2} autres)"
                
                tree.insert("", tk.END, values=(
                    timestamp,
                    entry['scan_type'],
                    targets_str,
                    entry['principal'],
                    f"{entry['result_count']} lignes"
                ))
            except Exception as e:
                logger.warning(f"Error displaying history entry: {e}")

    def _clear_history(self, window: tk.Toplevel) -> None:
        """Clear scan history."""
        if messagebox.askyesno("Effacer historique", "Êtes-vous sûr de vouloir effacer tout l'historique ?"):
            self.history_manager.clear_history()
            window.destroy()
            messagebox.showinfo("Historique", "Historique effacé avec succès.")

    # ---- misc ----
    def _persist_scan_results(self) -> None:
        """Save scan results to temporary file."""

        mode = self.scan_mode
        self.scan_mode = None
        if not mode:
            return
        lines = [it["line"] for it in self.logs]
        target_path = self.base_scan_path if mode == "baseline" else self.compare_scan_path
        try:
            with open(target_path, "w", encoding="utf-8") as fh:
                if lines:
                    fh.write("\n".join(lines))
                    fh.write("\n")
                else:
                    fh.truncate(0)
        except Exception as ex:
            messagebox.showerror("Enregistrement du scan", f"Impossible d'enregistrer le scan : {ex}")
            return

        if mode == "baseline":
            self._safe_remove(self.compare_scan_path)
            self._safe_remove(self.diff_output_path)
            messagebox.showinfo("Scan initial", f"Scan initial enregistré dans : {target_path}")
        else:
            self._handle_compare_diff(lines)

    def _handle_compare_diff(self, current_lines):
        """Compare current scan to baseline then display/save diff."""

        try:
            with open(self.base_scan_path, "r", encoding="utf-8") as fh:
                base_lines = fh.read().splitlines()
        except FileNotFoundError:
            messagebox.showerror("Scan comparaison", "Le scan initial est introuvable pour générer la comparaison.")
            return
        except Exception as ex:
            messagebox.showerror("Scan comparaison", f"Impossible de lire le scan initial : {ex}")
            return

        new_lines = [ln.rstrip("\n") for ln in current_lines]
        base_filtered = self._filter_lines_for_diff(base_lines)
        new_filtered = self._filter_lines_for_diff(new_lines)
        diff_lines = [
            line for line in difflib.unified_diff(
                base_filtered,
                new_filtered,
                fromfile="",
                tofile="",
                lineterm="",
            )
            if line and not line.startswith("---") and not line.startswith("+++") and not line.startswith("@@")
        ]
        
        # Filter lines to keep only REALLY new RW rights
        filtered_diff_lines = []
        added_rw_lines = []
        removed_rw_lines = []
        
        # First pass: collect RW additions and removals
        for line in diff_lines:
            if "RW" in line:
                clean_line = line[1:].strip()
                if line.startswith("+"):
                    added_rw_lines.append((line, clean_line))
                elif line.startswith("-"):
                    removed_rw_lines.append(clean_line)
        
        # Second pass: keep only truly new rights
        for original_line, clean_added in added_rw_lines:
            if clean_added not in removed_rw_lines:
                filtered_diff_lines.append(original_line)
        
        # Add directory paths for context
        for line in diff_lines:
            if not line.startswith(("+", "-")) and extract_first_path(line) and "RW" not in line:
                filtered_diff_lines.append(line)
        
        diff_lines = filtered_diff_lines
        if diff_lines:
            diff_text = "\n".join(diff_lines)
            try:
                with open(self.diff_output_path, "w", encoding="utf-8") as fh:
                    fh.write(diff_text)
                    if not diff_text.endswith("\n"):
                        fh.write("\n")
            except Exception:
                pass
            self._show_diff_window(diff_lines)
        else:
            self._safe_remove(self.diff_output_path)
            messagebox.showinfo("Scan comparaison", "Aucune différence RW détectée entre les scans.")

    def _show_diff_window(self, diff_lines):
        """Open window containing generated diff between two scans."""

        win = tk.Toplevel(self)
        win.title("Différence entre les scans")
        win.geometry("900x600")
        txt_content = "\n".join(diff_lines)
        if txt_content and not txt_content.endswith("\n"):
            txt_content += "\n"

        frm_actions = ttk.Frame(win)
        frm_actions.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)

        def _export_diff():
            path = filedialog.asksaveasfilename(
                title="Exporter la comparaison",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=AppConfig.DIFF_EXPORT_DEFAULT,
            )
            if not path:
                return
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(txt_content)
                messagebox.showinfo("Export diff", f"Export terminé : {path}")
            except Exception as ex:
                messagebox.showerror("Export diff", str(ex))

        ttk.Button(frm_actions, text="Exporter", command=_export_diff).pack(side=tk.RIGHT)

        txt = tk.Text(win, wrap=tk.NONE)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt.insert("1.0", txt_content)
        txt.configure(state=tk.DISABLED)
        yscroll = ttk.Scrollbar(win, orient=tk.VERTICAL, command=txt.yview)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        txt.configure(yscrollcommand=yscroll.set)
        xscroll = ttk.Scrollbar(win, orient=tk.HORIZONTAL, command=txt.xview)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        txt.configure(xscrollcommand=xscroll.set)

    def _update_compare_state(self) -> None:
        """Enable/disable scan buttons based on current state."""

        if self.running:
            self.btn_scan_base.configure(state=tk.DISABLED)
            self.btn_scan_compare.configure(state=tk.DISABLED)
        else:
            self.btn_scan_base.configure(state=tk.NORMAL)
            state_compare = tk.NORMAL if os.path.isfile(self.base_scan_path) else tk.DISABLED
            self.btn_scan_compare.configure(state=state_compare)

    def _safe_remove(self, path: str):
        """Silently remove a file (used for temporary files)."""

        try:
            if path and os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass

    def _copy_selection(self):
        """Copy current text area selection to clipboard."""

        try: sel = self.txt.selection_get(); self.clipboard_clear(); self.clipboard_append(sel)
        except Exception: pass

    def _show_context_menu(self, event):
        """Show custom context menu for text widget."""

        try: self.menu.tk_popup(event.x_root, event.y_root)
        finally: self.menu.grab_release()

    def on_close(self) -> None:
        """Cleanly close main window by stopping any running processes."""
        try:
            self.runner.stop_scan()
        except Exception as e:
            logger.warning(f"Error stopping runner: {e}")
        
        self._cleanup_scan_files()
        self.destroy()

    def _cleanup_scan_files(self):
        """Remove temporary scan files generated by application."""

        for path in (self.base_scan_path, self.compare_scan_path, self.diff_output_path):
            self._safe_remove(path)
