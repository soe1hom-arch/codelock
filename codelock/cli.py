import os
import sys
import glob as glob_mod

from . import __version__
from .crypto import encrypt, decrypt, is_encrypted, scan_text
from .config import get_or_create_key, key_exists, init_config, load_config


def cmd_init():
    if key_exists():
        print("codelock already initialized in ~/.codelock/")
        return
    init_config()
    print("Initialized codelock.")
    print("  Key:  ~/.codelock/key")
    print("  Config: ~/.codelock/config.json")
    print()
    print("  Set CODELOCK_KEY env var to override the key file.")


def cmd_encrypt(args):
    if not key_exists():
        print("Error: not initialized. Run 'codelock init' first.", file=sys.stderr)
        sys.exit(1)

    key = get_or_create_key()
    plaintext = " ".join(args)
    if not plaintext:
        print("Usage: codelock encrypt <value>", file=sys.stderr)
        sys.exit(1)

    token = encrypt(key, plaintext)
    print(token)


def cmd_decrypt(args):
    if not key_exists():
        print("Error: not initialized. Run 'codelock init' first.", file=sys.stderr)
        sys.exit(1)

    if not args:
        print("Usage: codelock decrypt <token>", file=sys.stderr)
        sys.exit(1)

    key = get_or_create_key()
    token = " ".join(args)

    try:
        value = decrypt(key, token)
        print(value)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_check(args):
    path = args[0] if args else "."
    key = get_or_create_key()

    if not os.path.isfile(path) and not os.path.isdir(path):
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    if os.path.isfile(path):
        files = [path]
    else:
        files = []
        for ext in ["*.py", "*.yaml", "*.yml", "*.json", "*.env", "*.sh", "*.toml", "*.cfg", "*.ini", "*.txt", "*.md"]:
            files.extend(glob_mod.glob(os.path.join(path, "**", ext), recursive=True))

    found = 0
    decrypted = 0
    failed = 0

    for fp in sorted(files):
        try:
            content = open(fp, "r", errors="ignore").read()
        except Exception:
            continue

        tokens = scan_text(content)
        if not tokens:
            continue

        found += len(tokens)
        for tok in tokens:
            try:
                decrypt(key, tok)
                decrypted += 1
            except Exception:
                failed += 1
                print(f"  FAILED: {tok[:40]}... in {fp}")

        if found > 0 and failed > 0:
            pass

    if found == 0:
        print("No codelock tokens found.")
    else:
        print(f"Found {found} token(s): {decrypted} valid, {failed} invalid.")


def cmd_rekey():
    """Generate a new key and update config."""
    if not key_exists():
        print("Error: not initialized.", file=sys.stderr)
        sys.exit(1)

    from .config import APP_DIR, CONFIG_FILE, KEY_FILE
    import json

    if KEY_FILE.exists():
        KEY_FILE.unlink()

    from .crypto import generate_key
    new_key = generate_key()
    APP_DIR.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_bytes(new_key)
    KEY_FILE.chmod(0o600)

    from .config import generate_key_id
    cfg = load_config()
    cfg["key_id"] = generate_key_id()
    cfg["rekeyed"] = str(__import__("datetime").datetime.now())
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

    print("Key rotated. Old tokens can no longer be decrypted.")


def cmd_help():
    print(f"""
 codelock v{__version__} - Inline secret encryption

  {colors("init", bold=True)}        Initialize codelock (generates key)
  {colors("encrypt <value>", bold=True)}  Encrypt a value
  {colors("decrypt <token>", bold=True)}  Decrypt a token
  {colors("check [path]", bold=True)}     Scan files for tokens, verify them
  {colors("rekey", bold=True)}       Rotate the master key
  {colors("help", bold=True)}       Show this help

 Examples:
   codelock init
   codelock encrypt "db_password=secret123"
   # Output: CLK_AES_...

   # Use it in code:
   # DB_PASSWORD = codelock.decrypt("CLK_AES_...")

   codelock check src/
""")


def colors(text, bold=False):
    if not sys.stdout.isatty():
        return text
    c = "\033[36m"
    b = "\033[1m" if bold else ""
    return f"{b}{c}{text}\033[0m"


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        cmd_help()
        return

    cmd = sys.argv[1]

    if cmd == "init":
        cmd_init()
    elif cmd == "encrypt":
        cmd_encrypt(sys.argv[2:])
    elif cmd == "decrypt":
        cmd_decrypt(sys.argv[2:])
    elif cmd == "check":
        cmd_check(sys.argv[2:])
    elif cmd == "rekey":
        cmd_rekey()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print("Run 'codelock help' for usage.", file=sys.stderr)
        sys.exit(1)
