""" Algorithme LZ77 """

def lz77_encode_text(text: str, search_buffer_size: int = 7, lookahead_size: int = 6):
    """Génère les triplets (Distance, Longueur, Caractère) selon la fenêtre glissante."""
    if not text:
        return []
    triplets = []
    cursor = 0
    n = len(text)

    while cursor < n:
        search_start = max(0, cursor - search_buffer_size)
        search_buf = text[search_start:cursor]
        lookahead = text[cursor:cursor + lookahead_size]
        best_dist = 0
        best_len = 0
        best_char = lookahead[0]

        # Cherche la plus longue correspondance dans la fenêtre de recherche
        for length in range(1, len(lookahead)):
            sub = lookahead[:length]
            pos = search_buf.rfind(sub)
            if pos != -1:
                best_dist = len(search_buf) - pos
                best_len = length
                best_char = lookahead[length]

        if best_len == 0:
            cursor += 1
        else:
            cursor += best_len + 1
        triplets.append((best_dist, best_len, best_char))
    return triplets

def lz77_decode_text(triplets: list) -> str:
    """Reconstitue le texte à partir des triplets (distance, longueur, caractère)."""
    decoded = []
    for dist, length, char in triplets:
        if dist > 0:
            start_pos = len(decoded) - dist
            for i in range(length):
                decoded.append(decoded[start_pos + i])
        if char:
            decoded.append(char)
    return "".join(decoded)
