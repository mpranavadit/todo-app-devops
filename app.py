import os
import sqlite3

from flask import Flask, abort, g, jsonify, redirect, render_template, request, url_for

APP_VERSION = "v3"   # bump this for each release in the CI/CD demo

app = Flask(__name__)
app.config["DB_PATH"] = os.environ.get(
    "DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo.db")
)


# ---------- Database ----------
def init_db():
    path = app.config["DB_PATH"]
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
               id      INTEGER PRIMARY KEY AUTOINCREMENT,
               text    TEXT    NOT NULL,
               done    INTEGER NOT NULL DEFAULT 0,
               created TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP)"""
    )
    conn.commit()
    conn.close()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_counts():
    total, done = get_db().execute(
        "SELECT COUNT(*), COALESCE(SUM(done), 0) FROM tasks"
    ).fetchone()
    percent = round(done / total * 100) if total else 0
    return {"total": total, "done": done, "pending": total - done, "percent": percent}


@app.context_processor
def inject_version():
    return {"version": APP_VERSION}


init_db()


# ---------- Pages ----------
@app.route("/")
def index():
    current = request.args.get("filter", "all")
    if current not in ("all", "active", "done"):
        current = "all"
    where = {"active": "WHERE done = 0", "done": "WHERE done = 1"}.get(current, "")
    tasks = get_db().execute(f"SELECT * FROM tasks {where} ORDER BY id").fetchall()
    return render_template("index.html", tasks=tasks, current=current, **get_counts())


@app.route("/stats")
def stats():
    recent = get_db().execute(
        "SELECT * FROM tasks ORDER BY id DESC LIMIT 5"
    ).fetchall()
    return render_template("stats.html", recent=recent, **get_counts())


@app.route("/about")
def about():
    return render_template("about.html")


# ---------- CRUD ----------
@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("task", "").strip()[:140]
    if text:
        db = get_db()
        db.execute("INSERT INTO tasks (text) VALUES (?)", (text,))
        db.commit()
    return redirect(url_for("index"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        abort(404)
    if request.method == "POST":
        text = request.form.get("task", "").strip()[:140]
        if text:
            db.execute("UPDATE tasks SET text = ? WHERE id = ?", (text, task_id))
            db.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", task=task)


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
    db.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/clear", methods=["POST"])
def clear():
    db = get_db()
    db.execute("DELETE FROM tasks WHERE done = 1")
    db.commit()
    return redirect(url_for("index"))


@app.route("/health")
def health():
    get_db().execute("SELECT 1")
    return jsonify(status="ok", version=APP_VERSION)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
