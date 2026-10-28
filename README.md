# Cryptography Learning Toolkit

A beginner-friendly Streamlit project for the college cryptography assignment. **Task 1** demonstrates the Caesar cipher and password-based AES-128-GCM. The existing **Task 2** RSA tools and numerical example remain accessible.

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Run the tests

```powershell
python -m pytest
```

## Features

### Task 1 — Classical and Symmetric Encryption

- **Caesar Cipher:** shifts English letters using `E(x) = (x + k) mod 26` and `D(x) = (x - k) mod 26`, where `k` is 0–25. Letter case is preserved; spaces, punctuation, numbers, emoji, and non-English letters pass through unchanged. The page includes separate Encrypt and Decrypt buttons and the `HELLO`, shift 3 demonstration.
- **AES-128-GCM:** encrypts UTF-8 text with AES-GCM. PBKDF2-HMAC-SHA-256 derives a 128-bit key from the entered passphrase. Each encryption creates a fresh 16-byte salt and 12-byte nonce; GCM produces a 16-byte authentication tag.

#### AES payload format

The copyable payload is `CLT1:` followed by URL-safe Base64-encoded compact JSON. Its fields are:

| Field | Meaning |
| --- | --- |
| `version` | Payload version, currently `1` |
| `kdf` | `PBKDF2-HMAC-SHA-256` |
| `iterations` | PBKDF2 iteration count, currently `600000` |
| `salt` | Standard Base64-encoded random 16-byte salt |
| `nonce` | Standard Base64-encoded random 12-byte GCM nonce |
| `ciphertext` | Standard Base64-encoded encrypted UTF-8 bytes |
| `tag` | Standard Base64-encoded 16-byte GCM authentication tag |

During decryption, the payload's salt and iteration count are used to derive the key again. GCM rejects a wrong passphrase or modified ciphertext/tag.

### Task 2 — Public-Key Cryptography

- **RSA Key Generation:** securely generates 2048-bit or 3072-bit key pairs, displays/copies the public PEM, and downloads it on request. Private-key export requires confirmation and a user-supplied password; the downloaded key is password-protected PKCS#8 PEM.
- **RSA Encryption:** accepts a public PEM key, validates it, shows the RSA-OAEP/SHA-256 UTF-8 byte limit, and encrypts without truncating messages.
- **RSA Decryption:** imports a private PEM key (optionally password-protected) or uses a key generated in the current session. Invalid Base64 and decryption failures are shown as errors.
- **RSA Numerical Example:** walks through `p=3`, `q=11`, `n=33`, `φ(n)=20`, `e=3`, `d=7`, `M=4`, including `gcd(e, φ(n)) = 1`, `(e × d) mod φ(n) = 1`, `C=31`, and recovery of `M=4`. This example is educational only and is never used by the real RSA implementation.
- **Algorithm Explanation:** explains public/private keys, OAEP, RSA's short-message limit, and private-key handling.
- **Algorithm Comparison:** compares Caesar and AES-128-GCM and retains a short reference to the Task 2 algorithms.

## Security notes

Caesar and the tiny numerical RSA example are insecure by design. AES-GCM and RSA-OAEP are implemented with PyCryptodome, but this application is a learning project, not a reviewed production cryptosystem. The toolkit does not store passwords or keys in project files; generated RSA private-key material is held in Streamlit session memory until reset or the session ends. Save exported keys securely and keep the export password separate.
