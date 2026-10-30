# Cryptography Learning Toolkit

An interactive college project with a React/Vite interface and a Python/FastAPI backend. It demonstrates Caesar, a historical DES cipher, RSA-OAEP, and a separate small-number RSA example.

## Project structure

```text
backend/                 FastAPI REST endpoints
frontend/                React + Vite interface and responsive CSS
src/                     Caesar, DES, RSA, and numerical-demo modules
tests/                   Pytest algorithm and API tests
app.py                   FastAPI application entry point
requirements.txt         Python dependencies
```

## Run locally

Use Python 3.10+, Node.js 22+, and pnpm 11.25.0.

### Start the API

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend
```

The API listens on `http://127.0.0.1:8000`; API documentation is at `http://127.0.0.1:8000/docs`.

### Start the frontend

In another terminal:

```powershell
npm install --global pnpm@11.25.0
cd frontend
pnpm install
pnpm dev
```

Open `http://127.0.0.1:5173`. To build the frontend for production, run `pnpm build` from `frontend/`. Set `VITE_API_BASE_URL` in `frontend/.env.local` to change the API base URL.

## Tests

From the project root with the virtual environment active:

```powershell
python -m pytest -q
```

## Features

### Task 1 — Classical and Symmetric Cryptography

- **Caesar Cipher:** Encrypts and decrypts with shifts from 0 through 25 while preserving letter case and non-letter characters. The `HELLO`, shift `3` example produces `KHOOR`.
- **DES-CBC demonstration:** Encrypts UTF-8 text using PyCryptodome DES-CBC with PKCS#7 padding. PBKDF2-HMAC-SHA-256 derives a DES encryption key and a separate HMAC-SHA-256 authentication key from the passphrase and random 16-byte salt. Each encryption uses a random 8-byte CBC IV. The `DES1:` URL-safe Base64 JSON payload contains version, algorithm settings, KDF settings, salt, IV, ciphertext, and authentication tag. The tag is checked before decryption.

> **Security warning:** DES has a 64-bit block and only 56 effective key bits. It is obsolete and vulnerable to brute-force attacks. This is a classroom demonstration and must not be used to protect real information. The HMAC is included to demonstrate tamper detection; it does not make DES secure.

### Task 2 — Public-Key Cryptography

- **RSA key generation:** Generates 2048-bit or 3072-bit RSA key pairs with PyCryptodome. Generated private keys stay in backend memory. Explicit export is password-protected; public/private PEM import is validated.
- **RSA encryption/decryption:** Uses RSA-OAEP with SHA-256, Base64 ciphertext, and reports the maximum message size.
- **RSA numerical demonstration:** Shows `p=3`, `q=11`, `n=33`, `φ(n)=20`, `e=3`, `d=7`, encrypts `M=4` to `C=31`, and recovers `M=4`. These tiny values are educational only.
- **Learning and comparison:** Includes concept explanations and a side-by-side comparison.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/caesar/encrypt`, `/api/caesar/decrypt` | Caesar operations |
| `POST` | `/api/des/encrypt`, `/api/des/decrypt` | DES-CBC authenticated demonstration |
| `POST` | `/api/rsa/keys` | Generate an RSA key pair |
| `POST` | `/api/rsa/validate-public`, `/api/rsa/validate-private` | Validate imported keys |
| `POST` | `/api/rsa/encrypt`, `/api/rsa/decrypt` | RSA-OAEP operations |
| `POST` | `/api/rsa/export-private` | Explicit password-protected private-key export |
| `GET` | `/api/rsa/demo` | Numerical example values |

This toolkit is for education, not production key management. Caesar and DES are intentionally insecure, as is the tiny RSA math example. The local API binds to loopback and does not persist generated private keys. RSA-OAEP is limited to short messages; production systems commonly use hybrid encryption and reviewed key-management practices.
