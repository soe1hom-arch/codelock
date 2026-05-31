import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PREFIX = "CLK_AES_"
KEY_SIZE = 32
IV_SIZE = 12
TAG_SIZE = 16


def generate_key() -> bytes:
    return os.urandom(KEY_SIZE)


def encrypt(key: bytes, plaintext: str) -> str:
    aesgcm = AESGCM(key)
    iv = os.urandom(IV_SIZE)
    data = plaintext.encode("utf-8")
    ciphertext = aesgcm.encrypt(iv, data, None)
    payload = iv + ciphertext
    return PREFIX + base64.urlsafe_b64encode(payload).decode("ascii")


def decrypt(key: bytes, token: str) -> str:
    if not token.startswith(PREFIX):
        raise ValueError("invalid codelock token")
    raw = token[len(PREFIX):]
    payload = base64.urlsafe_b64decode(raw)
    iv = payload[:IV_SIZE]
    ciphertext = payload[IV_SIZE:]
    aesgcm = AESGCM(key)
    data = aesgcm.decrypt(iv, ciphertext, None)
    return data.decode("utf-8")


def is_encrypted(text: str) -> bool:
    return text.startswith(PREFIX)


def scan_text(text: str):
    import re
    pattern = re.escape(PREFIX) + r'[A-Za-z0-9_-]+={0,2}'
    return re.findall(pattern, text)
