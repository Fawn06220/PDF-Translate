# PDF & DOCX OCR Translate Tool 🇫🇷 ➡ 🌍

Un outil complet de traduction automatique de fichiers PDF et DOCX (texte ou images), avec détection OCR, traduction multi-langues, interface graphique élégante et animation de don personnalisée (C-18 ❤️).

---

## ✨ Fonctionnalités

- 🔤 **OCR automatique** sur fichiers PDF image-only
- 📝 **Traduction de fichiers texte et image** (PDF/DOCX)
- 🌐 **Traduction multilingue** via Google Translate API
- 🧠 **Détection de langue OCR intelligente**
- 🧽 **Nettoyage automatique** (deskew, rotate, optimise)
- 🎁 **Bouton de don animé (C-18)** intégré à l’interface
- 📁 **Export PDF** du résultat traduit
- 🎛 Interface `CustomTkinter` responsive & moderne

---

## 📦 Prérequis

### 🐍 Python

- Python 3.10+ recommandé
- Environnement virtuel (optionnel mais conseillé)

### 📚 Bibliothèques Python

```bash
pip install -r requirements.txt
```

Fichier `requirements.txt` :

```
customtkinter
pytesseract
pdf2image
pillow
ocrmypdf
pymupdf
deep-translator
```

### 🛠 Outils externes nécessaires

| Outil | Rôle | Lien / Emplacement |
|-------|------|--------------------|
| **Tesseract** | OCR principal | https://github.com/tesseract-ocr/tesseract |
| **Poppler**   | Convertir PDF en images | https://github.com/oschwartz10612/poppler-windows |
| **Ghostscript** | Traitement PDF | https://www.ghostscript.com/ |
| **pngquant** *(optionnel)* | Optimisation image | https://pngquant.org/ |

⚠ Assurez-vous que les exécutables sont dans le `PATH` ou définis manuellement dans le script via :

```python
os.environ["PATH"] += os.pathsep + r"C:\chemin\vers\outils"
```

---

## 🚀 Lancer l'application

```bash
python pdf_translate.py
```

L’application s’ouvre avec une interface graphique complète. Vous pouvez :

1. Sélectionner une langue cible
2. Charger un fichier PDF ou DOCX
3. Lancer la traduction avec **Go!**
4. Voir la progression de l’analyse et de la traduction
5. Récupérer le fichier traduit dans le dossier `trads/`

---

## 🎥 Démonstrations

👉 [Voir les vidéos de démonstration ici](http://ninjaaior.free.fr/devdemos/index.html)

---

## 💸 Soutenir le projet

Un bouton de donation animé avec **Android 18 (C-18)** est disponible dans l’interface.

Merci pour votre soutien 🙏  
**https://www.paypal.com/paypalme/noobpythondev**

---

## 📂 Arborescence du projet

```
pdf_translate/
├── flags/                # Drapeaux pour les langues
├── icon/                 # Logo et image de donation
├── tmp/                  # Fichiers temporaires OCR
├── trads/                # Fichiers PDF traduits exportés
├── pdf_translate.py      # Script principal
├── README.md             # Ce fichier
```

---

## 🧠 Auteur

**Créé par Fawn**  
Date de release : 27/05/2025

---

## 📃 Licence

Ce projet est open-source. Utilisation personnelle ou pédagogique uniquement.
