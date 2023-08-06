from hashlib import sha3_256
from hmac import new as get_hmac
from secrets import token_bytes

KEY_SIZE = 32


class Anticheat:
    def __init__(self, key_size=KEY_SIZE, digestmode=sha3_256):
        self.key_size = key_size
        self.digestmode = digestmode

    def encipher(self, message: str) -> tuple[str, str]:
        key = token_bytes(self.key_size)
        return (
            get_hmac(key, message.encode(), self.digestmode).hexdigest(),
            key.hex()
        )
