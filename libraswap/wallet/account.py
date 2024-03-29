from nacl.signing import SigningKey

from libraswap.utils.hash import create_hasher


class Account:
    def __init__(self, private_key):
        self._signing_key = SigningKey(bytes.fromhex(private_key))
        self._verify_key = self._signing_key.verify_key
        m = create_hasher()
        m.update(self._verify_key.encode())
        self.address = m.digest().hex()

    def sign(self, message):
        return self._signing_key.sign(message)

    @property
    def public_key(self):
        return self._verify_key.encode().hex()

    @property
    def private_key(self):
        return self._signing_key.encode().hex()
