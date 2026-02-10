import os
import ssl as ssl_module
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

from flask import Flask, jsonify, request

from auth.hmac_auth import HMACAuth
from orm.models import FormModel, UserModel

app = Flask(__name__)
auth_app = Flask(__name__)
form_model = FormModel()
user_model = UserModel()


@app.route("/", methods=["GET"])
def api_root():
    return jsonify(
        {
            "status": "active",
            "service": "Audit ORM System",
            "version": "1.0.0",
            "endpoints": {
                "admin": "/admin/forms",
                "operations": "/operations/form/{id}/{action}",
                "forms": "/submit-form",
            },
        }
    )


@app.route("/submit-form", methods=["POST"])
def submit_form():
    payload = {
        "nombre": request.form.get("nombre"),
        "email": request.form.get("email"),
        "producto": request.form.get("producto"),
    }
    form_id = form_model.create_form(payload)
    return jsonify({"status": "received", "form_id": form_id}), 201


@app.route("/admin/forms", methods=["GET"])
def admin_get_forms():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("HMAC "):
        return jsonify({"error": "HMAC authentication required"}), 401

    forms = form_model.get_all_forms(archived=False)
    return jsonify({"forms": forms})


@app.route("/operations/form/<int:form_id>/<action>", methods=["POST"])
def operations_form_action(form_id: int, action: str):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({"error": "API key required"}), 401

    if action == "approve":
        form_model.approve_form(form_id, "operations_user")
        return jsonify({"status": "approved"})
    if action == "decline":
        reason = (request.json or {}).get("reason", "")
        form_model.decline_form(form_id, reason)
        return jsonify({"status": "declined"})
    return jsonify({"error": "Invalid action"}), 400


@auth_app.route("/auth", methods=["POST"])
def authenticate():
    data = request.json or {}
    username = data.get("username")

    user = user_model.get_user_by_username(username)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if user["role"] == "admin":
        hmac_auth = HMACAuth(user["hmac_secret"])
        token = hmac_auth.generate_timestamped_token(username)
        return jsonify({"token": token, "role": "admin"})
    return jsonify({"api_key": "generated_key_here", "role": "operations"})


@auth_app.route("/block", methods=["POST"])
def block_user():
    return jsonify({"status": "blocked"})


class StaticHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="src/static", **kwargs)


def run_http_server(port: int, use_ssl: bool = False) -> None:
    server = HTTPServer(("0.0.0.0", port), StaticHandler)
    if use_ssl:
        context = ssl_module.SSLContext(ssl_module.PROTOCOL_TLS_SERVER)
        context.load_cert_chain("src/static/ssl/localhost.crt", "src/static/ssl/localhost.key")
        server.socket = context.wrap_socket(server.socket, server_side=True)
    print(f"Serving static on port {port}")
    server.serve_forever()


def run_pre_deploy_scan() -> None:
    print("Ejecutando scanner de seguridad pre-deploy...")
    os.system("python src/scanner/pre_deploy_scan.py")
    print("Scan completado. Iniciando servidores...")


def initialize_database() -> None:
    if not user_model.get_user_by_username("admin1"):
        user_model.create_user("admin1", "admin", hmac_secret="admin_secret_123")
    if not user_model.get_user_by_username("ops1"):
        user_model.create_user("ops1", "operations", api_key_hash="hashed_key_123")

    if not form_model.get_all_forms(False):
        form_model.create_form({"nombre": "Juan", "producto": "auditoria_basica"})
        form_model.create_form({"nombre": "Maria", "producto": "auditoria_avanzada"})


def start() -> None:
    run_pre_deploy_scan()
    initialize_database()

    threads = [
        threading.Thread(target=run_http_server, args=(80, False), daemon=True),
        threading.Thread(target=run_http_server, args=(443, True), daemon=True),
        threading.Thread(target=run_http_server, args=(8080, False), daemon=True),
        threading.Thread(target=lambda: app.run(port=5000, debug=False), daemon=True),
        threading.Thread(target=lambda: app.run(port=5001, debug=False), daemon=True),
        threading.Thread(target=lambda: auth_app.run(port=5002, debug=False), daemon=True),
    ]

    for thread in threads:
        thread.start()

    print("Sistema iniciado.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Deteniendo servidores...")


if __name__ == "__main__":
    start()
