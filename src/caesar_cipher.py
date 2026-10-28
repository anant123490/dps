"""A small Caesar cipher implementation for learning and demonstrations."""


def _validate_shift(shift: int) -> None:
    if isinstance(shift, bool) or not isinstance(shift, int):
        raise ValueError("Shift must be an integer from 0 to 25.")
    if not 0 <= shift <= 25:
        raise ValueError("Shift must be between 0 and 25.")


def _transform(text: str, shift: int) -> str:
    if not isinstance(text, str):
        raise ValueError("Text must be a string.")
    _validate_shift(shift)

    output: list[str] = []
    for char in text:
        if "A" <= char <= "Z":
            output.append(chr((ord(char) - ord("A") + shift) % 26 + ord("A")))
        elif "a" <= char <= "z":
            output.append(chr((ord(char) - ord("a") + shift) % 26 + ord("a")))
        else:
            output.append(char)
    return "".join(output)


def encrypt(text: str, shift: int) -> str:
    """Encrypt text while leaving non-English letters unchanged."""
    return _transform(text, shift)


def decrypt(text: str, shift: int) -> str:
    """Decrypt text produced with the same shift."""
    _validate_shift(shift)
    return _transform(text, (26 - shift) % 26)
