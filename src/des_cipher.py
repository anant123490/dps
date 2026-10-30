"""Password-based DES-CBC for a deliberately educational demonstration.

DES is obsolete and must not be used to protect real data. This module adds
encrypt-then-MAC authentication so the demo rejects wrong passwords and edits
before CBC decryption. It is still not a recommendation to use DES.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
from typing import Any

from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

VERSION_PREFIX = "DES1:"
KDF_NAME = "PBKDF2-HMAC-SHA-256"
DEFAULT_ITERATIONS = 600_000
MIN_ITERATIONS = 100_000
MAX_ITERATIONS = 2_000_000
SALT_BYTES = 16
IV_BYTES = DES.block_size
DES_KEY_BYTES = 8
MAC_KEY_BYTES = 32
TAG_BYTES = hashlib.sha256().digest_size
_FIELDS = {
    "version", "cipher", "mode", "padding", "kdf", "iterations",
    "salt", "iv", "ciphertext", "tag",
}


class InvalidPayloadError(ValueError):
    """The input is not a supported or well-formed toolkit payload."""


class AuthenticationError(ValueError):
    """The password is wrong or the payload was changed."""


def _validate_password(password: str) -> bytes:
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")
    try:
        return password.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("Password must contain valid Unicode text.") from exc


def _derive_keys(password: bytes, salt: bytes, iterations: int) -> tuple[bytes, bytes]:
    # Separate encryption and authentication key material from one PBKDF2 run.
    material = hashlib.pbkdf2_hmac("sha256", password, salt, iterations, dklen=DES_KEY_BYTES + MAC_KEY_BYTES)
    return material[:DES_KEY_BYTES], material[DES_KEY_BYTES:]


def _canonical_bytes(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _b64decode(value: Any, field: str) -> bytes:
    if not isinstance(value, str):
        raise InvalidPayloadError(f"Payload field '{field}' must be Base64 text.")
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
        raise InvalidPayloadError(f"Payload field '{field}' is not valid Base64.") from exc


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt text and return a ``DES1:`` URL-safe Base64 payload."""
    if not isinstance(plaintext, str):
        raise ValueError("Plaintext must be a string.")
    if not plaintext:
        raise ValueError("Plaintext must not be empty.")
    password_bytes = _validate_password(password)
    try:
        plaintext_bytes = plaintext.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("Plaintext must contain valid Unicode text.") from exc

    salt = get_random_bytes(SALT_BYTES)
    iv = get_random_bytes(IV_BYTES)
    encryption_key, authentication_key = _derive_keys(password_bytes, salt, DEFAULT_ITERATIONS)
    ciphertext = DES.new(encryption_key, DES.MODE_CBC, iv=iv).encrypt(pad(plaintext_bytes, IV_BYTES))

    data: dict[str, Any] = {
        "version": 1,
        "cipher": "DES",
        "mode": "CBC",
        "padding": "PKCS7",
        "kdf": KDF_NAME,
        "iterations": DEFAULT_ITERATIONS,
        "salt": _b64encode(salt),
        "iv": _b64encode(iv),
        "ciphertext": _b64encode(ciphertext),
    }
    data["tag"] = _b64encode(hmac.new(authentication_key, _canonical_bytes(data), hashlib.sha256).digest())
    encoded = base64.urlsafe_b64encode(_canonical_bytes(data)).decode("ascii")
    return VERSION_PREFIX + encoded


def _parse_payload(payload: str) -> tuple[dict[str, Any], bytes, bytes, bytes, bytes]:
    if not isinstance(payload, str) or not payload.strip():
        raise InvalidPayloadError("Ciphertext payload must be non-empty text.")
    token = payload.strip()
    if not token.startswith(VERSION_PREFIX):
        raise InvalidPayloadError("Unsupported payload. Expected a DES1: versioned DES payload.")
    try:
        encoded = token[len(VERSION_PREFIX):].encode("ascii")
        raw_json = base64.b64decode(encoded, altchars=b"-_", validate=True)
        data = json.loads(raw_json.decode("utf-8"))
    except (UnicodeEncodeError, binascii.Error, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidPayloadError("Ciphertext payload is malformed or not valid Base64.") from exc

    if not isinstance(data, dict) or set(data) != _FIELDS:
        raise InvalidPayloadError("Ciphertext payload has missing or unexpected fields.")
    if (data["version"] != 1 or isinstance(data["version"], bool)
            or data["cipher"] != "DES" or data["mode"] != "CBC"
            or data["padding"] != "PKCS7" or data["kdf"] != KDF_NAME):
        raise InvalidPayloadError("Ciphertext payload uses an unsupported version or algorithm setting.")
    iterations = data["iterations"]
    if isinstance(iterations, bool) or not isinstance(iterations, int) or not MIN_ITERATIONS <= iterations <= MAX_ITERATIONS:
        raise InvalidPayloadError("Ciphertext payload has an unsafe or unsupported PBKDF2 iteration count.")

    salt = _b64decode(data["salt"], "salt")
    iv = _b64decode(data["iv"], "iv")
    ciphertext = _b64decode(data["ciphertext"], "ciphertext")
    tag = _b64decode(data["tag"], "tag")
    if len(salt) != SALT_BYTES or len(iv) != IV_BYTES or len(tag) != TAG_BYTES:
        raise InvalidPayloadError("Ciphertext payload has an invalid salt, IV, or authentication tag length.")
    if not ciphertext or len(ciphertext) % IV_BYTES:
        raise InvalidPayloadError("Ciphertext must contain complete DES blocks.")
    return data, salt, iv, ciphertext, tag


def decrypt(payload: str, password: str) -> str:
    """Authenticate the payload before decrypting and unpadding the message."""
    password_bytes = _validate_password(password)
    data, salt, iv, ciphertext, tag = _parse_payload(payload)
    encryption_key, authentication_key = _derive_keys(password_bytes, salt, data["iterations"])
    authenticated_data = {key: value for key, value in data.items() if key != "tag"}
    expected_tag = hmac.new(authentication_key, _canonical_bytes(authenticated_data), hashlib.sha256).digest()
    if not hmac.compare_digest(expected_tag, tag):
        raise AuthenticationError("Authentication failed: the password is incorrect or the payload was modified.")

    padded = DES.new(encryption_key, DES.MODE_CBC, iv=iv).decrypt(ciphertext)
    try:
        plaintext = unpad(padded, IV_BYTES)
        return plaintext.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        # Authenticated malformed plaintext should not reveal CBC padding details.
        raise AuthenticationError("Authentication failed: the password is incorrect or the payload was modified.") from exc
