# Cryptography Learning Toolkit

A beginner-friendly Streamlit project demonstrating a Caesar cipher, password-based AES-128-GCM, RSA-OAEP with SHA-256, and a tiny RSA arithmetic example.

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

- **Caesar Cipher:** shifts English letters from 0 to 25, preserving case and all non-letter characters.
- **AES-128:** UTF-8 text encrypted with AES-GCM. A 128-bit key is derived from the passphrase using PBKDF2-HMAC-SHA-256. The copyable `CLT1:` payload contains the version, KDF parameters, salt, nonce, ciphertext, and authentication tag. A wrong passphrase or changed authenticated data is rejected.
- **RSA:** generates 2048-bit or 3072-bit key pairs, imports public or private PEM keys, encrypts short UTF-8 messages with RSA-OAEP/SHA-256, and exports private keys only as password-protected PKCS#8 PEM after an explicit in-app action.
- **RSA Numerical Demo:** demonstrates the specified `p=3`, `q=11`, `n=33`, `φ(n)=20`, `e=3`, `d=7`, `M=4` calculation. It is educational only.
- **Algorithm Comparison:** summarizes what each method is for and its limitations.

## Security notes

Caesar and the tiny numerical RSA example are insecure by design. AES-GCM and RSA-OAEP are implemented with PyCryptodome, but this application is a learning project, not a reviewed production cryptosystem. The toolkit does not store passwords or keys in project files; generated RSA private-key material is held in Streamlit session memory until reset or the session ends. Save exported keys securely and keep the export password separate.
