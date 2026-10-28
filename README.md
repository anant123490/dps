# Cryptography Learning Toolkit

An interactive college cryptography project with a React/Vite interface and a Python/FastAPI API. It demonstrates Caesar, password-based AES-128-GCM, RSA-OAEP, and a separate small-number RSA example.

## Project structure

```text
backend/                 FastAPI REST endpoints
frontend/                React + Vite application and responsive CSS
src/                      Reusable Caesar, AES, RSA, and numerical-demo modules
tests/                    Pytest algorithm and API tests
app.py                    Compatibility import for the FastAPI application
requirements.txt          Python dependencies
```

## Run locally

Use Python 3.10+, Node.js 22+, and pnpm 11.25.0. The project pins its pnpm version in `frontend/package.json`.

### Start the API

From the project root, create and activate a virtual environment, install Python requirements, and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend
```

The API listens on `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

### Start the frontend

In a second terminal:

```powershell
npm install --global pnpm@11.25.0
cd frontend
pnpm install
pnpm dev
```

Open `http://127.0.0.1:5173`. To build the production frontend, run `pnpm build` from `frontend/`. The API URL can be changed with `frontend/.env.local` using `VITE_API_BASE_URL=http://127.0.0.1:8000/api`.

## Run tests

From the project root with the virtual environment active:

```powershell
python -m pytest -q
```

## Features

### Task 1 — Classical and Symmetric Encryption

- **Caesar Cipher:** Encrypts and decrypts with a shift from 0 to 25, keeping case and non-letter characters intact. The example uses `HELLO`, shift `3`, and produces `KHOOR`.
- **AES-128-GCM:** Derives a 128-bit key from the passphrase with PBKDF2-HMAC-SHA-256, then encrypts UTF-8 text with authenticated AES-GCM. Every encryption creates a new 16-byte salt and 12-byte nonce. Wrong passphrases and modified payloads fail authentication.
- **AES payload:** `CLT1:` followed by URL-safe Base64 JSON with version, KDF identifier, iteration count, salt, nonce, ciphertext, and GCM tag.

### Task 2 — Public-Key Cryptography

- **RSA key generation:** Generates 2048-bit or 3072-bit RSA key pairs with PyCryptodome. Public PEM is shown and downloadable. Generated private keys remain in backend memory; an encrypted PKCS#8 export is only provided after explicit confirmation and a user-supplied password.
- **RSA encryption/decryption:** Uses RSA-OAEP with SHA-256. Public and private PEM keys can be imported and validated. Ciphertext is standard Base64. The UI reports the plaintext size limit and rejects overlong messages without truncation.
- **RSA numerical demonstration:** Walks through `p=3`, `q=11`, `n=33`, `φ(n)=20`, `e=3`, `d=7`, `M=4`, `C=31`, and recovery of `M=4`. The tiny values are educational only and are never used by RSA-OAEP.
- **Learning and comparison:** Provides short explanations and a side-by-side algorithm comparison.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `POST` | `/api/caesar/encrypt`, `/api/caesar/decrypt` | Caesar operations |
| `POST` | `/api/aes/encrypt`, `/api/aes/decrypt` | AES-GCM operations |
| `POST` | `/api/rsa/keys` | Generate a key pair |
| `POST` | `/api/rsa/validate-public`, `/api/rsa/validate-private` | Validate imported keys |
| `POST` | `/api/rsa/encrypt`, `/api/rsa/decrypt` | RSA-OAEP operations |
| `POST` | `/api/rsa/export-private` | Explicit password-protected export |
| `GET` | `/api/rsa/demo` | Numerical example values |

## Security notes

This is an educational application, not a production cryptosystem. Caesar and the small RSA example are intentionally insecure. The local API binds to loopback and does not persist generated private keys. AES and RSA use PyCryptodome; never reuse a GCM nonce with the same key or share private keys and passphrases. RSA is limited to short messages; production applications typically use hybrid encryption and reviewed key-management practices.
