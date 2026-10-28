import pytest

from src.caesar_cipher import decrypt, encrypt


def test_caesar_preserves_case_punctuation_digits_and_spaces():
    original = "Hello, World! 123"
    assert encrypt(original, 3) == "Khoor, Zruog! 123"
    assert decrypt("Khoor, Zruog! 123", 3) == original


@pytest.mark.parametrize("shift", [0, 25])
def test_caesar_shift_boundaries_round_trip(shift):
    text = "Abc xyz!"
    assert decrypt(encrypt(text, shift), shift) == text


@pytest.mark.parametrize("shift", [-1, 26, 1.5, True, "3"])
def test_caesar_rejects_invalid_shifts(shift):
    with pytest.raises(ValueError, match="Shift"):
        encrypt("hello", shift)


def test_caesar_rejects_non_text():
    with pytest.raises(ValueError, match="Text"):
        encrypt(b"hello", 2)
