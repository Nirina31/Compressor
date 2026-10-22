""" Moteurs de compression pour bzip2, lzma et 7-zip """

import os
import bz2
import lzma
import py7zr
from core.bzip2_custom import bzip2_custom_compress, bzip2_custom_decompress

# Clone bzip2
def compress_bzip2(src_path: str, dst_path: str = None, use_custom: bool = False) -> str:
    if not dst_path:
        dst_path = src_path + (".mybz2" if use_custom else ".bz2")
    with open(src_path, "rb") as f:
        data = f.read()
    compressed = bzip2_custom_compress(data) if use_custom else bz2.compress(data, compresslevel=9)
    with open(dst_path, "wb") as f:
        f.write(compressed)
    return dst_path


def decompress_bzip2(src_path: str, dst_path: str = None, use_custom: bool = False) -> str:
    if not dst_path:
        if src_path.endswith(".mybz2"):
            dst_path = src_path[:-6]
        elif src_path.endswith(".bz2"):
            dst_path = src_path[:-4]
        else:
            dst_path = src_path + ".decompressed"
    with open(src_path, "rb") as f:
        data = f.read()
    if use_custom or data.startswith(b"BZC1"):
        decompressed = bzip2_custom_decompress(data)
    else:
        decompressed = bz2.decompress(data)
    with open(dst_path, "wb") as f:
        f.write(decompressed)
    return dst_path

# Clone lzma
def compress_lzma(src_path: str, dst_path: str = None) -> str:
    if not dst_path:
        dst_path = src_path + ".xz"
    with open(src_path, "rb") as f:
        data = f.read()
    compressed = lzma.compress(data, preset=9)
    with open(dst_path, "wb") as f:
        f.write(compressed)
    return dst_path

def decompress_lzma(src_path: str, dst_path: str = None) -> str:
    if not dst_path:
        if src_path.endswith(".xz"):
            dst_path = src_path[:-3]
        elif src_path.endswith(".lzma"):
            dst_path = src_path[:-5]
        else:
            dst_path = src_path + ".decompressed"
    with open(src_path, "rb") as f:
        data = f.read()
    decompressed = lzma.decompress(data)
    with open(dst_path, "wb") as f:
        f.write(decompressed)
    return dst_path

# Clone 7-zip
def compress_7z(src_path: str, dst_path: str = None) -> str:
    if not dst_path:
        dst_path = src_path + ".7z"
    with py7zr.SevenZipFile(dst_path, "w") as archive:
        if os.path.isdir(src_path):
            archive.writeall(src_path, arcname=os.path.basename(src_path))
        else:
            archive.write(src_path, arcname=os.path.basename(src_path))
    return dst_path

def extract_7z(archive_path: str, dst_dir: str = None) -> str:
    if not dst_dir:
        dst_dir = os.path.dirname(os.path.abspath(archive_path))
    with py7zr.SevenZipFile(archive_path, "r") as archive:
        archive.extractall(path=dst_dir)
    return dst_dir
