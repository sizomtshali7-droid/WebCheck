"""Practice website with deliberate weaknesses (fake data, local computer only).

Normal start  -> WEAK version (insecure on purpose).
SECURE=1      -> FIXED version.
Never put this on the internet.
"""
import os
import secrets
import traceback

from flask import Flask, jsonify, make_response, request
from werkzeug.exceptions import HTTPException
from werkzeug.serving import WSGIRequestHandler

SECURE = os.environ.get("SECURE", "0") == "1"
PORT = int(os.environ.get("PORT", "5050"))

app = Flask(__name__)
if SECURE:
    WSGIRequestHandler.version_string = lambda self: "webserver"  # hide the version text

USERS = {
    "alice": {"id": 1, "password": "alicepass", "role": "user"},
    "bob": {"id": 2, "password": "bobpass", "role": "user"},
    "admin": {"id": 3, "password": "adminpass", "role": "admin"},
}
ORDERS = {
    101: {"id": 101, "owner_id": 1, "item": "Laptop"},
    102: {"id": 102, "owner_id": 2, "item": "Phone"},
}
TOKENS = {}


def current_user():
    header = request.headers.get("Authorization", "")
    name = TOKENS.get(header[7:]) if header.startswith("Bearer ") else None
    return USERS.get(name)


@app.after_request
def add_headers(response):
    if SECURE:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
    else:
        response.headers["Server"] = "PracticeApp/1.0 (Flask 3)"   # WEAK: shows a version
    return response


@app.errorhandler(Exception)
def handle_error(error):
    if isinstance(error, HTTPException):
        return error
    if SECURE:
        return jsonify({"error": "Something went wrong"}), 500
    return "Error: " + str(error) + "\n" + traceback.format_exc(), 500   # WEAK: shows internals


@app.route("/")
def index():
    response = make_response("<h1>Practice shop</h1>")
    if SECURE:
        response.set_cookie("visitor", "guest-1", secure=True, httponly=True)
    else:
        response.set_cookie("visitor", "guest-1")                       # WEAK: no protection flags
    return response


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    user = USERS.get(str(data.get("username", "")))
    if user is None or user["password"] != data.get("password"):
        if SECURE:
            return jsonify({"error": "Invalid username or password"}), 401
        if user is None:                                                 # WEAK: reveals which names exist
            return jsonify({"error": "User not found"}), 404
        return jsonify({"error": "Wrong password"}), 401
    token = secrets.token_hex(16)
    TOKENS[token] = data["username"]
    response = jsonify({"token": token})
    if SECURE:
        response.set_cookie("session", token, secure=True, httponly=True)
    else:
        response.set_cookie("session", token)
    return response


@app.route("/api/orders/<int:order_id>")
def get_order(order_id):
    user = current_user()
    if user is None:
        return jsonify({"error": "Login required"}), 401
    order = ORDERS.get(order_id)
    if order is None:
        return jsonify({"error": "Not found"}), 404
    if SECURE and order["owner_id"] != user["id"]:                      # WEAK version skips this check
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(order)


@app.route("/api/admin/users")
def admin_users():
    user = current_user()
    if user is None:
        return jsonify({"error": "Login required"}), 401
    if SECURE and user["role"] != "admin":                              # WEAK version skips this check
        return jsonify({"error": "Forbidden"}), 403
    return jsonify([{"username": n, "password": u["password"]} for n, u in USERS.items()])


@app.route("/api/search")
def search():
    query = request.args.get("q", "")
    if "'" in query:
        raise ValueError("Bad input in: SELECT * FROM products WHERE name = '" + query + "'")
    return jsonify({"results": []})


if __name__ == "__main__":
    print(("FIXED" if SECURE else "WEAK") + f" practice website on http://127.0.0.1:{PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=False)
