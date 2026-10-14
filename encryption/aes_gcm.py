import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class AesGcmEncryption:
    def __init__(self, key):
        if len(key) != 32:
            raise ValueError("AES-256 requires a 32-byte key")
        self.aesgcm = AESGCM(key)

    def encrypt(self, plaintext):
        nonce = os.urandom(12)
        data = plaintext.encode("utf-8") if isinstance(plaintext, str) else bytes(plaintext)
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        return nonce, ciphertext

    def decrypt(self, nonce, ciphertext):
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        try:
            return plaintext.decode("utf-8")
        except UnicodeDecodeError:
            return plaintext
