import base64
import hashlib
import hmac
import json

import pytest
from Crypto.Cipher import DES

from src.des_cipher import AuthenticationError, InvalidPayloadError, _derive_keys, decrypt, encrypt


def _read_payload(payload):
    return json.loads(base64.urlsafe_b64decode(payload.split(":", 1)[1]))


def _write_payload(data):
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("ascii")
    return "DES1:" + base64.urlsafe_b64encode(encoded).decode("ascii")


def test_des_round_trip_unicode_and_payload_metadata():
    message = "Hello 🔐 — नमस्ते"
    payload = encrypt(message, "correct horse battery staple")
    assert payload.startswith("DES1:")
    data = _read_payload(payload)
    assert {"version", "cipher", "mode", "padding", "kdf", "iterations", "salt", "iv", "ciphertext", "tag"} == set(data)
    assert data["cipher"] == "DES" and data["mode"] == "CBC"
    assert decrypt(payload, "correct horse battery staple") == message


def test_des_encryption_generates_fresh_salt_and_iv():
    first = _read_payload(encrypt("same message", "secret"))
    second = _read_payload(encrypt("same message", "secret"))
    assert first["salt"] != second["salt"]
    assert first["iv"] != second["iv"]


def test_des_rejects_wrong_password():
    with pytest.raises(AuthenticationError, match="incorrect or the payload was modified"):
        decrypt(encrypt("private text", "right password"), "wrong password")


@pytest.mark.parametrize("field", ["ciphertext", "tag", "iv", "iterations"])
def test_des_rejects_tampered_payload_fields(field):
    payload = encrypt("tamper me", "secret")
    data = _read_payload(payload)
    if field == "iterations":
        data[field] -= 1
    else:
        raw = bytearray(base64.b64decode(data[field]))
        raw[0] ^= 1
        data[field] = base64.b64encode(raw).decode("ascii")
    with pytest.raises(AuthenticationError):
        decrypt(_write_payload(data), "secret")


def test_des_rejects_authenticated_invalid_pkcs7_padding_without_oracle():
    password, salt, iterations = b"secret", bytes(range(16)), 100_000
    encryption_key, authentication_key = _derive_keys(password, salt, iterations)
    iv = bytes(range(16, 24))
    # This one-block plaintext ends with pad byte 0, which PKCS#7 forbids.
    invalid_padded = b"1234567\x00"
    ciphertext = DES.new(encryption_key, DES.MODE_CBC, iv=iv).encrypt(invalid_padded)
    data = {
        "version": 1, "cipher": "DES", "mode": "CBC", "padding": "PKCS7",
        "kdf": "PBKDF2-HMAC-SHA-256", "iterations": iterations,
        "salt": base64.b64encode(salt).decode("ascii"),
        "iv": base64.b64encode(iv).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("ascii")
    data["tag"] = base64.b64encode(hmac.new(authentication_key, canonical, hashlib.sha256).digest()).decode("ascii")
    with pytest.raises(AuthenticationError, match="Authentication failed"):
        decrypt(_write_payload(data), password.decode())


@pytest.mark.parametrize("password", ["", None, 12])
def test_des_requires_a_nonempty_text_password(password):
    with pytest.raises(ValueError, match="Password"):
        encrypt("hello", password)


def test_des_rejects_empty_plaintext():
    with pytest.raises(ValueError, match="empty"):
        encrypt("", "secret")


@pytest.mark.parametrize("payload", ["", "not a payload", "DES1:!!!", "DES2:abc"])
def test_des_rejects_malformed_or_unsupported_payload(payload):
    with pytest.raises(InvalidPayloadError):
        decrypt(payload, "secret")
