"""Streamlit interface for the Cryptography Learning Toolkit."""

import streamlit as st

from src import aes_cipher, caesar_cipher, rsa_cipher, rsa_demo

st.set_page_config(page_title="Cryptography Learning Toolkit", page_icon="🔐", layout="centered")

TASK1_PAGES = ("Caesar Cipher", "AES-128-GCM")
TASK2_PAGES = (
    "RSA Key Generation",
    "RSA Encryption",
    "RSA Decryption",
    "RSA Numerical Example",
    "Algorithm Explanation",
    "Algorithm Comparison",
)


def _reset(prefix: str) -> None:
    for key in list(st.session_state.keys()):
        if key.startswith(prefix):
            del st.session_state[key]
    st.rerun()


def _show_error(error: Exception) -> None:
    st.error(str(error))


def _navigate(page: str) -> None:
    st.session_state["current_page"] = page
    if page in TASK1_PAGES:
        st.session_state["task1_navigation"] = page
        st.session_state["task2_navigation"] = None
    elif page in TASK2_PAGES:
        st.session_state["task1_navigation"] = None
        st.session_state["task2_navigation"] = page
    else:
        st.session_state["task1_navigation"] = None
        st.session_state["task2_navigation"] = None


def _select_task1_page() -> None:
    page = st.session_state.get("task1_navigation")
    if page:
        _navigate(page)


def _select_task2_page() -> None:
    page = st.session_state.get("task2_navigation")
    if page:
        _navigate(page)


def _load_caesar_example() -> None:
    st.session_state["caesar_plaintext"] = "HELLO"
    st.session_state["caesar_shift"] = 3
    st.session_state["caesar_ciphertext_input"] = ""
    for key in ("caesar_original", "caesar_encrypted", "caesar_decrypted"):
        st.session_state.pop(key, None)


def _clear_caesar() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("caesar_"):
            del st.session_state[key]
    st.session_state["caesar_plaintext"] = ""
    st.session_state["caesar_shift"] = 3
    st.session_state["caesar_ciphertext_input"] = ""


def _home() -> None:
    st.title("🔐 Cryptography Learning Toolkit")
    st.write("Assignment workspace for classical, symmetric, and public-key cryptography.")
    st.info(
        "Use Caesar only to learn about substitution ciphers. AES and RSA here are educational tools; for real applications, "
        "use a reviewed protocol and secure key-management process."
    )
    task1, task2 = st.columns(2)
    with task1:
        st.subheader("Task 1 — Classical and Symmetric Encryption")
        st.write("Explore a classical substitution cipher and modern authenticated encryption.")
        st.button("Open Caesar Cipher", key="home_caesar", on_click=_navigate, args=("Caesar Cipher",), use_container_width=True)
        st.button("Open AES-128-GCM", key="home_aes", on_click=_navigate, args=("AES-128-GCM",), use_container_width=True)
    with task2:
        st.subheader("Task 2 — Public-Key Cryptography")
        st.write("The existing RSA key tools and numerical classroom demonstration remain available.")
        st.button("Open RSA Key Generation", key="home_rsa", on_click=_navigate, args=("RSA Key Generation",), use_container_width=True)
        st.button("Open RSA Numerical Example", key="home_rsa_demo", on_click=_navigate, args=("RSA Numerical Example",), use_container_width=True)
    st.caption("Use the sidebar to open the algorithm comparison and move between all assignment pages.")


