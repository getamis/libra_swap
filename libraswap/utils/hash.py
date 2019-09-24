import sha3


def create_hasher():
    return sha3.keccak_256()


def create_hasher_prefix(salt):
    m = create_hasher()
    m.update(salt)
    m.update(b'@@$$LIBRA$$@@')
    return m.digest()
