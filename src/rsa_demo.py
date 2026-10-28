"""Fixed classroom example illustrating modular RSA arithmetic."""

P = 3
Q = 11
N = P * Q
PHI = (P - 1) * (Q - 1)
E = 3
D = 7
MESSAGE = 4
CIPHERTEXT = pow(MESSAGE, E, N)
DECRYPTED = pow(CIPHERTEXT, D, N)


def calculations() -> dict[str, int | bool]:
    """Return the requested values and the result of the demonstration."""
    return {
        "p": P,
        "q": Q,
        "n": N,
        "phi_n": PHI,
        "e": E,
        "d": D,
        "message": MESSAGE,
        "ciphertext": CIPHERTEXT,
        "decrypted": DECRYPTED,
        "verified": DECRYPTED == MESSAGE,
    }
