""" Codage de Huffman """

import heapq
import struct
from collections import Counter


class HuffmanNode:
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq
    def is_leaf(self):
        return self.left is None and self.right is None

def build_huffman_tree(frequencies: dict):
    """Construit l'arbre de Huffman à partir du dictionnaire des fréquences."""
    heap = [HuffmanNode(freq, sym) for sym, freq in frequencies.items()]
    heapq.heapify(heap)
    if not heap:
        return None
    if len(heap) == 1:
        single = heapq.heappop(heap)
        return HuffmanNode(single.freq, left=single)
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = HuffmanNode(n1.freq + n2.freq, left=n1, right=n2)
        heapq.heappush(heap, merged)
    return heap[0]

def generate_codes(node: HuffmanNode, prefix="", code_map=None):
    """Génère récursivement les codes binaires (0 à gauche, 1 à droite)."""
    if code_map is None:
        code_map = {}
    if node is None:
        return code_map
    if node.is_leaf():
        code_map[node.symbol] = prefix or "0"
        return code_map
    if node.left:
        generate_codes(node.left, prefix + "0", code_map)
    if node.right:
        generate_codes(node.right, prefix + "1", code_map)
    return code_map

# Fonctions pour la démonstration textuelle
def huffman_encode_text(text: str):
    """Encode une chaîne de texte et renvoie (bits, codes, arbre, fréquences)."""
    if not text:
        return "", {}, None, {}
    freqs = dict(Counter(text))
    root = build_huffman_tree(freqs)
    codes = generate_codes(root)
    bits = "".join(codes[char] for char in text)
    return bits, codes, root, freqs

def huffman_decode_text(bits: str, root: HuffmanNode) -> str:
    """Décode une suite de bits en parcourant l'arbre de la racine aux feuilles."""
    if not bits or root is None:
        return ""
    decoded = []
    curr = root
    for bit in bits:
        curr = curr.left if bit == "0" else curr.right
        if curr.is_leaf():
            decoded.append(curr.symbol)
            curr = root
    return "".join(decoded)

# Compression et décompression binaire
def huffman_compress_bytes(data: bytes) -> bytes:
    """Compresse des octets en incluant l'en-tête nécessaire pour décompresser."""
    if not data:
        return b""
    orig_len = len(data)
    freqs = Counter(data)
    root = build_huffman_tree(freqs)
    codes = generate_codes(root)

    # Concaténation des bits
    bit_str = "".join(codes[b] for b in data)
    padding = (8 - len(bit_str) % 8) % 8
    if padding:
        bit_str += "0" * padding

    # Conversion en octets
    payload = bytearray(int(bit_str[i:i + 8], 2) for i in range(0, len(bit_str), 8))

    # En-tête
    header = bytearray(struct.pack(">IH", orig_len, len(freqs)))
    for sym, count in freqs.items():
        header.extend(struct.pack(">BI", sym, count))
    return bytes(header) + bytes(payload)


def huffman_decompress_bytes(compressed: bytes) -> bytes:
    """Décompresse un flux produit par huffman_compress_bytes."""
    if not compressed:
        return b""
    orig_len, num_syms = struct.unpack(">IH", compressed[:6])
    offset = 6

    freqs = {}
    for _ in range(num_syms):
        sym, count = struct.unpack(">BI", compressed[offset:offset + 5])
        freqs[sym] = count
        offset += 5
    root = build_huffman_tree(freqs)
    if not root:
        return b""
    decoded = bytearray()
    curr = root
    for byte in compressed[offset:]:
        for bit_pos in range(7, -1, -1):
            bit = (byte >> bit_pos) & 1
            curr = curr.left if bit == 0 else curr.right
            if curr.is_leaf():
                decoded.append(curr.symbol)
                if len(decoded) == orig_len:
                    return bytes(decoded)
                curr = root
    return bytes(decoded)