def _caesar() -> None:
    st.session_state.setdefault("caesar_plaintext", "HELLO")
    st.session_state.setdefault("caesar_shift", 3)
    st.session_state.setdefault("caesar_ciphertext_input", "")
    st.title("Caesar Cipher")
    st.write("A classical substitution cipher that shifts each English letter by a fixed number of places.")
    with st.expander("How it works"):
        st.write("Letters are mapped to values 0–25 (A–Z). The key is added to encrypt and subtracted to decrypt.")
        st.latex(r"E(x) = (x + k) \bmod 26")
        st.latex(r"D(x) = (x - k) \bmod 26")
        st.caption("Uppercase and lowercase are preserved. Spaces, punctuation, numbers, emoji, and non-English letters pass through unchanged.")
    st.info("Default demonstration: plaintext HELLO, shift 3, ciphertext KHOOR, decrypted text HELLO.")
    st.button("Load demonstration", key="caesar_load_example", on_click=_load_caesar_example)
    text = st.text_area("Plaintext", height=120, placeholder="Enter plaintext…", key="caesar_plaintext")
    shift = st.number_input("Shift", min_value=0, max_value=25, step=1, key="caesar_shift")
    ciphertext_input = st.text_area(
        "Ciphertext to decrypt (optional)",
        height=100,
        placeholder="Paste a Caesar ciphertext here, or encrypt plaintext above first.",
        key="caesar_ciphertext_input",
    )
    encrypt_col, decrypt_col, clear_col = st.columns(3)
    if encrypt_col.button("Encrypt", type="primary", key="caesar_encrypt"):
        if not text:
            st.error("Enter plaintext before encrypting.")
        else:
            try:
                encrypted = caesar_cipher.encrypt(text, shift)
                st.session_state["caesar_original"] = text
                st.session_state["caesar_encrypted"] = encrypted
                st.session_state["caesar_decrypted"] = caesar_cipher.decrypt(encrypted, shift)
            except ValueError as error:
                _show_error(error)
    if decrypt_col.button("Decrypt", key="caesar_decrypt"):
        ciphertext = ciphertext_input if ciphertext_input else st.session_state.get("caesar_encrypted", "")
        if not ciphertext:
            st.error("Enter ciphertext to decrypt, or encrypt plaintext first.")
        else:
            try:
                decrypted = caesar_cipher.decrypt(ciphertext, shift)
                st.session_state["caesar_original"] = decrypted
                st.session_state["caesar_encrypted"] = ciphertext
                st.session_state["caesar_decrypted"] = decrypted
            except ValueError as error:
                _show_error(error)
    clear_col.button("Clear / Reset", on_click=_clear_caesar, key="caesar_reset")

    if "caesar_encrypted" in st.session_state:
        st.subheader("Results")
        st.markdown("**Original text**")
        st.code(st.session_state.get("caesar_original", ""), language=None)
        st.markdown("**Encrypted text**")
        st.code(st.session_state["caesar_encrypted"], language=None)
        st.markdown("**Decrypted result**")
        st.code(st.session_state.get("caesar_decrypted", ""), language=None)


def _aes() -> None:
    st.title("AES-128-GCM")
    st.write("Authenticated symmetric encryption for UTF-8 text, using a passphrase-derived 128-bit key.")
    st.caption("Each encryption creates a fresh salt and nonce. Copy the complete CLT1: payload into the Decrypt tab to recover the text.")
    encrypt_tab, decrypt_tab = st.tabs(["Encrypt", "Decrypt"])
    with encrypt_tab:
        plaintext = st.text_area("Plaintext", height=130, placeholder="Enter text to encrypt…", key="aes_plaintext")
        encrypt_passphrase = st.text_input("Passphrase", type="password", key="aes_encrypt_passphrase")
        if st.button("Encrypt with AES-128-GCM", type="primary", key="aes_encrypt"):
            if not plaintext:
                st.error("Enter plaintext before encrypting.")
            elif not encrypt_passphrase:
                st.error("Enter a non-empty passphrase.")
            else:
                try:
                    st.session_state["aes_ciphertext_result"] = aes_cipher.encrypt(plaintext, encrypt_passphrase)
                except ValueError as error:
                    _show_error(error)
        if "aes_ciphertext_result" in st.session_state:
            st.markdown("**Encrypted payload (copyable)**")
            st.code(st.session_state["aes_ciphertext_result"], language=None)
    with decrypt_tab:
        payload = st.text_area("Ciphertext payload", height=150, placeholder="Paste the complete CLT1: payload…", key="aes_payload")
        decrypt_passphrase = st.text_input("Passphrase", type="password", key="aes_decrypt_passphrase")
        if st.button("Decrypt and authenticate", type="primary", key="aes_decrypt"):
            if not payload:
                st.error("Paste the ciphertext payload before decrypting.")
            elif not decrypt_passphrase:
                st.error("Enter the passphrase used for encryption.")
            else:
                try:
                    st.session_state["aes_plaintext_result"] = aes_cipher.decrypt(payload, decrypt_passphrase)
                except ValueError as error:
                    _show_error(error)
        if "aes_plaintext_result" in st.session_state:
            st.markdown("**Decrypted text**")
            st.code(st.session_state["aes_plaintext_result"], language=None)
    st.button("Clear / Reset", on_click=_reset, args=("aes_",), key="aes_reset")


