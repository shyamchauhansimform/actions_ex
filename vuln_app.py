"""
Intentionally vulnerable Flask app for Wapiti DAST demo.
DO NOT deploy this in production.
"""
from flask import Flask, request, redirect, make_response, session, render_template_string
import subprocess
import sqlite3
import os
import base64
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# ── Authentication Credentials ───────────────────────────────────────────────
VALID_USERNAME = "admin"
VALID_PASSWORD = "pass"

def check_auth(username, password):
    """Verify username and password."""
    return username == VALID_USERNAME and password == VALID_PASSWORD

def require_login(f):
    """Decorator to require session-based login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# ── Bootstrap an in-memory SQLite DB with demo data ──────────────────────────
def get_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, role TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'admin', 'admin')")
    conn.execute("INSERT INTO users VALUES (2, 'alice', 'user')")
    conn.commit()
    return conn

# ── Pure input-builders (extracted so they can be fuzz-tested directly) ──────
# ⚠️ VULNERABLE: no sanitisation — kept unsanitised on purpose for DAST/fuzz demos
def build_user_query(user_id):
    """Build the SQL query used by /user. Unsanitised string interpolation."""
    return f"SELECT * FROM users WHERE id = {user_id}"

def build_ping_command(host):
    """Build the shell command used by /ping. Unsanitised string interpolation."""
    return f"echo Pinging {host}"

# ── Home: lists all demo endpoints ───────────────────────────────────────────
@app.route("/")
@require_login
def index():
    return """
    <html><body>
    <h1>Vulnerable Demo App</h1>
    <p>Welcome, <strong>{{ user }}</strong>! | <a href="/logout">Logout</a></p>
    <ul>
      <li><a href="/search?q=hello">Search (XSS)</a></li>
      <li><a href="/user?id=1">User lookup (SQLi)</a></li>
      <li><a href="/ping?host=127.0.0.1">Ping (Command Injection)</a></li>
      <li><a href="/redirect?url=http://example.com">Redirect (Open Redirect)</a></li>
      <li><a href="/greet">Greet form (XSS via POST)</a></li>
    </ul>
    </body></html>
    """.replace("{{ user }}", session.get("user", "User"))

# ── Login Page ──────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if check_auth(username, password):
            session["user"] = username
            return redirect("/")
        else:
            return """
            <html><body>
            <h2>Login</h2>
            <form method="POST">
              Username: <input name="username" type="text" required><br>
              Password: <input name="password" type="password" required><br>
              <button type="submit">Login</button>
            </form>
            <p style="color:red;"><strong>Invalid credentials!</strong></p>
            <p>Demo credentials: <strong>admin / pass</strong></p>
            </body></html>
            """
    return """
    <html><body>
    <h2>Login</h2>
    <form method="POST">
      Username: <input name="username" type="text" required><br>
      Password: <input name="password" type="password" required><br>
      <button type="submit">Login</button>
    </form>
    <p>Demo credentials: <strong>admin / pass</strong></p>
    </body></html>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ── XSS: reflects ?q= directly into HTML without escaping ────────────────────
@require_login
@app.route("/search")
def search():
    q = request.args.get("q", "")
    # ⚠️ VULNERABLE: user input reflected without escaping
    return f"<html><body><h2>Results for: {q}</h2></body></html>"

# ── SQLi: unsanitised user id passed directly into SQL query ─────────────────
@require_login
@app.route("/user")
def user():
    user_id = request.args.get("id", "1")
    conn = get_db()
    try:
        # ⚠️ VULNERABLE: string interpolation in SQL
        cursor = conn.execute(build_user_query(user_id))
        row = cursor.fetchone()
        if row:
            return f"<html><body><p>User: {row[1]} Role: {row[2]}</p></body></html>"
        return "<html><body><p>User not found</p></body></html>"
    except Exception as e:
        # ⚠️ VULNERABLE: exposes raw DB error to the client
        return f"<html><body><p>Error: {e}</p></body></html>", 500

# ── Command Injection: passes ?host= directly to shell ───────────────────────
@require_login
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    try:
        # ⚠️ VULNERABLE: shell=True with unsanitised input
        result = subprocess.check_output(
            build_ping_command(host), shell=True, text=True, timeout=3
        )
        return f"<html><body><pre>{result}</pre></body></html>"
    except Exception as e:
        return f"<html><body><p>Error: {e}</p></body></html>", 500

# ── Open Redirect: blindly redirects to any URL ──────────────────────────────
@require_login
@app.route("/redirect")
def open_redirect():
    url = request.args.get("url", "/")
    # ⚠️ VULNERABLE: no validation on the target URL
    return redirect(url)

# ── XSS via POST form: reflects name back without escaping ───────────────────
@require_login
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
