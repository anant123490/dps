"""Password-based AES-GCM encryption with a portable, versioned payload."""

import base64
import binascii
import json
from typing import Any

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

VERSION_PREFIX = "CLT1:"
KDF_NAME = "PBKDF2-HMAC-SHA-256"
DEFAULT_ITERATIONS = 600_000
MIN_ITERATIONS = 100_000
MAX_ITERATIONS = 2_000_000
SALT_BYTES = 16
NONCE_BYTES = 12
TAG_BYTES = 16
KEY_BYTES = 16


class InvalidPayloadError(ValueError):
    """The input is not a supported or well-formed toolkit payload."""


class AuthenticationError(ValueError):
    """The passphrase is wrong or the encrypted data was changed."""


def _validate_passphrase(passphrase: str) -> bytes:
    if not isinstance(passphrase, str) or not passphrase:
        raise ValueError("Passphrase must be a non-empty string.")
    return passphrase.encode("utf-8")


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64decode(value: Any, field: str) -> bytes:
    if not isinstance(value, str):
        raise InvalidPayloadError(f"Payload field '{field}' must be Base64 text.")
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
        raise InvalidPayloadError(f"Payload field '{field}' is not valid Base64.") from exc


def _derive_key(passphrase: bytes, salt: bytes, iterations: int) -> bytes:
    return PBKDF2(passphrase, salt, dkLen=KEY_BYTES, count=iterations, hmac_hash_module=SHA256)


def encrypt(plaintext: str, passphrase: str) -> str:
    """Encrypt UTF-8 text and return a copyable ``CLT1:`` Base64 payload."""
    if not isinstance(plaintext, str):
        raise ValueError("Plaintext must be a string.")
    if not plaintext:
        raise ValueError("Plaintext must not be empty.")
    password_bytes = _validate_passphrase(passphrase)
    salt = get_random_bytes(SALT_BYTES)
    nonce = get_random_bytes(NONCE_BYTES)
    key = _derive_key(password_bytes, salt, DEFAULT_ITERATIONS)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=TAG_BYTES)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))

    data = {
        "version": 1,
        "kdf": KDF_NAME,
        "iterations": DEFAULT_ITERATIONS,
        "salt": _b64encode(salt),
        "nonce": _b64encode(nonce),
        "ciphertext": _b64encode(ciphertext),
        "tag": _b64encode(tag),
    }
    encoded_json = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload = base64.urlsafe_b64encode(encoded_json).decode("ascii")
    return VERSION_PREFIX + payload


def _parse_payload(payload: str) -> tuple[bytes, bytes, bytes, bytes, int]:
    if not isinstance(payload, str) or not payload.strip():
        raise InvalidPayloadError("Ciphertext payload must be non-empty text.")
    token = payload.strip()
    if not token.startswith(VERSION_PREFIX):
        raise InvalidPayloadError("Unsupported payload. Expected a CLT1: versioned AES payload.")
    try:
        encoded = token[len(VERSION_PREFIX):].encode("ascii")
        raw_json = base64.b64decode(encoded, altchars=b"-_", validate=True)
        data = json.loads(raw_json.decode("utf-8"))
    except (UnicodeEncodeError, binascii.Error, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidPayloadError("Ciphertext payload is malformed or not valid Base64.") from exc

    expected_fields = {"version", "kdf", "iterations", "salt", "nonce", "ciphertext", "tag"}
    if not isinstance(data, dict) or set(data) != expected_fields:
        raise InvalidPayloadError("Ciphertext payload has missing or unexpected fields.")
    if data["version"] != 1 or isinstance(data["version"], bool) or data["kdf"] != KDF_NAME:
        raise InvalidPayloadError("Ciphertext payload uses an unsupported version or key derivation method.")
    iterations = data["iterations"]
    if isinstance(iterations, bool) or not isinstance(iterations, int) or not MIN_ITERATIONS <= iterations <= MAX_ITERATIONS:
        raise InvalidPayloadError("Ciphertext payload has an unsafe or unsupported PBKDF2 iteration count.")

    salt = _b64decode(data["salt"], "salt")
    nonce = _b64decode(data["nonce"], "nonce")
    ciphertext = _b64decode(data["ciphertext"], "ciphertext")
    tag = _b64decode(data["tag"], "tag")
    if len(salt) != SALT_BYTES:
        raise InvalidPayloadError("Ciphertext payload has an invalid salt length.")
    if len(nonce) != NONCE_BYTES:
        raise InvalidPayloadError("Ciphertext payload has an invalid nonce length.")
    if len(tag) != TAG_BYTES:
        raise InvalidPayloadError("Ciphertext payload has an invalid authentication tag length.")
    return salt, nonce, ciphertext, tag, iterations


def decrypt(payload: str, passphrase: str) -> str:
    """Authenticate and decrypt a toolkit AES payload to UTF-8 text."""
    password_bytes = _validate_passphrase(passphrase)
    salt, nonce, ciphertext, tag, iterations = _parse_payload(payload)
    key = _derive_key(password_bytes, salt, iterations)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=TAG_BYTES)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError as exc:
        raise AuthenticationError("Authentication failed: the passphrase is incorrect or the payload was modified.") from exc
    try:
        return plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuthenticationError("Authenticated plaintext is not valid UTF-8 text.") from exc
