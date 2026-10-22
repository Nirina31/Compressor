""" Benchmark comparatif pour tester bzip2, lzma et 7-zip """

import os
import math
import struct
import time
from compressor import get_file_hash
from engines import (
    compress_bzip2, decompress_bzip2,
    compress_lzma, decompress_lzma,
    compress_7z, extract_7z
)

SAMPLES_DIR = "tests"
RESULTS_DIR = "benchmark_output"


def create_sample_files():
    """Genere les 4 fichiers de test UNIQUEMENT si ils n'existent pas deja."""
    os.makedirs(SAMPLES_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    txt_path = os.path.join(SAMPLES_DIR, "texte.txt")
    if not os.path.isfile(txt_path):
        with open(txt_path, "w", encoding="utf-8") as f:
            corpus = (
                "La compression sans perte preserve l'integrite exacte des donnees. "
                "Les algorithmes fondamentaux comme Huffman, RLE, BWT et LZ77/LZMA "
                "permettent de reduire significativement la taille des fichiers.\n"
            )
            f.write(corpus * 350)
        print("[Genere]   " + txt_path)
    else:
        print("[Conserve] " + txt_path + " (" + str(os.path.getsize(txt_path)) + " octets)")

    wav_path = os.path.join(SAMPLES_DIR, "audio.wav")
    if not os.path.isfile(wav_path):
        rate = 44100
        duration = 2
        raw_audio = bytearray()
        for i in range(rate * duration):
            val = int(16000 * math.sin(2.0 * math.pi * 440.0 * (i / rate)))
            raw_audio.extend(struct.pack("<h", val))
        with open(wav_path, "wb") as f:
            f.write(b"RIFF")
            f.write(struct.pack("<I", 36 + len(raw_audio)))
            f.write(b"WAVEfmt ")
            f.write(struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16))
            f.write(b"data")
            f.write(struct.pack("<I", len(raw_audio)))
            f.write(raw_audio)
        print("[Genere]   " + wav_path)
    else:
        print("[Conserve] " + wav_path + " (" + str(os.path.getsize(wav_path)) + " octets)")

    bmp_path = os.path.join(SAMPLES_DIR, "image.bmp")
    if not os.path.isfile(bmp_path):
        w, h = 256, 256
        row_bytes = (w * 3 + 3) & ~3
        pixel_data = bytearray(row_bytes * h)
        for y in range(h):
            for x in range(w):
                idx = y * row_bytes + x * 3
                pixel_data[idx] = (x + y) % 256
                pixel_data[idx + 1] = (x * 2) % 256
                pixel_data[idx + 2] = (y * 2) % 256
        with open(bmp_path, "wb") as f:
            f.write(b"BM")
            f.write(struct.pack("<IHHI", 54 + len(pixel_data), 0, 0, 54))
            f.write(struct.pack("<IIIHHIIIIII", 40, w, h, 1, 24, 0, len(pixel_data), 2835, 2835, 0, 0))
            f.write(pixel_data)
        print("[Genere]   " + bmp_path)
    else:
        print("[Conserve] " + bmp_path + " (" + str(os.path.getsize(bmp_path)) + " octets)")

    vid_path = os.path.join(SAMPLES_DIR, "video.mp4")
    if not os.path.isfile(vid_path):
        with open(vid_path, "wb") as f:
            frame = bytes([i % 256 for i in range(4096)])
            for t in range(60):
                f.write(frame)
                f.write(bytes([t % 256] * 256))
        print("[Genere]   " + vid_path)
    else:
        print("[Conserve] " + vid_path + " (" + str(os.path.getsize(vid_path)) + " octets)")

    return {
        "Texte (.txt)": txt_path,
        "Audio (.wav)": wav_path,
        "Image (.bmp)": bmp_path,
        "Video (.mp4)": vid_path
    }


def run_benchmark():
    files = create_sample_files()

    print("\n--- Benchmark d'efficacité comparative ---\n")
    print(f"{'Type':<15} | {'Original':<12} | {'bzip2':<18} | {'lzma':<18} | {'7-zip':<18}")
    print("-" * 88)

    results = []

    for label, path in files.items():
        orig_sz = os.path.getsize(path)
        h_orig = get_file_hash(path)

        # bzip2
        bz_out = os.path.join(RESULTS_DIR, os.path.basename(path) + ".bz2")
        t0 = time.time()
        compress_bzip2(path, bz_out)
        t_bz = (time.time() - t0) * 1000
        sz_bz = os.path.getsize(bz_out)
        ratio_bz = (1 - sz_bz / orig_sz) * 100

        # Vérification intégrité
        bz_dec = os.path.join(RESULTS_DIR, "dec_bz_" + os.path.basename(path))
        decompress_bzip2(bz_out, bz_dec)
        assert get_file_hash(bz_dec) == h_orig, f"Erreur de décompression bzip2 sur {label}"

        # lzma
        lz_out = os.path.join(RESULTS_DIR, os.path.basename(path) + ".xz")
        t0 = time.time()
        compress_lzma(path, lz_out)
        t_lz = (time.time() - t0) * 1000
        sz_lz = os.path.getsize(lz_out)
        ratio_lz = (1 - sz_lz / orig_sz) * 100

        lz_dec = os.path.join(RESULTS_DIR, "dec_lz_" + os.path.basename(path))
        decompress_lzma(lz_out, lz_dec)
        assert get_file_hash(lz_dec) == h_orig, f"Erreur de décompression lzma sur {label}"

        # 7-zip
        sz_out = os.path.join(RESULTS_DIR, os.path.basename(path) + ".7z")
        t0 = time.time()
        compress_7z(path, sz_out)
        t_sz = (time.time() - t0) * 1000
        sz_7z = os.path.getsize(sz_out)
        ratio_sz = (1 - sz_7z / orig_sz) * 100

        sz_dec_dir = os.path.join(RESULTS_DIR, "dec_7z_" + os.path.splitext(os.path.basename(path))[0])
        extract_7z(sz_out, sz_dec_dir)
        restored_file = os.path.join(sz_dec_dir, os.path.basename(path))
        assert get_file_hash(restored_file) == h_orig, f"Erreur de décompression 7-zip sur {label}"

        row_bz = f"{sz_bz:,} o (-{ratio_bz:.1f}%)"
        row_lz = f"{sz_lz:,} o (-{ratio_lz:.1f}%)"
        row_sz = f"{sz_7z:,} o (-{ratio_sz:.1f}%)"
        print(f"{label:<15} | {orig_sz:>8,} o  | {row_bz:<18} | {row_lz:<18} | {row_sz:<18}")

        results.append({
            "type": label,
            "orig_sz": orig_sz,
            "bzip2_sz": sz_bz, "bzip2_gain": ratio_bz, "bzip2_time": t_bz,
            "lzma_sz": sz_lz, "lzma_gain": ratio_lz, "lzma_time": t_lz,
            "7z_sz": sz_7z, "7z_gain": ratio_sz, "7z_time": t_sz,
        })

    print("-" * 88)
    print("Vérification SHA-256 : Intégrité 100% sans perte validée sur tous les formats.\n")
    return results


if __name__ == "__main__":
    run_benchmark()
