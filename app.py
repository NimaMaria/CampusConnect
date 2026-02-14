import os
import sqlite3
import uuid
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "campusconnect_secret_key_2026"
app.permanent_session_lifetime = timedelta(days=7)

# ✅ Always use absolute paths (prevents "event disappears after refresh")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "campusconnect.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -----------------------------
# Helper Functions
# -----------------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_conn():
    # ✅ timeout helps avoid “database is locked”
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row

    # ✅ IMPORTANT for Flask multi-requests (especially Windows)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")

    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # ✅ Events table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT,
            domain TEXT NOT NULL,
            reg_link TEXT NOT NULL,
            content TEXT,
            poster_url TEXT
        )
    """)

    # ✅ Users table for student registration
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # ✅ Migration: add reg_link if your DB was created earlier without it
    cur.execute("PRAGMA table_info(events)")
    cols = {row["name"] for row in cur.fetchall()}
    if "reg_link" not in cols:
        cur.execute("ALTER TABLE events ADD COLUMN reg_link TEXT NOT NULL DEFAULT ''")

    # ✅ Create test user if it doesn't exist
    cur.execute("SELECT id FROM users WHERE phone=?", ("0123456789",))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (phone, password) VALUES (?, ?)", ("0123456789", "password123"))
        print("✅ Test user created: Phone=0123456789, Password=password123")

    conn.commit()
    conn.close()


# ✅ Auth decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_phone" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session:
            return redirect(url_for("admin_page"))
        return f(*args, **kwargs)
    return decorated_function


# ✅ PAGES
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login_page():
    if "user_phone" in session:
        return redirect(url_for("user_dashboard"))
    return render_template("login.html")


@app.route("/admin")
def admin_page():
    if "admin_logged_in" in session:
        return redirect(url_for("admin_dashboard"))
    return render_template("admin.html")


@app.route("/user-dashboard")
@login_required
def user_dashboard():
    return render_template("user_dashboard.html")


@app.route("/admin-dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")


@app.route("/bookmarks")
@login_required
def bookmarks_page():
    return render_template("bookmarks.html")


# ✅ AUTHENTICATION API
@app.route("/api/auth/signup", methods=["POST"])
def api_signup():
    try:
        phone = (request.json.get("phone") or "").strip()
        password = (request.json.get("password") or "").strip()

        if not phone or not password:
            return jsonify({"error": "Phone and password required"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        conn = get_conn()
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT id FROM users WHERE phone=?", (phone,))
        if cur.fetchone():
            conn.close()
            return jsonify({"error": "Phone number already registered"}), 400

        # Create new user
        cur.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, password))
        conn.commit()
        conn.close()

        return jsonify({"message": "Account created successfully"}), 201

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    try:
        phone = (request.json.get("phone") or "").strip()
        password = (request.json.get("password") or "").strip()

        if not phone or not password:
            return jsonify({"error": "Phone and password required"}), 400

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE phone=? AND password=?", (phone, password))
        user = cur.fetchone()
        conn.close()

        if not user:
            return jsonify({"error": "Invalid phone or password"}), 401

        session["user_phone"] = phone
        session.permanent = True
        return jsonify({"message": "Login successful"}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/auth/admin-login", methods=["POST"])
def api_admin_login():
    try:
        username = (request.json.get("username") or "").strip()
        password = (request.json.get("password") or "").strip()

        # ✅ Admin credentials
        ADMIN_USER = "admin"
        ADMIN_PASS = "12345"

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin_logged_in"] = True
            session.permanent = True
            return jsonify({"message": "Admin login successful"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/api/auth/check", methods=["GET"])
def api_auth_check():
    return jsonify({
        "user_logged_in": "user_phone" in session,
        "admin_logged_in": "admin_logged_in" in session,
        "user_phone": session.get("user_phone", "")
    }), 200


# -----------------------------
# API: GET events
# -----------------------------
@app.route("/api/events", methods=["GET"])
def api_events():
    domain = (request.args.get("domain") or "All").strip()

    conn = get_conn()
    cur = conn.cursor()

    if domain == "All":
        cur.execute("SELECT * FROM events ORDER BY date ASC")
    else:
        # ✅ single-domain filter (exact)
        cur.execute("SELECT * FROM events WHERE domain = ? ORDER BY date ASC", (domain,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows), 200


# -----------------------------
# API: ADD event
# -----------------------------
@app.route("/api/events", methods=["POST"])
def api_add_event():
    try:
        name = (request.form.get("name") or "").strip()
        date = (request.form.get("date") or "").strip()
        time = (request.form.get("time") or "").strip()
        domain = (request.form.get("domain") or "").strip()   # ✅ single value
        content = (request.form.get("content") or "").strip()
        reg_link = (request.form.get("reg_link") or "").strip()

        # ✅ Validations
        if not name:
            return jsonify({"error": "Event name is required"}), 400
        if not date:
            return jsonify({"error": "Date is required"}), 400
        if not domain:
            return jsonify({"error": "Domain is required"}), 400
        if not reg_link:
            return jsonify({"error": "Registration link is required"}), 400

        # ✅ Auto add https if missing
        if not (reg_link.startswith("http://") or reg_link.startswith("https://")):
            reg_link = "https://" + reg_link

        poster_url = ""
        file = request.files.get("poster")

        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({"error": "Poster must be png/jpg/jpeg/webp"}), 400

            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            safe = secure_filename(file.filename)
            save_name = f"{abs(hash(safe))}_{safe}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], save_name)
            file.save(save_path)

            # URL for browser
            poster_url = "/static/uploads/" + save_name

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO events (name, date, time, domain, reg_link, content, poster_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, date, time, domain, reg_link, content, poster_url))

        event_id = cur.lastrowid
        conn.commit()
        conn.close()

        return jsonify({"message": "Event added successfully", "id": event_id}), 201

    except Exception as e:
        # ✅ Ensures frontend always receives JSON
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# -----------------------------
# API: DELETE event
# -----------------------------
@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT poster_url FROM events WHERE id=?", (event_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Event not found"}), 404

    poster_url = row["poster_url"] or ""

    cur.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()

    # Delete poster file if exists
    if poster_url.startswith("/static/uploads/"):
        filename = poster_url.replace("/static/uploads/", "")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify({"message": "Event deleted successfully"}), 200


# ✅ API: UPDATE event
@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    try:
        name = (request.form.get("name") or "").strip()
        date = (request.form.get("date") or "").strip()
        time = (request.form.get("time") or "").strip()
        domain = (request.form.get("domain") or "").strip()
        content = (request.form.get("content") or "").strip()
        reg_link = (request.form.get("reg_link") or "").strip()

        # ✅ Validations
        if not name:
            return jsonify({"error": "Event name is required"}), 400
        if not date:
            return jsonify({"error": "Date is required"}), 400
        if not domain:
            return jsonify({"error": "Domain is required"}), 400
        if not reg_link:
            return jsonify({"error": "Registration link is required"}), 400

        # ✅ Auto add https if missing
        if not (reg_link.startswith("http://") or reg_link.startswith("https://")):
            reg_link = "https://" + reg_link

        conn = get_conn()
        cur = conn.cursor()

        # Get existing event
        cur.execute("SELECT poster_url FROM events WHERE id=?", (event_id,))
        row = cur.fetchone()

        if not row:
            conn.close()
            return jsonify({"error": "Event not found"}), 404

        poster_url = row["poster_url"] or ""

        # Handle new poster if uploaded
        file = request.files.get("poster")
        if file and file.filename:
            if not allowed_file(file.filename):
                conn.close()
                return jsonify({"error": "Poster must be png/jpg/jpeg/webp"}), 400

            try:
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

                # Delete old poster
                if poster_url.startswith("/static/uploads/"):
                    old_filename = poster_url.replace("/static/uploads/", "")
                    old_path = os.path.join(UPLOAD_FOLDER, old_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                # Save new poster
                safe = secure_filename(file.filename)
                ext = safe.rsplit(".", 1)[-1].lower() if "." in safe else "jpg"
                unique_name = f"{uuid.uuid4().hex}.{ext}"
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                file.save(save_path)

                if not os.path.exists(save_path):
                    conn.close()
                    return jsonify({"error": "Failed to save poster file"}), 500

                poster_url = "/static/uploads/" + unique_name

            except Exception as file_err:
                conn.close()
                return jsonify({"error": f"File upload error: {str(file_err)}"}), 500

        # Update event
        cur.execute("""
            UPDATE events 
            SET name=?, date=?, time=?, domain=?, reg_link=?, content=?, poster_url=?
            WHERE id=?
        """, (name, date, time, domain, reg_link, content, poster_url, event_id))

        conn.commit()
        conn.close()

        return jsonify({"message": "Event updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
