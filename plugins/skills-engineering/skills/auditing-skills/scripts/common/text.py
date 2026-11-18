"""Text helpers the checks measure and quote with."""


def utf16_len(s: str) -> int:
    """Length of s in UTF-16 code units: a character outside the BMP counts as two."""
    return len(s.encode("utf-16-le", errors="surrogatepass")) // 2


def snippet(s: str, index: int, width: int = 40) -> str:
    """The text around index, width characters on each side, with '|' marking the index."""
    start = max(0, index - width)
    return f"{s[start:index]}|{s[index : index + width]}"
