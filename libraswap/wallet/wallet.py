import os

from sha3 import sha3_256

from libraswap.wallet.account import Account


class LibraWallet:
    def __init__(self, entropy=None):
        if entropy is None:
            entropy = os.urandom(32)
        self.entropy = entropy

    def new_account(self, index):
        """ sha3_256(entropy || index) """
        shazer = sha3_256()
        shazer.update(self.entropy)
        shazer.update(index.to_bytes(32, "big"))
        return Account(shazer.digest().hex())