def _ensure_rsa_state() -> None:
    st.session_state.setdefault("rsa_public_pem", "")
    st.session_state.setdefault("rsa_active_private_pem", "")
    st.session_state.setdefault("rsa_active_private_bits", 0)
    st.session_state.setdefault("rsa_private_import_pem", "")
    st.session_state.setdefault("rsa_public_key_input", st.session_state["rsa_public_pem"])
    st.session_state.setdefault("rsa_decrypt_input", "")


def _clear_rsa_encryption() -> None:
    for key in ("rsa_message", "rsa_ciphertext"):
        st.session_state.pop(key, None)


def _clear_rsa_decryption() -> None:
    for key in ("rsa_decrypt_input", "rsa_plaintext"):
        st.session_state.pop(key, None)


def _rsa_key_generation() -> None:
    _ensure_rsa_state()
    st.title("RSA Key Generation")
    st.write("Generate a public/private key pair with PyCryptodome's secure random generator.")
    bits = st.selectbox(
        "RSA key size",
        rsa_cipher.SUPPORTED_GENERATION_SIZES,
        format_func=lambda size: f"{size} bits",
        key="rsa_key_size",
    )
    if st.button("Generate key pair", type="primary", key="rsa_generate"):
        try:
            private_key, public_key = rsa_cipher.generate_key_pair(bits)
            public_pem = rsa_cipher.export_public_key(public_key)
            st.session_state["rsa_public_pem"] = public_pem
            st.session_state["rsa_public_key_input"] = public_pem
            st.session_state["rsa_active_private_pem"] = private_key.export_key(format="PEM").decode("ascii")
            st.session_state["rsa_active_private_bits"] = private_key.size_in_bits()
            st.session_state["rsa_active_private_source"] = "Generated"
            st.session_state.pop("rsa_ciphertext", None)
            st.session_state.pop("rsa_plaintext", None)
            st.success(f"Generated a {bits}-bit RSA key pair. The private key is available in this session.")
        except ValueError as error:
            _show_error(error)

    if st.session_state["rsa_public_pem"]:
        st.subheader("Public key")
        st.code(st.session_state["rsa_public_pem"], language=None)
        st.download_button(
            "Download public key (PEM)",
            data=st.session_state["rsa_public_pem"],
            file_name="cryptography-learning-toolkit-public-key.pem",
            mime="application/x-pem-file",
            key="rsa_public_download",
        )
    else:
        st.info("Generate a key pair to display and export its public key.")

    if st.session_state["rsa_active_private_pem"]:
        st.info(
            f"A {st.session_state['rsa_active_private_bits']}-bit private key is loaded in this Streamlit session. "
            "It is not displayed or written to project files."
        )
        st.warning("Keep private keys secret. A downloaded private-key file is protected with the password you choose below.")
        confirmed = st.checkbox("I understand and want to export the private key", key="rsa_export_confirm")
        export_password = st.text_input("Password to protect the exported key", type="password", key="rsa_export_password")
        if confirmed and export_password:
            try:
                active_key = rsa_cipher.import_private_key(st.session_state["rsa_active_private_pem"])
                protected_pem = rsa_cipher.export_private_key(active_key, export_password)
                st.download_button(
                    "Download password-protected private key",
                    data=protected_pem,
                    file_name="cryptography-learning-toolkit-private-key.pem",
                    mime="application/x-pem-file",
                    key="rsa_export_download",
                )
            except ValueError as error:
                _show_error(error)
        elif confirmed:
            st.caption("Enter a password to enable protected private-key export.")
    st.button("Reset RSA session", on_click=_reset, args=("rsa_",), key="rsa_reset")


