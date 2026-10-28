"""Streamlit interface for the Cryptography Learning Toolkit."""

import streamlit as st

from src import aes_cipher, caesar_cipher, rsa_cipher, rsa_demo

st.set_page_config(page_title="Cryptography Learning Toolkit", page_icon="🔐", layout="centered")

TASK1_PAGES = ("Caesar Cipher", "AES-128-GCM")
TASK2_PAGES = ("RSA", "RSA Numerical Demo", "Algorithm Comparison")


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
        st.button("Open RSA", key="home_rsa", on_click=_navigate, args=("RSA",), use_container_width=True)
        st.button("Open RSA Numerical Demo", key="home_rsa_demo", on_click=_navigate, args=("RSA Numerical Demo",), use_container_width=True)
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


def _rsa() -> None:
    st.title("RSA-OAEP")
    st.write("Use RSA-OAEP with SHA-256 for short messages. RSA is not designed to encrypt large files directly.")

    if "rsa_public_pem_input" not in st.session_state:
        st.session_state["rsa_public_pem_input"] = ""
    if "rsa_active_private_pem" not in st.session_state:
        st.session_state["rsa_active_private_pem"] = ""
    if "rsa_private_import_pem" not in st.session_state:
        st.session_state["rsa_private_import_pem"] = ""

    col_size, col_button = st.columns([1, 1])
    with col_size:
        bits = st.selectbox("New key size", rsa_cipher.SUPPORTED_GENERATION_SIZES, format_func=lambda size: f"{size} bits", key="rsa_key_size")
    with col_button:
        st.write("")
        if st.button("Generate key pair", type="primary", key="rsa_generate"):
            try:
                private_key, public_key = rsa_cipher.generate_key_pair(bits)
                st.session_state["rsa_public_pem_input"] = rsa_cipher.export_public_key(public_key)
                st.session_state["rsa_active_private_pem"] = private_key.export_key(format="PEM").decode("ascii")
                st.session_state["rsa_private_import_pem"] = ""
                st.success(f"Generated a {bits}-bit key pair in this browser session.")
            except ValueError as error:
                _show_error(error)

    public_pem = st.text_area("Public key (PEM)", height=130, key="rsa_public_pem_input", placeholder="Paste an RSA public key, or generate a key pair above.")
    if st.button("Validate public key", key="rsa_validate_public"):
        try:
            parsed_public = rsa_cipher.import_public_key(public_pem)
            st.success(f"Valid RSA public key ({parsed_public.size_in_bits()} bits).")
        except ValueError as error:
            _show_error(error)
    if public_pem:
        try:
            validated_public = rsa_cipher.import_public_key(public_pem)
        except ValueError:
            st.caption("Validate the PEM text to enable public-key download.")
        else:
            st.download_button(
                "Download public key (PEM)",
                data=rsa_cipher.export_public_key(validated_public),
                file_name="cryptography-learning-toolkit-public-key.pem",
                mime="application/x-pem-file",
                key="rsa_public_download",
            )

    with st.expander("Import a private key for decryption or protected export"):
        private_pem = st.text_area("Private key (PEM)", height=130, key="rsa_private_import_pem")
        private_passphrase = st.text_input("Private key password (if protected)", type="password", key="rsa_private_import_password")
        if st.button("Validate and use private key", key="rsa_validate_private"):
            try:
                private_key = rsa_cipher.import_private_key(private_pem, private_passphrase or None)
                st.session_state["rsa_active_private_pem"] = private_key.export_key(format="PEM").decode("ascii")
                st.success(f"Valid RSA private key ({private_key.size_in_bits()} bits); available in this session.")
            except ValueError as error:
                _show_error(error)

    encrypt_tab, decrypt_tab, export_tab = st.tabs(["Encrypt", "Decrypt", "Export private key"])
    with encrypt_tab:
        message = st.text_area("Message to encrypt", height=110, key="rsa_message")
        try:
            public_key_for_size = rsa_cipher.import_public_key(public_pem) if public_pem else None
            if public_key_for_size:
                st.caption(f"Maximum message size with this key: {rsa_cipher.max_message_bytes(public_key_for_size)} UTF-8 bytes (OAEP/SHA-256).")
        except ValueError:
            public_key_for_size = None
        if st.button("Encrypt with public key", type="primary", key="rsa_encrypt"):
            if not message:
                st.error("Enter a message first.")
            else:
                try:
                    if public_key_for_size is None:
                        raise rsa_cipher.RSAInputError("Enter or import a valid public key first.")
                    st.session_state["rsa_ciphertext"] = rsa_cipher.encrypt(message, public_key_for_size)
                except ValueError as error:
                    _show_error(error)
        if "rsa_ciphertext" in st.session_state:
            st.markdown("**Ciphertext (Base64, copyable)**")
            st.code(st.session_state["rsa_ciphertext"], language=None)

    with decrypt_tab:
        ciphertext = st.text_area("Ciphertext (Base64)", height=120, key="rsa_decrypt_input")
        if st.button("Decrypt with private key", type="primary", key="rsa_decrypt"):
            if not ciphertext:
                st.error("Paste the Base64 ciphertext first.")
            elif not st.session_state["rsa_active_private_pem"]:
                st.error("Generate a key pair or import a private key first.")
            else:
                try:
                    private_key = rsa_cipher.import_private_key(st.session_state["rsa_active_private_pem"])
                    st.session_state["rsa_plaintext"] = rsa_cipher.decrypt(ciphertext, private_key)
                except ValueError as error:
                    _show_error(error)
        if "rsa_plaintext" in st.session_state:
            st.markdown("**Decrypted message**")
            st.code(st.session_state["rsa_plaintext"], language=None)

    with export_tab:
        st.warning("A private key grants full access to messages encrypted for its matching public key. Store the downloaded file securely.")
        confirmed = st.checkbox("I understand and want to export the private key", key="rsa_export_confirm")
        export_password = st.text_input("Password to encrypt the exported key", type="password", key="rsa_export_password")
        if st.session_state["rsa_active_private_pem"] and confirmed and export_password:
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
        elif not st.session_state["rsa_active_private_pem"]:
            st.caption("Generate a key pair or import a private key before exporting.")
        elif confirmed:
            st.caption("Enter a password to protect the exported key file.")

    st.button("Reset RSA session", on_click=_reset, args=("rsa_",), key="rsa_reset")


def _rsa_demo() -> None:
    st.title("RSA Numerical Demo")
    st.error("Educational only. These tiny values are insecure and must never be used to protect real data.")
    values = rsa_demo.calculations()
    st.markdown(
        "For the classroom example, choose the supplied small primes and public exponent:\n\n"
        "1. `p = 3`, `q = 11`\n"
        "2. `n = p × q = 3 × 11 = 33`\n"
        "3. `φ(n) = (p − 1)(q − 1) = 2 × 10 = 20`\n"
        "4. `e = 3` and `d = 7`, because `e × d = 21 ≡ 1 (mod 20)`\n"
        "5. With `M = 4`, encrypt: `C = Mᵉ mod n = 4³ mod 33 = 64 mod 33 = 31`\n"
        "6. Decrypt: `Cᵈ mod n = 31⁷ mod 33 = 4`"
    )
    st.success(f"Verification: C = {values['ciphertext']}; decrypted M = {values['decrypted']}; matches original: {values['verified']}.")


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
    "RSA": _rsa,
    "RSA Numerical Demo": _rsa_demo,
    "Algorithm Comparison": _comparison,
}[st.session_state["current_page"]]()
