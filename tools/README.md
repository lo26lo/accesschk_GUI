# Tools Directory

Ce dossier contient les outils externes nécessaires au fonctionnement d'AccessChk GUI.

## Contenu

### accesschk.exe
**Source** : Microsoft Sysinternals  
**Téléchargement** : https://learn.microsoft.com/sysinternals/downloads/accesschk

AccessChk est un outil en ligne de commande de Microsoft permettant de vérifier les autorisations d'accès
aux fichiers, clés de registre, services Windows, et autres objets sécurisables.

### Installation

1. Téléchargez accesschk.exe depuis le site officiel Sysinternals
2. Placez le fichier dans ce dossier (`tools/`)
3. L'application AccessChk GUI le détectera automatiquement

### ⚠️ Important

Ce fichier est **gitignored** et ne doit pas être commité dans le dépôt Git.  
Chaque utilisateur doit télécharger sa propre copie depuis Microsoft Sysinternals.

### Vérification

Pour vérifier que accesschk.exe fonctionne correctement :

```powershell
.\accesschk.exe -accepteula -nobanner
```

Vous devriez voir la bannière d'aide d'accesschk.
