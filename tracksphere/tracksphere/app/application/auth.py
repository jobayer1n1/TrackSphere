import hashlib
import hmac
import secrets
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Optional

from tracksphere.app.infrastructure.config import ConfigurationManager

SESSION_COOKIE_NAME = "tracksphere_session"
SESSION_MAX_AGE = 86400
HASH_ITERATIONS = 100_000
SALT_SIZE = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_SIZE)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
    )
    return f"{urlsafe_b64encode(salt).decode()}${urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_b64, digest_b64 = stored_hash.split("$")
        salt = urlsafe_b64decode(salt_b64.encode())
        expected_digest = urlsafe_b64decode(digest_b64.encode())
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            HASH_ITERATIONS,
        )
        return hmac.compare_digest(digest, expected_digest)
    except Exception:
        return False


def _sign(value: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()


def _base64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode(value + padding)


def create_session_token(user_id: int) -> str:
    config = ConfigurationManager()
    timestamp = int(time.time())
    payload = f"{user_id}:{timestamp}"
    signature = _sign(payload, config.secret_key)
    token = f"{payload}:{signature}"
    return urlsafe_b64encode(token.encode("utf-8")).decode("utf-8")


def verify_session_token(token: str) -> Optional[int]:
    config = ConfigurationManager()
    try:
        payload = _base64_decode(token).decode("utf-8")
        user_id_str, timestamp_str, signature = payload.rsplit(":", 2)
        data = f"{user_id_str}:{timestamp_str}"
        expected_signature = _sign(data, config.secret_key)
        if not hmac.compare_digest(signature, expected_signature):
            return None
        timestamp = int(timestamp_str)
        if time.time() - timestamp > SESSION_MAX_AGE:
            return None
        return int(user_id_str)
    except Exception:
        return None