def _rsa_encryption() -> None:
    _ensure_rsa_state()
    st.title("RSA Encryption")
    st.write("Encrypt a short message with the recipient's public key using RSA-OAEP and SHA-256.")
    public_pem = st.text_area(
        "Public key (PEM)",
        height=150,
        key="rsa_public_key_input",
        placeholder="Generate a key pair or paste a public key in PEM format.",
    )
    public_key = None
    if public_pem:
        try:
            public_key = rsa_cipher.import_public_key(public_pem)
            limit = rsa_cipher.max_message_bytes(public_key)
            st.caption(f"Valid {public_key.size_in_bits()}-bit public key. OAEP/SHA-256 limit: {limit} UTF-8 bytes.")
        except ValueError:
            st.caption("The public key has not been validated yet. Use the button below to check it.")
    if st.button("Validate public key", key="rsa_validate_public"):
        try:
            public_key = rsa_cipher.import_public_key(public_pem)
            st.session_state["rsa_public_pem"] = rsa_cipher.export_public_key(public_key)
            st.success(f"Valid RSA public key ({public_key.size_in_bits()} bits).")
        except ValueError as error:
            _show_error(error)

    st.info("RSA-OAEP cannot encrypt large messages. This app shows the exact UTF-8 byte limit and never truncates the input.")
    message = st.text_area("Plaintext message", height=120, key="rsa_message", placeholder="Enter a short message…")
    if st.button("Encrypt with public key", type="primary", key="rsa_encrypt"):
        st.session_state.pop("rsa_ciphertext", None)
        if not message:
            st.error("Enter a message before encrypting.")
        else:
            try:
                public_key = rsa_cipher.import_public_key(public_pem)
                st.session_state["rsa_ciphertext"] = rsa_cipher.encrypt(message, public_key)
                st.session_state["rsa_public_pem"] = rsa_cipher.export_public_key(public_key)
            except ValueError as error:
                _show_error(error)
    if "rsa_ciphertext" in st.session_state:
        st.markdown("**Ciphertext (Base64, copyable)**")
        st.code(st.session_state["rsa_ciphertext"], language=None)
    st.button("Clear encryption fields", on_click=_clear_rsa_encryption, key="rsa_clear_encrypt")


