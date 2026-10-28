from src.rsa_demo import calculations


def test_rsa_numerical_example_has_requested_values_and_verifies():
    result = calculations()
    assert (result["p"], result["q"], result["n"], result["phi_n"]) == (3, 11, 33, 20)
    assert (result["e"], result["d"], result["message"]) == (3, 7, 4)
    assert result["ciphertext"] == 31
    assert result["decrypted"] == 4
    assert result["verified"] is True
