"""RSA-OAEP helpers for small-message demonstrations and key management."""

import base64
import binascii

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

SUPPORTED_GENERATION_SIZES = (2048, 3072)
OAEP_HASH_BYTES = SHA256.digest_size


class RSAInputError(ValueError):
    """A key, message, or ciphertext is invalid for RSA-OAEP."""


def _require_key_size(key: RSA.RsaKey) -> RSA.RsaKey:
    if not isinstance(key, RSA.RsaKey):
        raise RSAInputError("A valid RSA key is required.")
    if key.size_in_bits() < 2048:
        raise RSAInputError("RSA keys must be at least 2048 bits.")
    return key


def generate_key_pair(bits: int = 2048) -> tuple[RSA.RsaKey, RSA.RsaKey]:
    """Generate and return ``(private_key, public_key)``."""
    if isinstance(bits, bool) or not isinstance(bits, int) or bits not in SUPPORTED_GENERATION_SIZES:
        raise RSAInputError("Choose a supported RSA key size: 2048 or 3072 bits.")
    private_key = RSA.generate(bits)
    return private_key, private_key.public_key()


def import_public_key(pem: str | bytes) -> RSA.RsaKey:
    """Import and validate a public-only RSA PEM key."""
    if not pem:
        raise RSAInputError("Public key is required.")
    try:
        key = RSA.import_key(pem)
    except (ValueError, IndexError, TypeError) as exc:
        raise RSAInputError("Could not read this RSA public key. Check the PEM text.") from exc
    if key.has_private():
        raise RSAInputError("Paste a public key here; this field does not accept private keys.")
    return _require_key_size(key)


def import_private_key(pem: str | bytes, passphrase: str | bytes | None = None) -> RSA.RsaKey:
    """Import and validate an RSA private PEM key."""
    if not pem:
        raise RSAInputError("Private key is required.")
    if isinstance(passphrase, str):
        passphrase = passphrase.encode("utf-8") or None
    try:
        key = RSA.import_key(pem, passphrase=passphrase)
    except (ValueError, IndexError, TypeError) as exc:
        raise RSAInputError("Could not read this RSA private key. Check the PEM text and key password.") from exc
    if not key.has_private():
        raise RSAInputError("A private key is required for RSA decryption.")
    return _require_key_size(key)


def export_public_key(key: RSA.RsaKey) -> str:
    """Export only the public portion of an RSA key in PEM format."""
    _require_key_size(key)
    return key.public_key().export_key(format="PEM").decode("ascii")


def export_private_key(key: RSA.RsaKey, export_password: str) -> str:
    """Export a private key as password-protected PKCS#8 PEM."""
    if not isinstance(export_password, str) or not export_password:
        raise RSAInputError("Set a non-empty export password to protect the private key file.")
    _require_key_size(key)
    if not key.has_private():
        raise RSAInputError("A private RSA key is required for private-key export.")
    try:
        encoded = key.export_key(
            format="PEM",
            passphrase=export_password.encode("utf-8"),
            pkcs=8,
            protection="PBKDF2WithHMAC-SHA512AndAES256-CBC",
            prot_params={"iteration_count": 131_072},
        )
    except (ValueError, TypeError) as exc:
        raise RSAInputError("Could not protect and export this private key.") from exc
    return encoded.decode("ascii")


def max_message_bytes(key: RSA.RsaKey) -> int:
    """Return the OAEP/SHA-256 plaintext byte limit for this RSA key."""
    _require_key_size(key)
    return key.size_in_bytes() - 2 * OAEP_HASH_BYTES - 2


def encrypt(plaintext: str, public_key: RSA.RsaKey) -> str:
    """Encrypt UTF-8 text with RSA-OAEP/SHA-256 and return standard Base64."""
    if not isinstance(plaintext, str):
        raise RSAInputError("Plaintext must be text.")
    if not plaintext:
        raise RSAInputError("Plaintext must not be empty.")
    _require_key_size(public_key)
    try:
        message = plaintext.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise RSAInputError("Plaintext must contain valid Unicode text.") from exc
    limit = max_message_bytes(public_key)
    if len(message) > limit:
        raise RSAInputError(
            f"Message is {len(message)} UTF-8 bytes; this key allows at most {limit} bytes with OAEP/SHA-256."
        )
    cipher = PKCS1_OAEP.new(public_key.public_key(), hashAlgo=SHA256)
    encrypted = cipher.encrypt(message)
    return base64.b64encode(encrypted).decode("ascii")


def decrypt(ciphertext_base64: str, private_key: RSA.RsaKey) -> str:
    """Decrypt a standard Base64 RSA-OAEP/SHA-256 ciphertext."""
    if not isinstance(ciphertext_base64, str) or not ciphertext_base64.strip():
        raise RSAInputError("Ciphertext must be non-empty Base64 text.")
    _require_key_size(private_key)
    if not private_key.has_private():
        raise RSAInputError("A private RSA key is required for decryption.")
    try:
        encrypted = base64.b64decode(ciphertext_base64.strip().encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
        raise RSAInputError("Ciphertext is not valid standard Base64.") from exc
    if len(encrypted) != private_key.size_in_bytes():
        raise RSAInputError(
            f"Ciphertext has {len(encrypted)} bytes; this key requires exactly {private_key.size_in_bytes()} bytes."
        )
    cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
    try:
        plaintext = cipher.decrypt(encrypted)
    except ValueError as exc:
        raise RSAInputError("RSA decryption failed: ciphertext is invalid or was made for a different key.") from exc
    try:
        return plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RSAInputError("Decrypted message is not valid UTF-8 text.") from exc
