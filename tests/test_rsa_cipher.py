import pytest

from src.rsa_cipher import (
    RSAInputError,
    decrypt,
    encrypt,
    export_private_key,
    export_public_key,
    generate_key_pair,
    import_private_key,
    import_public_key,
    max_message_bytes,
)


@pytest.fixture(scope="module")
def key_pair():
    return generate_key_pair(2048)


def test_rsa_oaep_round_trip_and_public_private_key_handling(key_pair):
    private_key, public_key = key_pair
    public_pem = export_public_key(public_key)
    imported_public = import_public_key(public_pem)
    imported_private = import_private_key(private_key.export_key())
    ciphertext = encrypt("Hello RSA 🔑", imported_public)
    assert decrypt(ciphertext, imported_private) == "Hello RSA 🔑"
    assert len(ciphertext) > 0


def test_rsa_private_export_is_password_protected_and_importable(key_pair):
    private_key, _ = key_pair
    protected = export_private_key(private_key, "file password")
    assert "ENCRYPTED" in protected
    assert import_private_key(protected, "file password").has_private()
    with pytest.raises(RSAInputError, match="key password"):
        import_private_key(protected, "wrong password")


def test_rsa_key_size_validation(key_pair):
    with pytest.raises(RSAInputError, match="2048 or 3072"):
        generate_key_pair(1024)
    private_key, _ = key_pair
    with pytest.raises(RSAInputError, match="public key"):
        import_public_key(private_key.export_key())
    with pytest.raises(RSAInputError, match="private key"):
        import_private_key(export_public_key(private_key))


def test_rsa_can_generate_3072_bit_keys():
    private_key, public_key = generate_key_pair(3072)
    assert private_key.size_in_bits() == 3072
    assert public_key.size_in_bits() == 3072


def test_rsa_rejects_oversized_message(key_pair):
    _, public_key = key_pair
    with pytest.raises(RSAInputError, match="UTF-8 bytes.*at most"):
        encrypt("x" * (max_message_bytes(public_key) + 1), public_key)


def test_rsa_rejects_empty_message(key_pair):
    _, public_key = key_pair
    with pytest.raises(RSAInputError, match="must not be empty"):
        encrypt("", public_key)


def test_rsa_rejects_malformed_ciphertext(key_pair):
    private_key, _ = key_pair
    with pytest.raises(RSAInputError, match="Base64"):
        decrypt("not base64!", private_key)
    with pytest.raises(RSAInputError, match="requires exactly"):
        decrypt("YQ==", private_key)


def test_rsa_rejects_ciphertext_with_wrong_private_key(key_pair):
    _, public_key = key_pair
    wrong_private_key, _ = generate_key_pair(2048)
    ciphertext = encrypt("message for the first key", public_key)
    with pytest.raises(RSAInputError, match="invalid or was made for a different key"):
        decrypt(ciphertext, wrong_private_key)


def test_rsa_rejects_invalid_public_key():
    with pytest.raises(RSAInputError, match="Could not read"):
        import_public_key("not a PEM key")


def test_rsa_requires_export_password(key_pair):
    private_key, _ = key_pair
    with pytest.raises(RSAInputError, match="export password"):
        export_private_key(private_key, "")
