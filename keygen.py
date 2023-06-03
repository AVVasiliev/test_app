import rsa
from pathlib import Path


if __name__ == '__main__':
    public_key, private_key = rsa.newkeys(2048)

    with open('private.pem', 'wb') as private:
        private.write(private_key.save_pkcs1())

    with open('public.pem', 'wb') as private:
        private.write(public_key.save_pkcs1())

    print('Created public.pem and private.pem')

    prv = rsa.PrivateKey.load_pkcs1(Path('private.pem').read_bytes())
    pub = rsa.PublicKey.load_pkcs1(Path('public.pem').read_bytes())

    message: bytes = 'some text русский текст'.encode('utf-8')
    print('Original: ' + message.decode('utf-8'))
    crypt_text: bytes = rsa.encrypt(message, pub)
    Path('result.data').write_bytes(crypt_text)

    crypt_from_file = Path('result.data').read_bytes()
    message_encrypt: bytes = rsa.decrypt(crypt_from_file, prv)
    print(message_encrypt.decode('utf-8'))

