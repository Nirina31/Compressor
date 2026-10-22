# Projet Compressor : Clones bzip2, lzma et 7-zip

## Fonctionnalités
1. **Algorithmes théoriques du cours (`core/`) :**
   - **Huffman** (`core/huffman.py`) : Construction de l'arbre binaire pondéré, attribution des codes préfixes et décodage bit-à-bit (validé sur `"ABRACADABRA"`).
   - **RLE (Run-Length Encoding)** (`core/rle.py`) : Compression par plages répétées (validé sur `"AAAABBBCCDAA"` $\to$ `"4A3B2C1D2A"`).
   - **BWT (Burrows-Wheeler Transform)** (`core/bwt.py`) : Rotations cycliques, tri lexicographique et inversion matricielle (validé sur `"BANANA"` $\to$ `("NNBAAA", 4)`).
   - **LZ77** (`core/lz77.py`) : Fenêtre glissante (tampon de recherche + tampon d'entrée) et encodage par triplets $(D, L, C)$ (validé sur `"CABRACADABRARRARRAD"`).
   - **bzip2 Custom** (`core/bzip2_custom.py`) : Chaîne complète "from scratch" combinant **BWT $\to$ RLE $\to$ Huffman**.

2. **Moteurs de compression (`engines.py`) :**
   - **`bzip2`** : Format standard `.bz2` (niveau 9) et mode `--custom` algorithmique.
   - **`lzma`** : Format standard `.xz`.
   - **`7-zip`** : Format d'archive standard `.7z`.

3. **Vérification d'intégrité (100% sans perte) :**
   - Calcul de hachage cryptographique **SHA-256** avant et après décompression garantissant une restauration exacte de chaque fichier.

4. **Banc d'essai comparatif (`benchmark.py`) :**
   - Évaluation automatisée sur 4 types de médias : **texte**, **audio**, **image** et **vidéo**.

## Installation
Cloner le dépôt et installer la dépendance requise (`py7zr` pour le format 7-zip) :
```bash
pip install -r requirements.txt
```

## Guide d'utilisation
Le point d'entrée principal est l'utilitaire en ligne de commande `compressor.py` :

### 1. Test des exemples du cours
Valide et affiche les étapes de calcul pour les algorithmes Huffman, RLE, BWT et LZ77 :
```bash
python compressor.py --demo-cours
```

### 2. Compression et décompression avec `bzip2`
```bash
# Compresser un fichier en .bz2
python compressor.py bzip2 -c tests/texte.txt
# Décompresser une archive .bz2
python compressor.py bzip2 -d tests/texte.txt.bz2
# Utiliser le pipeline BWT -> RLE -> Huffman développé à la main
python compressor.py bzip2 -c tests/texte.txt --custom
```

### 3. Compression et décompression avec `lzma`
```bash
# Compresser un fichier en .xz
python compressor.py lzma -c tests/audio.wav
# Décompresser un fichier .xz
python compressor.py lzma -d tests/audio.wav.xz
```

### 4. Création et extraction d'archives `7-zip`
```bash
# Créer une archive .7z
python compressor.py 7z -c tests/image.bmp
# Extraire une archive .7z
python compressor.py 7z -d tests/image.bmp.7z -o dossier_destination/
```

### 5. Exécution du benchmark complet
Lance les tests comparatifs sur les 4 catégories de fichiers et vérifie l'intégrité SHA-256 :
```bash
python compressor.py benchmark
```

## Structure du projet
Compressor/
├── core/                   # Algorithmes du cours (from scratch)
│   ├── rle.py              # Run-Length Encoding
│   ├── huffman.py          # Arbre et codage de Huffman
│   ├── bwt.py              # Burrows-Wheeler Transform
│   ├── lz77.py             # Lempel-Ziv 77
│   └── bzip2_custom.py     # Pipeline pédagogique BWT+RLE+Huffman
├── tests/                  # Fichiers de test (texte, audio, image, vidéo)
├── utiles/                 # Documentation, configurations et aide-mémoire
├── engines.py              # Moteurs bzip2, lzma, 7-zip
├── compressor.py           # Interface en ligne de commande (CLI)
└── benchmark.py            # Script d'évaluation comparative
