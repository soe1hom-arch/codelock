import json
import os
from pathlib import Path

APP_DIR = Path.home() / ".codelock"
KEY_FILE = APP_DIR / "key"
KEY_ID_FILE = APP_DIR / "key_id"
CONFIG_FILE = APP_DIR / "config.json"


def get_or_create_key() -> bytes:
    if "CODELOCK_KEY" in os.environ:
        raw = os.environ["CODELOCK_KEY"]
        return raw.encode("utf-8")

    if KEY_FILE.exists():
        raw = KEY_FILE.read_bytes()
        return raw

    from .crypto import generate_key
    key = generate_key()
    APP_DIR.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_bytes(key)
    KEY_FILE.chmod(0o600)
    return key


def get_key() -> bytes:
    if "CODELOCK_KEY" in os.environ:
        raw = os.environ["CODELOCK_KEY"]
        return raw.encode("utf-8")

    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    return None


def key_exists() -> bool:
    return "CODELOCK_KEY" in os.environ or KEY_FILE.exists()


def generate_key_id() -> str:
    import hashlib
    key = get_or_create_key()
    return hashlib.sha256(key).hexdigest()[:16]


def init_config() -> dict:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    cfg = {
        "version": 1,
        "key_id": generate_key_id(),
        "created": str(__import__("datetime").datetime.now()),
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    return cfg


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)
