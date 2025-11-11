# AccessChk GUI

Version 1.10 - Interface graphique moderne pour Microsoft AccessChk

## 📋 Description

AccessChk GUI est une interface graphique Python/Tkinter pour l'outil **AccessChk** de Microsoft Sysinternals. Elle permet d'analyser facilement les permissions de fichiers et dossiers Windows, avec des fonctionnalités avancées de filtrage, comparaison et export.

## ✨ Fonctionnalités

- 🔍 **Scan des permissions** : Analyse complète des droits d'accès (lecture, écriture, exécution)
- 🔄 **Comparaison de scans** : Détecte les changements de permissions entre deux scans
- 🎯 **Filtrage avancé** : Recherche textuelle et affichage des dossiers uniquement
- 📤 **Multi-format export** : TXT, CSV, JSON, XML
- 🚫 **Exclusions** : Ignore les chemins non pertinents (ex: AppData)
- 📊 **Historique** : Conservation des scans précédents
- ⌨️ **Raccourcis clavier** : Navigation rapide et efficace
- 🎨 **Interface moderne** : Groupes organisés, barre de progression, statut en temps réel

## 🏗️ Architecture

Le projet suit une architecture modulaire :

```
accesschk_GUI/
├── AccessChkGUI.py          # Point d'entrée principal
├── accesschk_gui_tk.py      # [LEGACY] Fichier monolithique original
├── src/                     # Code source modulaire
│   ├── __init__.py
│   ├── config.py           # Configuration centralisée
│   ├── validation.py       # Validation et sécurité
│   ├── utils.py            # Fonctions utilitaires
│   ├── scanner.py          # Exécution des scans AccessChk
│   ├── export.py           # Gestionnaire d'exports multi-formats
│   ├── history.py          # Historique des scans
│   └── gui.py              # Interface Tkinter principale
├── tests/                   # Tests unitaires
│   └── test_*.py
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md
│   ├── AMELIORATIONS.md
│   └── NOUVELLES_FONCTIONNALITES.md
├── scripts/                 # Scripts utilitaires
│   ├── build_gui.ps1
│   └── diagnostic_scan.py
└── tools/                   # Outils externes
    └── accesschk.exe       # Microsoft Sysinternals AccessChk
```

Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) pour plus de détails.

## 📦 Installation

### Prérequis

- **Python 3.10+**
- **Tkinter** (inclus avec Python sur Windows)
- **accesschk.exe** de Microsoft Sysinternals

### Étapes

1. **Cloner ou télécharger le projet** :
   ```bash
   git clone https://github.com/votre-repo/accesschk_GUI.git
   cd accesschk_GUI
   ```

