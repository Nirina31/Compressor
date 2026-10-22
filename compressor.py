""" Clone fonctionnel des utilitaires de compression bzip2, lzma et 7-zip """

import os
import sys
import time
import argparse
import hashlib

# Algorithmes du cours
from core.rle import rle_encode_text, rle_decode_text
from core.huffman import huffman_encode_text, huffman_decode_text
from core.bwt import bwt_encode_text, bwt_decode_text_steps
from core.lz77 import lz77_encode_text, lz77_decode_text

# Moteurs bzip2, lzma et 7z
from engines import (
    compress_bzip2, decompress_bzip2,
    compress_lzma, decompress_lzma,
    compress_7z, extract_7z
)


def get_file_hash(filepath: str) -> str:
    """Calcule le hash SHA-256 pour vérifier que la décompression est sans perte."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def print_compression_stats(tool_name: str, src: str, dst: str, elapsed_ms: float):
    """Affiche les statistiques de compression de manière lisible."""
    orig_size = os.path.getsize(src) if os.path.isfile(src) else 0
    comp_size = os.path.getsize(dst)
    gain = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0
    print(f"[{tool_name}] Fichier créé : {dst}")
    print(f"  Taille originale : {orig_size:,} octets")
    print(f"  Taille compressée: {comp_size:,} octets (gain de {gain:.1f}%)")
    print(f"  Temps d'exécution: {elapsed_ms:.1f} ms")


def run_course_demo():
    """Valide les algorithmes théoriques avec les exemples exacts du cours."""
    print("--- Démonstration des algorithmes du cours ---\n")

    # Huffman
    texte = "ABRACADABRA"
    bits, codes, root, _ = huffman_encode_text(texte)
    decoded = huffman_decode_text(bits, root)
    print(f"1. Huffman (texte: '{texte}')")
    print(f"   Codes binaires : {codes}")
    print(f"   Flux encodé    : {bits} ({len(bits)} bits)")
    print(f"   Décodage       : '{decoded}' -> {'OK' if decoded == texte else 'ERREUR'}\n")

    # RLE
    texte_rle = "AAAABBBCCDAA"
    enc_rle = rle_encode_text(texte_rle)
    dec_rle = rle_decode_text(enc_rle)
    print(f"2. RLE (texte: '{texte_rle}')")
    print(f"   Encodage : {enc_rle}")
    print(f"   Décodage : '{dec_rle}' -> {'OK' if dec_rle == texte_rle else 'ERREUR'}\n")

    # BWT
    texte_bwt = "BANANA"
    bwt_res, idx = bwt_encode_text(texte_bwt)
    dec_bwt, _ = bwt_decode_text_steps(bwt_res, idx)
    print(f"3. BWT (texte: '{texte_bwt}')")
    print(f"   Transformée : ({bwt_res}, {idx})")
    print(f"   Inversion   : '{dec_bwt}' -> {'OK' if dec_bwt == texte_bwt else 'ERREUR'}\n")

    # LZ77
    texte_lz = "CABRACADABRARRARRAD"
    triplets = lz77_encode_text(texte_lz, search_buffer_size=7, lookahead_size=6)
    dec_lz = lz77_decode_text(triplets)
    print(f"4. LZ77 (texte: '{texte_lz}')")
    print(f"   Triplets : {triplets}")
    print(f"   Décodage : '{dec_lz}' -> {'OK' if dec_lz == texte_lz else 'ERREUR'}\n")


def main():
    parser = argparse.ArgumentParser(description="Clone fonctionnel de bzip2, lzma et 7-zip")
    parser.add_argument("--demo-cours", action="store_true", help="Afficher les exemples du cours")
    subparsers = parser.add_subparsers(dest="tool")

    # bzip2
    p_bzip2 = subparsers.add_parser("bzip2", help="Utilitaire bzip2")
    p_bzip2.add_argument("-c", "--compress", metavar="FICHIER", help="Compresser un fichier")
    p_bzip2.add_argument("-d", "--decompress", metavar="FICHIER", help="Décompresser un fichier")
    p_bzip2.add_argument("-o", "--output", metavar="DEST", help="Fichier de sortie")
    p_bzip2.add_argument("--custom", action="store_true", help="Utiliser la chaîne BWT+RLE+Huffman codée à la main")

    # lzma
    p_lzma = subparsers.add_parser("lzma", help="Utilitaire lzma")
    p_lzma.add_argument("-c", "--compress", metavar="FICHIER", help="Compresser un fichier")
    p_lzma.add_argument("-d", "--decompress", metavar="FICHIER", help="Décompresser un fichier")
    p_lzma.add_argument("-o", "--output", metavar="DEST", help="Fichier de sortie")

    # 7-zip
    p_7z = subparsers.add_parser("7z", help="Utilitaire 7-zip")
    p_7z.add_argument("-c", "--compress", metavar="SOURCE", help="Créer une archive .7z")
    p_7z.add_argument("-d", "--decompress", metavar="ARCHIVE", help="Extraire une archive .7z")
    p_7z.add_argument("-o", "--output", metavar="DEST", help="Dossier ou fichier de sortie")

    # Benchmark
    subparsers.add_parser("benchmark", help="Comparer les formats sur texte, audio, image et vidéo")
    args = parser.parse_args()
    if args.demo_cours or len(sys.argv) == 1:
        run_course_demo()
        if len(sys.argv) == 1:
            print("Utilisez --help pour voir les options : python compressor.py -h")
        return

    # Exécution selon l'outil demandé
    if args.tool == "bzip2":
        if args.compress:
            t0 = time.time()
            out = compress_bzip2(args.compress, args.output, use_custom=args.custom)
            print_compression_stats("bzip2", args.compress, out, (time.time() - t0) * 1000)
        elif args.decompress:
            t0 = time.time()
            out = decompress_bzip2(args.decompress, args.output, use_custom=args.custom)
            print(f"[bzip2] Fichier restauré : {out} ({(time.time() - t0) * 1000:.1f} ms)")
        else:
            p_bzip2.print_help()
    elif args.tool == "lzma":
        if args.compress:
            t0 = time.time()
            out = compress_lzma(args.compress, args.output)
            print_compression_stats("lzma", args.compress, out, (time.time() - t0) * 1000)
        elif args.decompress:
            t0 = time.time()
            out = decompress_lzma(args.decompress, args.output)
            print(f"[lzma] Fichier restauré : {out} ({(time.time() - t0) * 1000:.1f} ms)")
        else:
            p_lzma.print_help()
    elif args.tool == "7z":
        if args.compress:
            t0 = time.time()
            out = compress_7z(args.compress, args.output)
            print_compression_stats("7-zip", args.compress, out, (time.time() - t0) * 1000)
        elif args.decompress:
            t0 = time.time()
            out = extract_7z(args.decompress, args.output)
            print(f"[7-zip] Archive extraite dans : {out} ({(time.time() - t0) * 1000:.1f} ms)")
        else:
            p_7z.print_help()
    elif args.tool == "benchmark":
        import benchmark
        benchmark.run_benchmark()

if __name__ == "__main__":
    main()
