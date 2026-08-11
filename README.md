# codelock

**Inline secret encryption for codebases.** Encrypt individual values, not whole files.

Unlike `sops`, `git-crypt`, or `blackbox` which encrypt entire files or YAML/JSON
structures, codelock lets you encrypt single values and mix them freely with
plaintext — in any file type.

```
pip install codelock
```

## Usage

```bash
# Initialize
codelock init

# Encrypt a value
codelock encrypt "db_password=secret123"
# → CLK_AES_RXh0cmVtZWx5U2VjdXJlWW91ckRhdGE...

# Use the token anywhere
# config.py: DB_PASSWORD = "CLK_AES_RXh0cmVtZWx5U2VjdXJlWW91ckRhdGE..."
```

## Commands

| Command | Description |
|---|---|
| `codelock init` | Generate master key in `~/.codelock/` |
| `codelock encrypt <value>` | Encrypt a value |
| `codelock decrypt <token>` | Decrypt a token |
| `codelock check [path]` | Scan files for tokens, verify decryptability |
| `codelock rekey` | Rotate master key |

## How it works

codelock uses AES-256-GCM encryption:

1. A 256-bit key is generated and stored in `~/.codelock/key`
2. Each encryption uses a random 12-byte IV
3. Output format: `CLK_AES_<base64(iv + ciphertext + tag)>`
4. The token is deterministic but includes the IV for security

Encrypted tokens can be committed to git, shared, or embedded in any file.
Without the master key, they are indecipherable.

## Why codelock?

- **Value-level, not file-level** — encrypt one config key at a time
- **No format restrictions** — works in Python, YAML, JSON, shell scripts, .env files, any text
- **Simple key management** — single file or env var
- **Zero runtime deps** for decryption (pure Python + cryptography)
- **Git-friendly** — tokens look like strings, diffs are clean

## Security

- AES-256-GCM (authenticated encryption)
- Random IV per encryption (no two encryptions look the same)
- Key file is `chmod 600`
- Or use `CODELOCK_KEY` env var (never written to disk)

## Credits

Created and maintained by **soe1hom-arch**.

## License

MIT &copy; 2026 soe1hom-arch
