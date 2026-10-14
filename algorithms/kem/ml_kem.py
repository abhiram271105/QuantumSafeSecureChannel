import oqs

class MLKEM:
    def __init__(self, algorithm="ML-KEM-768"):
        self.algorithm = algorithm
        self.kem = oqs.KeyEncapsulation(self.algorithm)

    def generate_keypair(self):
        return self.kem.generate_keypair()

    def encapsulate(self, public_key):
        ciphertext, shared_secret = self.kem.encap_secret(public_key)
        return ciphertext, shared_secret

    def decapsulate(self, ciphertext):
        return self.kem.decap_secret(ciphertext)

    def close(self):
        if getattr(self, "kem", None) is not None:
            self.kem.free()
            self.kem = None
