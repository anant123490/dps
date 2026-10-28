import base64
import json

import pytest

from src.aes_cipher import AuthenticationError, InvalidPayloadError, decrypt, encrypt


def test_aes_round_trip_unicode_and_payload_format():
    text = "Hello 🔐 — नमस्ते"
    payload = encrypt(text, "correct horse battery staple")
    assert payload.startswith("CLT1:")
    assert decrypt(payload, "correct horse battery staple") == text


def test_aes_encryption_uses_fresh_random_values():
    first = encrypt("same", "secret")
    second = encrypt("same", "secret")
    assert first != second
    first_data = _payload_data(first)
    second_data = _payload_data(second)
    assert first_data["salt"] != second_data["salt"]
    assert first_data["nonce"] != second_data["nonce"]


def test_aes_rejects_wrong_passphrase():
    payload = encrypt("private text", "right password")
    with pytest.raises(AuthenticationError, match="incorrect or the payload was modified"):
        decrypt(payload, "wrong password")


@pytest.mark.parametrize("field", ["ciphertext", "tag"])
def test_aes_rejects_tampered_ciphertext_or_tag(field):
    payload = encrypt("tamper me", "secret")
    prefix, _ = payload.split(":", 1)
    data = _payload_data(payload)
    changed = bytearray(base64.b64decode(data[field]))
    changed[0] ^= 1
    data[field] = base64.b64encode(changed).decode("ascii")
    modified = prefix + ":" + base64.urlsafe_b64encode(json.dumps(data).encode()).decode("ascii")
    with pytest.raises(AuthenticationError):
        decrypt(modified, "secret")


@pytest.mark.parametrize("passphrase", ["", None, 42])
def test_aes_requires_nonempty_text_passphrase(passphrase):
    with pytest.raises(ValueError, match="Passphrase"):
        encrypt("hello", passphrase)


def test_aes_rejects_empty_plaintext():
    with pytest.raises(ValueError, match="empty"):
        encrypt("", "secret")


@pytest.mark.parametrize("payload", ["", "not a payload", "CLT1:!!!", "CLT2:abc"])
def test_aes_rejects_malformed_or_unsupported_payload(payload):
    with pytest.raises(InvalidPayloadError):
        decrypt(payload, "secret")


def _payload_data(payload):
    _, encoded = payload.split(":", 1)
    return json.loads(base64.urlsafe_b64decode(encoded))
