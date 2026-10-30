"""REST API for the Cryptography Learning Toolkit.

Cryptographic work delegates to the tested helpers in ``src``. RSA private
keys generated in this process stay in memory and are never persisted.
"""

from __future__ import annotations

import uuid
from threading import RLock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, StrictInt

from src import caesar_cipher, des_cipher, rsa_cipher, rsa_demo

app = FastAPI(title="Cryptography Learning Toolkit API", description="Educational Caesar, DES-CBC, and RSA-OAEP operations.", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_generated_keys: dict[str, object] = {}
_key_lock = RLock()


class CaesarRequest(BaseModel):
    text: str
    shift: StrictInt


class DESRequest(BaseModel):
    plaintext: str = ""
    payload: str = ""
    password: str


class RSAKeyRequest(BaseModel):
    bits: StrictInt


class RSAValidatePublicRequest(BaseModel):
    public_key: str


class RSAEncryptRequest(BaseModel):
    plaintext: str
    public_key: str


class RSAValidatePrivateRequest(BaseModel):
    private_key: str
    private_key_password: str = ""


class RSADecryptRequest(BaseModel):
    ciphertext: str
    private_key: str = ""
    private_key_password: str = ""
    key_id: str = ""


class RSAExportRequest(BaseModel):
    key_id: str
    password: str


def _bad_request(error: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(error))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Cryptography Learning Toolkit API"}


@app.post("/api/caesar/encrypt")
def caesar_encrypt(request: CaesarRequest) -> dict[str, str]:
    try:
        return {"result": caesar_cipher.encrypt(request.text, request.shift)}
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/caesar/decrypt")
def caesar_decrypt(request: CaesarRequest) -> dict[str, str]:
    try:
        return {"result": caesar_cipher.decrypt(request.text, request.shift)}
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/des/encrypt")
def des_encrypt(request: DESRequest) -> dict[str, str]:
    try:
        return {"payload": des_cipher.encrypt(request.plaintext, request.password)}
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/des/decrypt")
def des_decrypt(request: DESRequest) -> dict[str, str]:
    try:
        return {"plaintext": des_cipher.decrypt(request.payload, request.password)}
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/rsa/keys")
def rsa_generate_keys(request: RSAKeyRequest) -> dict[str, str | int]:
    try:
        private_key, public_key = rsa_cipher.generate_key_pair(request.bits)
        key_id = uuid.uuid4().hex
        with _key_lock:
            _generated_keys[key_id] = private_key
        return {"key_id": key_id, "public_key": rsa_cipher.export_public_key(public_key), "bits": private_key.size_in_bits()}
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/rsa/validate-public")
def rsa_validate_public(request: RSAValidatePublicRequest) -> dict[str, str | int]:
    try:
        public_key = rsa_cipher.import_public_key(request.public_key)
        return {"public_key": rsa_cipher.export_public_key(public_key), "bits": public_key.size_in_bits(), "max_message_bytes": rsa_cipher.max_message_bytes(public_key)}
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/rsa/validate-private")
def rsa_validate_private(request: RSAValidatePrivateRequest) -> dict[str, str | int]:
    try:
        private_key = rsa_cipher.import_private_key(request.private_key, request.private_key_password or None)
        return {
            "public_key": rsa_cipher.export_public_key(private_key),
            "bits": private_key.size_in_bits(),
        }
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/rsa/encrypt")
def rsa_encrypt(request: RSAEncryptRequest) -> dict[str, str | int]:
    try:
        public_key = rsa_cipher.import_public_key(request.public_key)
        return {"ciphertext": rsa_cipher.encrypt(request.plaintext, public_key), "max_message_bytes": rsa_cipher.max_message_bytes(public_key), "message_bytes": len(request.plaintext.encode("utf-8"))}
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/rsa/decrypt")
def rsa_decrypt(request: RSADecryptRequest) -> dict[str, str]:
    try:
        if request.key_id:
            with _key_lock:
                private_key = _generated_keys.get(request.key_id)
            if private_key is None:
                raise rsa_cipher.RSAInputError("This generated key is no longer available. Import its private key again.")
        else:
            private_key = rsa_cipher.import_private_key(request.private_key, request.private_key_password or None)
        return {"plaintext": rsa_cipher.decrypt(request.ciphertext, private_key)}
    except ValueError as error:
        raise _bad_request(error) from error


@app.post("/api/rsa/export-private")
def rsa_export_private(request: RSAExportRequest) -> dict[str, str]:
    try:
        if len(request.password) < 8:
            raise rsa_cipher.RSAInputError("Choose an export password of at least 8 characters.")
        with _key_lock:
            private_key = _generated_keys.get(request.key_id)
        if private_key is None:
            raise rsa_cipher.RSAInputError("Generated private key not found. Generate a new key pair.")
        return {"private_key": rsa_cipher.export_private_key(private_key, request.password)}
    except ValueError as error:
        raise _bad_request(error) from error


@app.get("/api/rsa/demo")
def rsa_demo_values() -> dict[str, int | bool]:
    return rsa_demo.calculations()
