"""
Pipeline bzip2 pédagogique (From Scratch)
Enchaîne BWT -> RLE -> Huffman pour la compression,
et Huffman -> RLE -> BWT pour la décompression.
"""

import struct
from core.bwt import bwt_encode_bytes, bwt_decode_bytes
from core.rle import rle_encode_bytes, rle_decode_bytes
from core.huffman import huffman_compress_bytes, huffman_decompress_bytes

MAGIC = b"BZC1"


def bzip2_custom_compress(data: bytes, block_size: int = 32768) -> bytes:
    """Compresse les données en appliquant BWT, RLE puis Huffman."""
    if not data:
        return MAGIC + struct.pack(">I", 0)
    blocks = bwt_encode_bytes(data, block_size=block_size)
    output = bytearray(MAGIC + struct.pack(">I", len(blocks)))
    for bwt_chunk, primary_idx in blocks:
        rle_chunk = rle_encode_bytes(bwt_chunk)
        huff_chunk = huffman_compress_bytes(rle_chunk)
        output.extend(struct.pack(">III", primary_idx, len(bwt_chunk), len(huff_chunk)))
        output.extend(huff_chunk)
    return bytes(output)

def bzip2_custom_decompress(compressed_data: bytes) -> bytes:
    """Décompresse les données en appliquant Huffman inverse, RLE inverse, puis BWT inverse."""
    if not compressed_data or len(compressed_data) < 8:
        return b""
    if compressed_data[:4] != MAGIC:
        raise ValueError("Signature bzip2 Custom non reconnue.")
    num_blocks = struct.unpack(">I", compressed_data[4:8])[0]
    offset = 8
    restored = []
    for _ in range(num_blocks):
        primary_idx, orig_len, huff_len = struct.unpack(">III", compressed_data[offset:offset + 12])
        offset += 12
        huff_chunk = compressed_data[offset:offset + huff_len]
        offset += huff_len
        rle_chunk = huffman_decompress_bytes(huff_chunk)
        bwt_chunk = rle_decode_bytes(rle_chunk)
        chunk = bwt_decode_bytes([(bwt_chunk, primary_idx)])
        restored.append(chunk)
    return b"".join(restored)