def _rsa_decryption() -> None:
    _ensure_rsa_state()
    st.title("RSA Decryption")
    st.write("Recover a message with the matching private key. Decryption uses the same OAEP/SHA-256 parameters as encryption.")
    if st.session_state["rsa_active_private_pem"]:
        st.success(
            f"Private key loaded: {st.session_state['rsa_active_private_bits']} bits "
            f"({st.session_state.get('rsa_active_private_source', 'Imported')})."
        )
    else:
        st.info("Generate a key pair on the RSA Key Generation page, or import the matching private key below.")

    with st.expander("Import a private key"):
        private_pem = st.text_area("Private key (PEM)", height=150, key="rsa_private_import_pem")
        private_passphrase = st.text_input("Private-key password (if protected)", type="password", key="rsa_private_import_password")
        if st.button("Validate and use private key", key="rsa_validate_private"):
            try:
                private_key = rsa_cipher.import_private_key(private_pem, private_passphrase or None)
                st.session_state["rsa_active_private_pem"] = private_key.export_key(format="PEM").decode("ascii")
                st.session_state["rsa_active_private_bits"] = private_key.size_in_bits()
                st.session_state["rsa_active_private_source"] = "Imported"
                matching_public_pem = rsa_cipher.export_public_key(private_key)
                st.session_state["rsa_public_pem"] = matching_public_pem
                st.session_state["rsa_public_key_input"] = matching_public_pem
                st.session_state.pop("rsa_plaintext", None)
                st.success(f"Valid {private_key.size_in_bits()}-bit private key loaded for this session.")
            except ValueError as error:
                _show_error(error)

    ciphertext = st.text_area(
        "Ciphertext (standard Base64)",
        height=130,
        key="rsa_decrypt_input",
        placeholder="Paste the complete ciphertext produced by RSA Encryption.",
    )
    if st.button("Decrypt with private key", type="primary", key="rsa_decrypt"):
        st.session_state.pop("rsa_plaintext", None)
        if not ciphertext.strip():
            st.error("Paste the Base64 ciphertext before decrypting.")
        elif not st.session_state["rsa_active_private_pem"]:
            st.error("Generate or import a private key before decrypting.")
        else:
            try:
                private_key = rsa_cipher.import_private_key(st.session_state["rsa_active_private_pem"])
                st.session_state["rsa_plaintext"] = rsa_cipher.decrypt(ciphertext, private_key)
            except ValueError as error:
                _show_error(error)
    if "rsa_plaintext" in st.session_state:
        st.markdown("**Recovered plaintext**")
        st.code(st.session_state["rsa_plaintext"], language=None)
    st.button("Clear decryption fields", on_click=_clear_rsa_decryption, key="rsa_clear_decrypt")


def _rsa_numerical_example() -> None:
    st.title("RSA Numerical Example")
    st.warning("Educational only: these tiny numbers are insecure and must never be used for real encryption.")
    values = rsa_demo.calculations()
    st.subheader("1. Choose the small primes")
    st.markdown("`p = 3`, `q = 11`. These are deliberately tiny for hand calculation.")
    st.subheader("2. Calculate n and φ(n)")
    st.latex(r"n = p \times q = 3 \times 11 = 33")
    st.latex(r"\varphi(n) = (p - 1)(q - 1) = 2 \times 10 = 20")
    st.subheader("3. Check the public exponent and private exponent")
    st.latex(r"\gcd(e, \varphi(n)) = \gcd(3, 20) = 1")
    st.write("Because the greatest common divisor is 1, `e = 3` is relatively prime to `φ(n) = 20`.")
    st.latex(r"(e \times d) \bmod \varphi(n) = (3 \times 7) \bmod 20 = 21 \bmod 20 = 1")
    st.write("Therefore `d = 7` is the modular inverse of `e = 3` modulo 20.")
    st.subheader("4. Encrypt the message number M = 4")
    st.latex(r"C = M^e \bmod n = 4^3 \bmod 33 = 64 \bmod 33 = 31")
    st.subheader("5. Decrypt C = 31")
    st.latex(r"M = C^d \bmod n = 31^7 \bmod 33")
    st.write("Since `31 ≡ -2 (mod 33)`, `31⁷ ≡ (-2)⁷ = -128 ≡ 4 (mod 33)`. The recovered number is the original `M = 4`.")
    st.success(
        f"Verified: gcd(e, φ(n)) = {values['gcd_e_phi']}; (e × d) mod φ(n) = {values['ed_mod_phi']}; "
        f"ciphertext C = {values['ciphertext']}; decrypted M = {values['decrypted']}."
    )


