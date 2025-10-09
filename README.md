#The views:
#!./templates/
# crear template del 81% de toda app.
cat << base.html << EOF```!DOCTYPE
<html>
<title><title>
</html>
<head>
<body>
</body>
</html>
```EOF


cat << app.py << EOF 
```
import CUSTOM.src 
`python
# Extensión para red PiTech
def share_safely(self, content, recipients):
    """Compartir archivos firmados en red P2P"""
    encrypted_package = {
        'content': content,
        'signature': self.sign_content(content),
        'picoin_id': self.picoin_id,
        'timestamp': datetime.now().isoformat(),
        'recipients': recipients  # Lista de PiCoin IDs autorizados
    }
    return self.encrypt_for_recipients(encrypted_package)
```

cat << safe_file_writer.py << EOF
```
import hashlib
import json
import os
import socket
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class SafeFileWriter:
    def __init__(self, key_dir=".keys"):
        self.key_dir = key_dir
        os.makedirs(self.key_dir, exist_ok=True)
        self.private_key = None
        self.public_key = None
        self.picoin_id = None
        self._load_or_generate_keys()

    def _load_or_generate_keys(self):
        priv_path = os.path.join(self.key_dir, "private.pem")
        pub_path = os.path.join(self.key_dir, "public.pem")

        if os.path.exists(priv_path) and os.path.exists(pub_path):
            with open(priv_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(f.read(), password=None)
            with open(pub_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(f.read())
        else:
            self._generate_keys(priv_path, pub_path)

        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        fingerprint = hashlib.sha3_256(pub_bytes).hexdigest()
        self.picoin_id = f"PIC-{fingerprint[:8]}-{fingerprint[-4:]}"

    def _generate_keys(self, priv_path, pub_path):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        self.public_key = self.private_key.public_key()

        with open(priv_path, "wb") as f:
            f.write(
                self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        with open(pub_path, "wb") as f:
            f.write(
                self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

        os.chmod(priv_path, 0o600)
        os.chmod(pub_path, 0o644)

    def sign_content(self, content: str) -> bytes:
        return self.private_key.sign(
            content.encode("utf-8"),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

    def save_signed_file(self, content: str, filename: str):
        signature = self.sign_content(content)
        nonce = os.urandom(16).hex()
        ip = self._get_local_ip()

        file_data = {
            "picoin_id": self.picoin_id,
            "timestamp": datetime.now().isoformat(),
            "nonce": nonce,
            "source_ip": ip,
            "content": content,
            "signature": signature.hex(),
            "public_key": self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode("utf-8"),
        }

        with open(filename, "w") as f:
            json.dump(file_data, f, indent=2)

        file_hash = self._hash_file(filename)
        print(f"✓ Archivo firmado con hash: {file_hash}")
        self.create_verification_script(filename, file_hash)

    def _hash_file(self, filename):
        h = hashlib.sha3_256()
        with open(filename, "rb") as f:
            while chunk := f.read(4096):
                h.update(chunk)
        return h.hexdigest()

    def _get_local_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "unknown"

    def create_verification_script(self, filename, file_hash):
        script_name = f"verify_{os.path.basename(filename)}.py"
        code = f"""#!/usr/bin/env python3
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import hashlib

def verify_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    public_key = serialization.load_pem_public_key(data['public_key'].encode())
    signature = bytes.fromhex(data['signature'])
    try:
        public_key.verify(
            signature,
            data['content'].encode('utf-8'),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print('✓ Firma válida')
    except Exception as e:
        print('✗ Firma inválida:', e)
        return False

    h = hashlib.sha3_256()
    with open(filename, 'rb') as f:
        while chunk := f.read(4096):
            h.update(chunk)
    if h.hexdigest() == '{file_hash}':
        print('✓ Integridad confirmada (hash coincide)')
    else:
        print('✗ Hash alterado')
    print(f"PiCoin ID: {{data['picoin_id']}}")
    return True

if __name__ == '__main__':
    verify_file('{filename}')
"""
        with open(script_name, "w") as f:
            f.write(code)
        os.chmod(script_name, 0o755)
        print(f"✓ Script de verificación generado: {script_name}")

if __name__ == "__main__":
    writer = SafeFileWriter()
    content = "EL SCRIPT MÁS SEGURO ES EL QUE NO EXISTE.\n#Anti-tamper test\nEOF"
    writer.save_signed_file(content, "secure_arachne_file.json")
```
