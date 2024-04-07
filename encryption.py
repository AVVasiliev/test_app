import rsa
from pathlib import Path

PUBLIC_KEY = Path(__file__).parent / 'settings' / 'public.pem'


def encrypt_data(message: bytes) -> bytes:
    pub: rsa.key.PublicKey = rsa.PublicKey.load_pkcs1(PUBLIC_KEY.read_bytes())
    data = b''
    for i in range(0, len(message), 128):
        data += rsa.encrypt(message[i: i+128], pub) + b"\n"

    return data