def _rsa_explanation() -> None:
    st.title("Algorithm Explanation")
    st.write("RSA is a public-key cryptosystem: the public key can be shared, while the private key must remain secret.")
    st.subheader("Key generation")
    st.markdown(
        "1. A trusted cryptographic library securely generates two large prime numbers.\n"
        "2. It computes the modulus `n` and the public and private exponents.\n"
        "3. The public key contains `(n, e)`; the private key contains secret values needed for decryption."
    )
    st.subheader("Encryption and decryption")
    st.markdown(
        "- **Encrypt:** the sender uses the recipient's public key and RSA-OAEP with SHA-256.\n"
        "- **Decrypt:** only the matching private key can recover the message using the same OAEP parameters.\n"
        "- OAEP randomizes encryption and adds padding, so the same message does not produce a fixed ciphertext."
    )
    st.subheader("Why the message must be short")
    st.latex(r"\text{maximum message bytes} = k - 2h_{Len} - 2")
    st.write("Here `k` is the RSA modulus length in bytes and `hLen = 32` for SHA-256. This gives 190 bytes for a 2048-bit key and 318 bytes for a 3072-bit key.")
    st.info("RSA is for short messages or key transport, not large files. Real systems commonly use hybrid encryption: a symmetric cipher protects the data and RSA protects a short symmetric key.")
    st.subheader("Keep private keys safe")
    st.write("Do not share a private key. This app keeps the active key in the current Streamlit session, does not display it, and only offers downloads as password-protected PKCS#8 PEM after explicit confirmation.")
    st.warning("The numerical example uses tiny values only to demonstrate arithmetic. It is completely separate from the real RSA-OAEP implementation.")


def _comparison() -> None:
    st.title("Algorithm Comparison")
    st.write("Compare the two Assignment Task 1 algorithms, then review the existing Task 2 algorithms.")
    st.subheader("Task 1 — Caesar Cipher and AES-128-GCM")
    st.table(
        [
            {"Property": "Category", "Caesar Cipher": "Classical substitution cipher", "AES-128-GCM": "Modern symmetric authenticated encryption"},
            {"Property": "Key", "Caesar Cipher": "Integer shift from 0 to 25", "AES-128-GCM": "128-bit key derived from a passphrase"},
            {"Property": "How it works", "Caesar Cipher": "Shifts English letters; other characters pass through", "AES-128-GCM": "Encrypts bytes and authenticates ciphertext and tag"},
            {"Property": "Key sharing", "Caesar Cipher": "Sender and receiver share the shift", "AES-128-GCM": "Sender and receiver share the passphrase"},
            {"Property": "Security", "Caesar Cipher": "Insecure; useful only for learning", "AES-128-GCM": "Modern authenticated encryption when keys are managed safely"},
            {"Property": "Typical output", "Caesar Cipher": "Readable shifted text", "AES-128-GCM": "Versioned Base64-compatible payload"},
        ]
    )
    st.subheader("Task 2 — Public-Key Cryptography")
    st.table(
        [
            {"Algorithm": "RSA-OAEP / SHA-256", "Purpose": "Encrypt short messages with public-key cryptography", "Security note": "Modern padding; plaintext size is limited"},
            {"Algorithm": "Tiny RSA demo", "Purpose": "Follow modular arithmetic", "Security note": "Insecure by design"},
        ]
    )


st.session_state.setdefault("current_page", "Home")
st.session_state.setdefault("task1_navigation", None)
st.session_state.setdefault("task2_navigation", None)

with st.sidebar:
    st.title("🔐 CLT")
    st.button("Home", key="go_home", on_click=_navigate, args=("Home",), use_container_width=True)
    st.markdown("### Task 1 — Classical and Symmetric Encryption")
    st.radio(
        "Task 1 pages",
        TASK1_PAGES,
        index=None,
        key="task1_navigation",
        on_change=_select_task1_page,
        label_visibility="collapsed",
    )
    st.markdown("### Task 2 — Public-Key Cryptography")
    st.radio(
        "Task 2 pages",
        TASK2_PAGES,
        index=None,
        key="task2_navigation",
        on_change=_select_task2_page,
        label_visibility="collapsed",
    )
    st.caption("Cryptography Learning Toolkit")

{
    "Home": _home,
    "Caesar Cipher": _caesar,
    "AES-128-GCM": _aes,
    "RSA Key Generation": _rsa_key_generation,
    "RSA Encryption": _rsa_encryption,
    "RSA Decryption": _rsa_decryption,
    "RSA Numerical Example": _rsa_numerical_example,
    "Algorithm Explanation": _rsa_explanation,
    "Algorithm Comparison": _comparison,
}[st.session_state["current_page"]]()
