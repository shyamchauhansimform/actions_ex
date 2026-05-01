"""
Intentionally vulnerable Flask app for Wapiti DAST demo.
DO NOT deploy this in production.
"""
from flask import Flask, request, redirect, make_response
import subprocess
import sqlite3
import os

app = Flask(__name__)

# ── Bootstrap an in-memory SQLite DB with demo data ──────────────────────────
def get_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, role TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'admin', 'admin')")
    conn.execute("INSERT INTO users VALUES (2, 'alice', 'user')")
    conn.commit()
    return conn

# ── Home: lists all demo endpoints ───────────────────────────────────────────
@app.route("/")
def index():
    return """
    <html><body>
    <h1>Vulnerable Demo App</h1>
    <ul>
      <li><a href="/search?q=hello">Search (XSS)</a></li>
      <li><a href="/user?id=1">User lookup (SQLi)</a></li>
      <li><a href="/ping?host=127.0.0.1">Ping (Command Injection)</a></li>
      <li><a href="/redirect?url=http://example.com">Redirect (Open Redirect)</a></li>
      <li><a href="/greet">Greet form (XSS via POST)</a></li>
    </ul>
    </body></html>
    """

# ── XSS: reflects ?q= directly into HTML without escaping ────────────────────
@app.route("/search")
def search():
    q = request.args.get("q", "")
    # ⚠️ VULNERABLE: user input reflected without escaping
    return f"<html><body><h2>Results for: {q}</h2></body></html>"

# ── SQLi: unsanitised user id passed directly into SQL query ─────────────────
@app.route("/user")
def user():
    user_id = request.args.get("id", "1")
    conn = get_db()
    try:
        # ⚠️ VULNERABLE: string interpolation in SQL
        cursor = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
        row = cursor.fetchone()
        if row:
            return f"<html><body><p>User: {row[1]} Role: {row[2]}</p></body></html>"
        return "<html><body><p>User not found</p></body></html>"
    except Exception as e:
        # ⚠️ VULNERABLE: exposes raw DB error to the client
        return f"<html><body><p>Error: {e}</p></body></html>", 500

# ── Command Injection: passes ?host= directly to shell ───────────────────────
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    try:
        # ⚠️ VULNERABLE: shell=True with unsanitised input
        result = subprocess.check_output(
            f"echo Pinging {host}", shell=True, text=True, timeout=3
        )
        return f"<html><body><pre>{result}</pre></body></html>"
    except Exception as e:
        return f"<html><body><p>Error: {e}</p></body></html>", 500

# ── Open Redirect: blindly redirects to any URL ──────────────────────────────
@app.route("/redirect")
def open_redirect():
    url = request.args.get("url", "/")
    # ⚠️ VULNERABLE: no validation on the target URL
    return redirect(url)

# ── XSS via POST form: reflects name back without escaping ───────────────────
@app.route("/greet", methods=["GET", "POST"])
def greet():
    if request.method == "POST":
        name = request.form.get("name", "")
        # ⚠️ VULNERABLE: unsanitised POST data reflected in response
        return f"<html><body><h2>Hello, {name}!</h2></body></html>"
    return """
    <html><body>
    <form method="POST">
      Name: <input name="name" type="text">
      <button type="submit">Submit</button>
    </form>
    </body></html>
    """

# ── Missing security headers & insecure cookie ───────────────────────────────
@app.after_request
def add_insecure_cookie(response):
    # ⚠️ VULNERABLE: cookie missing Secure and HttpOnly flags
    response.set_cookie("session_demo", "abc123")
    # No X-Frame-Options, no CSP, no X-Content-Type-Options set intentionally
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
