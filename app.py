"""Streamlit interface for the Cryptography Learning Toolkit."""

import streamlit as st

from src import aes_cipher, caesar_cipher, rsa_cipher, rsa_demo

st.set_page_config(page_title="Cryptography Learning Toolkit", page_icon="🔐", layout="centered")

PAGES = [
    "Home",
    "Caesar Cipher",
    "AES-128",
    "RSA",
    "RSA Numerical Demo",
    "Algorithm Comparison",
]


def _reset(prefix: str) -> None:
    for key in list(st.session_state.keys()):
        if key.startswith(prefix):
            del st.session_state[key]
    st.rerun()


def _show_error(error: Exception) -> None:
    st.error(str(error))


def _home() -> None:
    st.title("🔐 Cryptography Learning Toolkit")
    st.write(
        "A hands-on introduction to classical and modern encryption. Choose an item in the sidebar to try an algorithm."
    )
    st.info(
        "Use Caesar only to learn about substitution ciphers. AES and RSA here are educational tools; for real applications, "
        "use a reviewed protocol and secure key-management process."
    )
    st.subheader("Explore")
    st.markdown(
        "- **Caesar Cipher** — shift letters while keeping punctuation and letter case.\n"
        "- **AES-128** — protect text with a passphrase using authenticated AES-GCM.\n"
        "- **RSA** — create or import keys and use OAEP with SHA-256 for short messages.\n"
        "- **RSA Numerical Demo** — walk through a tiny, intentionally insecure classroom example.\n"
        "- **Algorithm Comparison** — compare the intended use and properties of each method."
    )


def _caesar() -> None:
    st.title("Caesar Cipher")
    st.write("Each English letter moves forward by the selected number of places. Other characters stay unchanged.")
    operation = st.radio("Operation", ["Encrypt", "Decrypt"], horizontal=True, key="caesar_operation")
    text = st.text_area("Text", height=140, placeholder="Type or paste text…", key="caesar_text")
    shift = st.number_input("Shift", min_value=0, max_value=25, step=1, value=3, key="caesar_shift")
    if st.button(f"{operation} text", type="primary", key="caesar_run"):
        if not text:
            st.error("Enter some text first.")
        else:
            try:
                result = caesar_cipher.encrypt(text, shift) if operation == "Encrypt" else caesar_cipher.decrypt(text, shift)
                st.session_state["caesar_result"] = result
            except ValueError as error:
                _show_error(error)
    if "caesar_result" in st.session_state:
        st.markdown("**Result (copyable)**")
        st.code(st.session_state["caesar_result"], language=None)
    st.button("Reset", on_click=_reset, args=("caesar_",), key="caesar_reset")


def _aes() -> None:
    st.title("AES-128")
    st.write("AES-GCM encrypts UTF-8 text and detects changes to the encrypted payload.")
    operation = st.radio("Operation", ["Encrypt", "Decrypt"], horizontal=True, key="aes_operation")
    input_label = "Plaintext" if operation == "Encrypt" else "Ciphertext payload"
    value = st.text_area(input_label, height=150, placeholder="Type or paste text…", key="aes_input")
    passphrase = st.text_input("Passphrase", type="password", key="aes_passphrase")
    if operation == "Encrypt":
        st.caption("Each encryption uses a fresh random salt and nonce. Keep the passphrase safe; it cannot be recovered.")
    else:
        st.caption("Paste the complete CLT1: payload produced by this toolkit.")
    if st.button(f"{operation}", type="primary", key="aes_run"):
        if not value:
            st.error(f"Enter {input_label.lower()} first.")
        elif not passphrase:
            st.error("Enter a non-empty passphrase.")
        else:
            try:
                result = aes_cipher.encrypt(value, passphrase) if operation == "Encrypt" else aes_cipher.decrypt(value, passphrase)
                st.session_state["aes_result"] = result
            except ValueError as error:
                _show_error(error)
    if "aes_result" in st.session_state:
        st.markdown("**Result (copyable)**")
        st.code(st.session_state["aes_result"], language=None)
    st.button("Reset", on_click=_reset, args=("aes_",), key="aes_reset")


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
    st.write("These methods solve different problems; their ciphertexts and keys are not interchangeable.")
    st.table(
        [
            {"Algorithm": "Caesar", "Type": "Classical substitution", "Key": "Shift 0–25", "Good for": "Learning letter shifts", "Security": "None; trivial to break"},
            {"Algorithm": "AES-128-GCM", "Type": "Symmetric authenticated encryption", "Key": "Passphrase-derived 128-bit key", "Good for": "Text when both sides share a passphrase", "Security": "Modern authenticated encryption"},
            {"Algorithm": "RSA-OAEP / SHA-256", "Type": "Public-key encryption", "Key": "Public key to encrypt; private key to decrypt", "Good for": "Short messages or key transport", "Security": "Modern padding; plaintext size is limited"},
            {"Algorithm": "Tiny RSA demo", "Type": "Modular arithmetic", "Key": "p=3, q=11", "Good for": "Following the arithmetic", "Security": "Insecure by design"},
        ]
    )


with st.sidebar:
    st.title("🔐 CLT")
    page = st.radio("Navigate", PAGES, key="navigation")
    st.caption("Cryptography Learning Toolkit")

{
    "Home": _home,
    "Caesar Cipher": _caesar,
    "AES-128": _aes,
    "RSA": _rsa,
    "RSA Numerical Demo": _rsa_demo,
    "Algorithm Comparison": _comparison,
}[page]()
