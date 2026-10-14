import oqs

class MLDSA:
    def __init__(self, algorithm="ML-DSA-65"):
        self.algorithm = algorithm
        self.signer = oqs.Signature(self.algorithm)

    def generate_keypair(self):
        return self.signer.generate_keypair()

    def sign_message(self, message):
        data = message.encode("utf-8") if isinstance(message, str) else bytes(message)
        return self.signer.sign(data)

    def verify_signature(self, message, signature, public_key):
        data = message.encode("utf-8") if isinstance(message, str) else bytes(message)
        verifier = oqs.Signature(self.algorithm)
        try:
            return bool(verifier.verify(data, signature, public_key))
        finally:
            verifier.free()

    def close(self):
        if getattr(self, "signer", None) is not None:
            self.signer.free()
            self.signer = None
