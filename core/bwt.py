""" BWT """

def bwt_encode_text(text: str):
    """Génère les rotations, les trie et extrait la dernière colonne avec l'indice initial."""
    if not text:
        return "", 1
    n = len(text)
    rotations = sorted(text[i:] + text[:i] for i in range(n))
    last_col = "".join(r[-1] for r in rotations)
    primary_idx = rotations.index(text) + 1
    return last_col, primary_idx


def bwt_decode_text_steps(last_col: str, primary_idx: int):
    """Reconstitue le texte selon la méthode matricielle pas-à-pas (colonnes C1..Cn)."""
    if not last_col:
        return "", []
    n = len(last_col)
    table = [""] * n
    history = []
    for step in range(n):
        table = [last_col[i] + table[i] for i in range(n)]
        history.append((f"C{step * 2 + 1}", list(table)))
        table.sort()
        history.append((f"C{step * 2 + 2} (Tri)", list(table)))
    return table[primary_idx - 1], history

def bwt_encode_bytes(data: bytes, block_size: int = 65536):
    """Encode un flux d'octets par blocs via tri d'indices."""
    if not data:
        return []
    results = []
    for start in range(0, len(data), block_size):
        chunk = data[start:start + block_size]
        n = len(chunk)
        # Tri indirect des rotations virtuelles
        double = chunk + chunk
        indices = list(range(n))
        indices.sort(key=lambda i: double[i:i + n])
        last_col = bytes([chunk[(i - 1 + n) % n] for i in indices])
        primary_idx = indices.index(0)
        results.append((last_col, primary_idx))
    return results


def bwt_decode_bytes(bwt_blocks: list) -> bytes:
    """Décode les blocs BWT à l'aide du vecteur de correspondance LF."""
    decoded = []
    for last_col, primary_idx in bwt_blocks:
        n = len(last_col)
        if n == 0:
            continue
        first_col = sorted((last_col[i], i) for i in range(n))
        chunk = bytearray(n)
        curr = primary_idx
        for step in range(n):
            val, curr = first_col[curr]
            chunk[step] = val
        decoded.append(bytes(chunk))
    return b"".join(decoded)
