"""API integration tests for the React client endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

import app as app_entrypoint

client = TestClient(app)


def test_health_and_caesar_round_trip():
    assert client.get("/api/health").json()["status"] == "ok"
    encrypted = client.post("/api/caesar/encrypt", json={"text": "HeLLo, 世界!", "shift": 3})
    assert encrypted.status_code == 200
    assert encrypted.json()["result"] == "KhOOr, 世界!"
    decrypted = client.post("/api/caesar/decrypt", json={"text": encrypted.json()["result"], "shift": 3})
    assert decrypted.json()["result"] == "HeLLo, 世界!"


def test_app_entrypoint_exports_the_fastapi_app():
    assert app_entrypoint.app is app


def test_api_rejects_empty_text_and_out_of_range_shift():
    assert client.post("/api/caesar/encrypt", json={"text": "", "shift": 3}).status_code == 400
    assert client.post("/api/caesar/encrypt", json={"text": "abc", "shift": 26}).status_code == 400
    assert client.post("/api/caesar/encrypt", json={"text": "abc", "shift": True}).status_code == 422


def test_aes_encrypt_decrypt_and_reject_wrong_password():
    encrypted = client.post("/api/aes/encrypt", json={"plaintext": "Secure 🌍 text", "password": "right password"})
    assert encrypted.status_code == 200
    payload = encrypted.json()["payload"]
    decrypted = client.post("/api/aes/decrypt", json={"payload": payload, "password": "right password"})
    assert decrypted.json()["plaintext"] == "Secure 🌍 text"
    wrong_password = client.post("/api/aes/decrypt", json={"payload": payload, "password": "wrong password"})
    assert wrong_password.status_code == 400
    assert "Authentication failed" in wrong_password.json()["detail"]


def test_aes_rejects_empty_and_tampered_payload():
    assert client.post("/api/aes/encrypt", json={"plaintext": "", "password": "pass"}).status_code == 400
    payload = client.post("/api/aes/encrypt", json={"plaintext": "text", "password": "pass"}).json()["payload"]
    tampered = payload[:-1] + ("A" if payload[-1] != "A" else "B")
    response = client.post("/api/aes/decrypt", json={"payload": tampered, "password": "pass"})
    assert response.status_code == 400


def test_aes_encryption_uses_fresh_random_salt_and_nonce():
    first = client.post("/api/aes/encrypt", json={"plaintext": "same", "password": "same password"}).json()["payload"]
    second = client.post("/api/aes/encrypt", json={"plaintext": "same", "password": "same password"}).json()["payload"]
    assert first != second


@pytest.fixture(scope="module")
def generated_pair():
    response = client.post("/api/rsa/keys", json={"bits": 2048})
    assert response.status_code == 200
    return response.json()


def test_rsa_generate_validate_encrypt_decrypt_and_explicit_export(generated_pair):
    pair = generated_pair
    assert pair["bits"] == 2048
    checked = client.post("/api/rsa/validate-public", json={"public_key": pair["public_key"]})
    assert checked.json()["max_message_bytes"] == 190
    encrypted = client.post("/api/rsa/encrypt", json={"plaintext": "Hello RSA 🔑", "public_key": pair["public_key"]})
    assert encrypted.status_code == 200
    assert client.post("/api/rsa/decrypt", json={"ciphertext": encrypted.json()["ciphertext"], "key_id": pair["key_id"]}).json()["plaintext"] == "Hello RSA 🔑"
    protected = client.post("/api/rsa/export-private", json={"key_id": pair["key_id"], "password": "secure demo password"})
    assert protected.status_code == 200
    assert "ENCRYPTED" in protected.json()["private_key"]
    private_pem = protected.json()["private_key"]
    validated = client.post("/api/rsa/validate-private", json={"private_key": private_pem, "private_key_password": "secure demo password"})
    assert validated.status_code == 200
    assert validated.json()["bits"] == 2048


def test_rsa_rejects_invalid_key_ciphertext_and_oversize(generated_pair):
    pair = generated_pair
    invalid_key = client.post("/api/rsa/validate-public", json={"public_key": "not a pem key"})
    assert invalid_key.status_code == 400
    bad_base64 = client.post("/api/rsa/decrypt", json={"ciphertext": "bad base64!", "key_id": pair["key_id"]})
    assert bad_base64.status_code == 400
    too_long = client.post("/api/rsa/encrypt", json={"plaintext": "x" * 191, "public_key": pair["public_key"]})
    assert too_long.status_code == 400
    assert "at most 190 bytes" in too_long.json()["detail"]
    empty = client.post("/api/rsa/encrypt", json={"plaintext": "", "public_key": pair["public_key"]})
    assert empty.status_code == 400


def test_rsa_imported_private_key_and_numerical_example(generated_pair):
    pair = generated_pair
    assert client.post("/api/rsa/demo").status_code == 405
    demo = client.get("/api/rsa/demo").json()
    assert demo["ciphertext"] == 31
    assert demo["decrypted"] == 4
    assert demo["verified"] is True
    assert client.post("/api/rsa/export-private", json={"key_id": pair["key_id"], "password": "short"}).status_code == 400