2. **Télécharger AccessChk.exe** :
   - Rendez-vous sur [Microsoft Sysinternals](https://docs.microsoft.com/en-us/sysinternals/downloads/accesschk)
   - Téléchargez `accesschk.exe`
   - Placez-le dans le dossier `tools/`

3. **Lancer l'application** :
   ```bash
   python AccessChkGUI.py
   ```

## 🚀 Utilisation

### Démarrage rapide

1. **Lancer l'application** : `python AccessChkGUI.py`
2. **Vérifier accesschk.exe** : Le chemin devrait être auto-détecté dans `tools/`
3. **Choisir une cible** : Par défaut `C:\` (modifier si nécessaire)
4. **Lancer un scan** : Cliquer sur "🔍 Scan initial"

### Configuration du Principal (utilisateur)

L'application utilise automatiquement l'utilisateur courant **non-administrateur**. Pour analyser avec un autre compte :

1. Fermer l'application
2. Se connecter avec le compte standard souhaité
3. Relancer l'application

💡 **Astuce** : Utilisez `whoami /groups` pour lister vos groupes disponibles.

### Gestion des exclusions

1. **Fichier** → **Exclusions** (ou `Ctrl+X`)
2. Ajouter des chemins à ignorer (ex: `C:\Users\YourName\AppData`)
3. Les exclusions sont appliquées automatiquement lors des scans

### Comparaison de scans

1. Effectuer un **Scan initial** (baseline)
2. Modifier des permissions Windows
3. Lancer un **Scan de comparaison**
4. L'application affiche uniquement les **nouveaux droits RW**

### Export des résultats

- **TXT** : Export simple filtré (`Ctrl+E`)
- **CSV** : Tableau avec timestamp, type, permissions, chemin
- **JSON** : Format structuré avec métadonnées
- **XML** : Arbre XML complet

## ⌨️ Raccourcis clavier

### Fichier
- `Ctrl+N` : Nouveau scan initial
- `Ctrl+R` : Scan de comparaison
- `Ctrl+X` : Gestion des exclusions
- `Ctrl+E` : Export TXT
- `Ctrl+Q` : Quitter

### Édition
- `Ctrl+C` : Copier la sélection
- `Ctrl+A` : Sélectionner tout
- `Ctrl+L` : Effacer les logs

### Vue
- `Ctrl+D` : Basculer "Dossiers seulement"
- `Ctrl+F` : Focus sur le champ de recherche

### Autres
- `F1` : Aide raccourcis clavier
- `Échap` : Arrêter le scan en cours

## 🔧 Build exécutable (optionnel)

Pour créer un fichier `.exe` autonome :

```powershell
# Installer PyInstaller
pip install pyinstaller

# Build avec le script PowerShell
.\scripts\build_gui.ps1

# Ou manuellement
pyinstaller --onefile --noconsole --name AccessChkGUI AccessChkGUI.py
```

**Important** : Placez manuellement `accesschk.exe` à côté du fichier `.exe` généré.

## 🧪 Tests

Exécuter les tests unitaires :

```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/test_validation.py
pytest tests/test_filtering.py

# Avec couverture
pytest --cov=src tests/
```

## 📝 Développement

### Structure des modules

- **config.py** : Configuration centralisée (chemins, constantes, UI)
- **validation.py** : Validation des entrées, détection d'élévation, sanitization
- **utils.py** : Utilitaires (décodage, extraction de chemins, détection CJK)
- **scanner.py** : `AccessChkRunner` - Exécution des scans en thread
- **export.py** : `ExportManager` - Exports multi-formats
- **history.py** : `ScanHistoryManager` - Persistance de l'historique
- **gui.py** : `AccessChkGUI` - Interface Tkinter complète

### Conventions

- **Encodage** : UTF-8 avec BOM pour compatibilité Windows
- **Style** : PEP 8 avec docstrings Google-style
- **Logging** : Module `logging` avec niveaux INFO/DEBUG/WARNING/ERROR
- **Sécurité** : Validation stricte des entrées, sanitization des arguments

## 🛡️ Sécurité

- ✅ **Validation stricte** des chemins exécutables et cibles
- ✅ **Sanitization** des arguments de ligne de commande
- ✅ **Détection d'élévation** : Empêche l'exécution avec droits admin
- ✅ **Filtrage d'erreurs** : Suppression des messages sensibles
- ⚠️ **Utilisation requise** : Compte utilisateur standard (non-admin)

## 📚 Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) : Architecture détaillée du projet
- [AMELIORATIONS.md](docs/AMELIORATIONS.md) : Améliorations et optimisations
- [NOUVELLES_FONCTIONNALITES.md](docs/NOUVELLES_FONCTIONNALITES.md) : Nouvelles fonctionnalités

## 🐛 Dépannage

### accesschk.exe introuvable
- Vérifier que `accesschk.exe` est dans `tools/`
- Utiliser le bouton "Parcourir" pour spécifier un chemin personnalisé

### "Droits élevés détectés"
- L'application doit être lancée avec un compte standard (non-admin)
- Fermer et relancer sans "Exécuter en tant qu'administrateur"

### Scan très lent
- Utiliser les exclusions pour ignorer les dossiers volumineux (AppData, Windows, etc.)
- Limiter les cibles de scan

### Erreurs de décodage
- Normal pour certains fichiers système
- Les erreurs sont automatiquement filtrées et comptabilisées

## 📄 Licence

Ce projet est un outil interne. AccessChk.exe est propriété de Microsoft Corporation (Sysinternals).

## 🤝 Contribution

Les contributions sont bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committer les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📞 Support

Pour toute question ou problème :

- 📝 Ouvrir une issue sur GitHub
- 📧 Contacter l'équipe de développement
- 📚 Consulter la documentation dans `docs/`

## 🎯 Roadmap

- [ ] Support multi-plateforme (Linux/macOS avec permissions natives)
- [ ] Interface web avec Flask/FastAPI
- [ ] Export Excel avec formatage
- [ ] Graphiques de visualisation des permissions
- [ ] Intégration CI/CD avec tests automatisés
- [ ] Packaging avec Poetry/setuptools

## 📜 Changelog

### v1.10 (2025-01-XX) - Architecture modulaire
- ✨ Refactorisation complète en modules séparés
- 📁 Nouvelle structure src/, tests/, docs/, scripts/, tools/
- 📝 Documentation étendue (ARCHITECTURE.md)
- 🧪 Suite de tests unitaires complète
- 🚀 Launcher dédié (AccessChkGUI.py)

### v1.4 (Previous)
- 'Aide' avec explications et exemples
- Détection auto de accesschk.exe
- 'Only folders' fiabilisé
- Barre de progression + compteur

---

**© 2025 AccessChk GUI Development Team**
