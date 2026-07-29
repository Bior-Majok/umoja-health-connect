"""AES-256-GCM field-level encryption for personal health information at rest (NFR01/NFR14).

Applied to free-text medical fields (symptoms, response notes, alert conditions, record
details) via EncryptedText, a SQLAlchemy column type that encrypts on write and decrypts
on read transparently. Fields used in queries (patient_id, phone_number, etc.) are left
alone, since AES-GCM's random nonce makes ciphertext non-deterministic and therefore
unsuitable for equality lookups.
"""

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import current_app
from sqlalchemy.types import TypeDecorator, Text

_DEV_ONLY_KEY_MATERIAL = 'umoja-dev-only-encryption-key-not-for-production'


def _key():
    raw = current_app.config.get('ENCRYPTION_KEY') or _DEV_ONLY_KEY_MATERIAL
    return hashlib.sha256(raw.encode('utf-8')).digest()


def encrypt_text(plaintext):
    if plaintext is None:
        return None
    nonce = os.urandom(12)
    ciphertext = AESGCM(_key()).encrypt(nonce, plaintext.encode('utf-8'), None)
    return base64.b64encode(nonce + ciphertext).decode('ascii')


def decrypt_text(token):
    if token is None:
        return None
    raw = base64.b64decode(token)
    nonce, ciphertext = raw[:12], raw[12:]
    return AESGCM(_key()).decrypt(nonce, ciphertext, None).decode('utf-8')


class EncryptedText(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return encrypt_text(value)

    def process_result_value(self, value, dialect):
        return decrypt_text(value)
