import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

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

    # ✅ Table (single domain) + reg_link required
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

    # ✅ Migration: add reg_link if your DB was created earlier without it
    cur.execute("PRAGMA table_info(events)")
    cols = {row["name"] for row in cur.fetchall()}
    if "reg_link" not in cols:
        # Add as NOT NULL with default so old rows don't break
        cur.execute("ALTER TABLE events ADD COLUMN reg_link TEXT NOT NULL DEFAULT ''")

    conn.commit()
    conn.close()


# -----------------------------
# Pages
# -----------------------------
@app.route("/")
def admin_home():
    return render_template("admin_dashboard.html")


@app.route("/user")
def user_dashboard():
    return render_template("user_dashboard.html")


@app.route("/bookmarks")
def bookmarks_page():
    return render_template("bookmarks.html")


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


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
