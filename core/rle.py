""" Codage RLE """
import re

def rle_encode_text(text: str) -> str:
    """Encode une chaîne de caractères en RLE (ex: AAAABBBCCDAA -> 4A3B2C1D2A)."""
    if not text:
        return ""
    encoded = []
    i = 0
    n = len(text)
    while i < n:
        char = text[i]
        count = 1
        while i + 1 < n and text[i + 1] == char:
            count += 1
            i += 1
        encoded.append(f"{count}{char}")
        i += 1
    return "".join(encoded)


def rle_decode_text(encoded_text: str) -> str:
    """Décode une chaîne RLE textuelle (ex: 4A3B2C1D2A -> AAAABBBCCDAA)."""
    if not encoded_text:
        return ""
    matches = re.findall(r"(\d+)(.)", encoded_text)
    return "".join(char * int(count) for count, char in matches)

def rle_encode_bytes(data: bytes) -> bytes:
    """Compression RLE binaire par paires (compteur, octet)."""
    if not data:
        return b""
    encoded = bytearray()
    i = 0
    n = len(data)
    while i < n:
        val = data[i]
        count = 1
        while i + 1 < n and data[i + 1] == val and count < 255:
            count += 1
            i += 1
        encoded.append(count)
        encoded.append(val)
        i += 1
    return bytes(encoded)

def rle_decode_bytes(data: bytes) -> bytes:
    """Décompression RLE binaire avec restitution exacte."""
    if not data:
        return b""
    decoded = bytearray()
    for i in range(0, len(data), 2):
        count = data[i]
        val = data[i + 1]
        decoded.extend([val] * count)
    return bytes(decoded)
