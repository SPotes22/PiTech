# GANGSTER README — For the Real G's (like the G in lasagnia)

**PiTech · SafeFileWriter · SysAdminInitAuthModule_mook & more!**

> *Open-source white-hat crypto toolkit for folks who build, ship, and don’t trust anything that isn’t verifiably signed.*

---

## Why this exists

This repo is for the engineers who sweat the small stuff. We sign, timestamp, and verify every file so you — or anyone you trust — can audit origin and integrity without squinting at raw keys. Think of it as a tiny, portable, auditable vault that spits out a verification script for every file it touches.

Built for: seniors, sysadmins, devs who want provable chains of custody for files, and anyone who likes gangster-level hygiene.

---

## Highlights (why it’s gangster)

* ✅ RSA 3072 keypair generation with safe file permissions
* ✅ SHA3-256 public-key fingerprint → human-friendly **PiCoin ID**
* ✅ Deterministic signed JSON packaging with nonce & source metadata
* ✅ Automatic verification script generation (`verify_<file>.py`)
* ✅ Low-deps: `cryptography` + Python stdlib
* ✅ Portable: outputs plain JSON + scripts anyone with Python can run

---

## Quickstart (run this and flex)

```bash
# clone
git clone https://github.com/SPotes22/PiTech.git
cd PiTech/layer_0_the_auth

# create venv (recommended)
python3 -m venv .venv
source .venv/bin/activate

# deps
pip install -r requirements.txt

# run the safe writer example (creates keys + signed JSON + verification script)
python3 safe_file_writer.py

# verify the produced file
./verify_secure_arachne_file.json.py  # or: python3 verify_secure_arachne_file.json.py
```

> Files created:
>
> * `private.pem`, `public.pem` in `.keys/` (private perms `600`)
> * `secure_arachne_file.json` (signed payload)
> * `verify_secure_arachne_file.json.py` (verification script)

---

## How it works (short)

1. On first run, `SafeFileWriter` loads or generates an RSA 3072 keypair.
2. Public key bytes are hashed with SHA3-256 to create a compact **PiCoin ID** fingerprint.
3. `save_signed_file()` signs the plaintext content with PSS+SHA256 and writes a JSON file containing `content`, `signature` (hex), `public_key` (PEM), `timestamp`, `nonce` and metadata.
4. A standalone `verify_*.py` script is generated so anyone can check authenticity and integrity without importing your library.

---

## API (developer quick reference)

```python
from safe_file_writer import SafeFileWriter

w = SafeFileWriter(key_dir='.keys')
# sign & save
w.save_signed_file('some secret content', 'output.json')

# generated verification script: verify_output.json.py
```

---

## Security notes (read this like a contract)

* **Private key safety:** `private.pem` is written with `0600`. Keep backups in an HSM or secure vault if used in production.
* **Do NOT commit keys or secrets** to git. Use the repo `.gitignore` — keys and `secrets/` are blacklisted.
* **Rotate keys** when you suspect compromise. The PiCoin ID changes with a new public key.
* **Signature algorithm** uses RSA-PSS + SHA256; hashes use SHA3-256 for fingerprinting.
* **Local IP** is recorded for forensics; if privacy is required, sanitize or omit it.

---

## CI / deployment tips

* Keep signing keys out of CI. Use environment-backed secrets or an agent with local key access.
* CI can run the verification script as a gating step to assert artifact provenance.
* Consider publishing only signed artifacts and their verification scripts to package repos.

---

## Troubleshooting

* `ModuleNotFoundError: cryptography` → `pip install cryptography` inside your venv
* `PermissionError` creating `.keys/private.pem` → check umask or run permissions as correct user
* `Signature invalid` on verification → file was mutated after signing or wrong file supplied

---

## Contributing & Tone

This is strict but generous: we welcome PRs, but keep the hygiene high. If your patch adds a feature, include tests and update the verification expectations.

* Be readable. Be auditable. Ship signed.

---

## License

GPL-3.0 — share, adapt, and keep the world safer.

---

## Credits

PiTech · SPotes22 — Gangster white-hat legacy.

---

Want a `Makefile` or a tiny `install.sh` to automate the quickstart above? Say the word and I’ll drop it in.

