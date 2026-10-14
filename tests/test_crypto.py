import oqs


def test_ml_kem_768_shared_secret_matches():
    """Test ML-KEM-768 key encapsulation and shared-secret agreement."""

    # Bob generates his own key pair.
    with oqs.KeyEncapsulation("ML-KEM-768") as bob:
        bob_public_key = bob.generate_keypair()

        # Alice encapsulates a shared secret using Bob's public key.
        with oqs.KeyEncapsulation("ML-KEM-768") as alice:
            ciphertext, alice_secret = alice.encap_secret(bob_public_key)

        # Bob decapsulates using the secret key stored in his own object.
        bob_secret = bob.decap_secret(ciphertext)

    assert len(bob_public_key) == 1184
    assert len(ciphertext) == 1088
    assert len(alice_secret) == 32
    assert alice_secret == bob_secret


def test_ml_dsa_65_valid_signature():
    """Test that ML-DSA-65 verifies a valid signature."""

    message = b"Quantum-safe secure channel test."

    with oqs.Signature("ML-DSA-65") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(message)

    with oqs.Signature("ML-DSA-65") as verifier:
        result = verifier.verify(message, signature, public_key)

    assert result is True


def test_ml_dsa_65_rejects_modified_message():
    """Test that ML-DSA-65 rejects a modified message."""

    message = b"Original message."
    modified_message = b"Modified message."

    with oqs.Signature("ML-DSA-65") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(message)

    with oqs.Signature("ML-DSA-65") as verifier:
        result = verifier.verify(modified_message, signature, public_key)

    assert result is False


def test_falcon_512_valid_signature():
    """Test that Falcon-512 verifies a valid signature."""

    message = b"Falcon post-quantum signature test."

    with oqs.Signature("Falcon-512") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(message)

    with oqs.Signature("Falcon-512") as verifier:
        result = verifier.verify(message, signature, public_key)

    assert result is True


def test_falcon_512_rejects_modified_message():
    """Test that Falcon-512 rejects a modified message."""

    message = b"Original Falcon message."
    modified_message = b"Modified Falcon message."

    with oqs.Signature("Falcon-512") as signer:
        public_key = signer.generate_keypair()
        signature = signer.sign(message)

    with oqs.Signature("Falcon-512") as verifier:
        result = verifier.verify(modified_message, signature, public_key)

    assert result is False