from flask import Flask, request, redirect, render_template_string, jsonify, url_for

app = Flask(__name__)

APP_VERSION = "v1"   # change to "v2" for the CI/CD demo

tasks = []           # in-memory list; resets when the container restarts
next_id = 1

PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tasks</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #eef1f6;
    --surface: #ffffff;
    --ink: #172033;
    --muted: #657089;
    --line: #dde2ec;
    --accent: #3b4cca;
    --accent-ink: #ffffff;
    --accent-soft: #e5e8fb;
    --done: #1f9d6b;
    --danger: #c0392b;
    --shadow: 0 1px 2px rgba(23,32,51,.06), 0 12px 32px -12px rgba(23,32,51,.18);
    --display: "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
    --body: "Figtree", "Segoe UI", system-ui, sans-serif;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0e1220;
      --surface: #171c2e;
      --ink: #eaeefb;
      --muted: #9aa5c4;
      --line: #2a3150;
      --accent: #8b97ff;
      --accent-ink: #0e1220;
      --accent-soft: #232a4d;
      --done: #4fd1a0;
      --danger: #ff8478;
      --shadow: 0 1px 2px rgba(0,0,0,.4), 0 12px 32px -12px rgba(0,0,0,.6);
    }
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body {
    margin: 0;
    min-height: 100vh;
    background: var(--bg);
    color: var(--ink);
    font: 16px/1.5 var(--body);
    display: flex;
    justify-content: center;
    padding: 48px 16px 64px;
  }
  main { width: 100%; max-width: 620px; }

  header { margin-bottom: 24px; }
  .top { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; }
  h1 {
    margin: 0;
    font: 800 clamp(2.4rem, 8vw, 3.4rem)/1 var(--display);
    letter-spacing: -0.03em;
  }
  .version {
    font-size: .8rem;
    color: var(--muted);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 2px 10px;
    background: var(--surface);
  }

  .summary { margin: 20px 0 0; }
  .summary-text { display: flex; justify-content: space-between; color: var(--muted); font-size: .95rem; margin-bottom: 8px; }
  .summary-text strong { color: var(--ink); font-weight: 600; }
  .bar { height: 10px; border-radius: 999px; background: var(--line); overflow: hidden; }
  .bar > span {
    display: block; height: 100%;
    width: {{ percent }}%;
    background: var(--done);
    border-radius: 999px;
    transition: width .4s ease;
  }

  .card {
    background: var(--surface);
    border-radius: 18px;
    box-shadow: var(--shadow);
    overflow: hidden;
  }

  form.add { display: flex; gap: 10px; padding: 14px; border-bottom: 1px solid var(--line); }
  form.add input {
    flex: 1; min-width: 0;
    font: inherit; color: inherit;
    padding: 12px 14px;
    border: 1.5px solid var(--line);
    border-radius: 12px;
    background: transparent;
  }
  form.add input::placeholder { color: var(--muted); }
  form.add input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }

  button { font: inherit; cursor: pointer; }
  .btn-primary {
    border: 0; border-radius: 12px;
    background: var(--accent); color: var(--accent-ink);
    padding: 0 20px; font-weight: 600;
    transition: transform .1s ease, filter .15s ease;
  }
  .btn-primary:hover { filter: brightness(1.08); }
  .btn-primary:active { transform: scale(.97); }

  nav.filters { display: flex; gap: 6px; padding: 12px 14px; border-bottom: 1px solid var(--line); }
  nav.filters a {
    text-decoration: none; color: var(--muted);
    padding: 6px 14px; border-radius: 999px; font-size: .92rem; font-weight: 500;
  }
  nav.filters a:hover { color: var(--ink); }
  nav.filters a[aria-current="page"] { background: var(--accent-soft); color: var(--accent); font-weight: 600; }

  ul { list-style: none; margin: 0; padding: 0; }
  li { display: flex; align-items: center; gap: 12px; padding: 14px; border-bottom: 1px solid var(--line); }
  li:last-child { border-bottom: 0; }
  li form { margin: 0; display: flex; }

  .check {
    width: 26px; height: 26px; border-radius: 50%;
    border: 2px solid var(--line); background: transparent;
    display: grid; place-items: center; padding: 0; color: transparent;
    transition: background .2s ease, border-color .2s ease, color .2s ease;
  }
  .check:hover { border-color: var(--done); }
  .check svg { width: 14px; height: 14px; }
  li.done .check { background: var(--done); border-color: var(--done); color: #fff; }

  .text { flex: 1; word-break: break-word; }
  li.done .text { color: var(--muted); text-decoration: line-through; text-decoration-color: var(--muted); }

  .del {
    border: 0; background: transparent; color: var(--muted);
    width: 34px; height: 34px; border-radius: 10px; font-size: 1.1rem; line-height: 1;
  }
  .del:hover { background: color-mix(in srgb, var(--danger) 14%, transparent); color: var(--danger); }

  .empty { padding: 44px 24px; text-align: center; color: var(--muted); }
  .empty strong { display: block; color: var(--ink); font: 700 1.2rem var(--display); margin-bottom: 4px; }

  footer.tools { display: flex; justify-content: space-between; align-items: center; padding: 12px 14px; border-top: 1px solid var(--line); color: var(--muted); font-size: .9rem; }
  .link-btn { border: 0; background: transparent; color: var(--muted); text-decoration: underline; padding: 4px; }
  .link-btn:hover { color: var(--danger); }

  :focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>
<main>
  <header>
    <div class="top">
      <h1>Tasks</h1>
      <span class="version">{{ version }}</span>
    </div>
    <div class="summary">
      <div class="summary-text">
        {% if total %}
          <span><strong>{{ done_count }} of {{ total }}</strong> done</span>
          <span>{{ percent }}%</span>
        {% else %}
          <span>Nothing planned yet</span><span></span>
        {% endif %}
      </div>
      <div class="bar" role="progressbar" aria-valuenow="{{ percent }}" aria-valuemin="0" aria-valuemax="100"><span></span></div>
    </div>
  </header>

  <section class="card">
    <form class="add" method="post" action="/add">
      <input name="task" placeholder="What needs doing?" maxlength="140" autocomplete="off" required autofocus aria-label="New task">
      <button class="btn-primary">Add task</button>
    </form>

    <nav class="filters" aria-label="Filter tasks">
      <a href="/" {% if current == 'all' %}aria-current="page"{% endif %}>All</a>
      <a href="/?filter=active" {% if current == 'active' %}aria-current="page"{% endif %}>To do</a>
      <a href="/?filter=done" {% if current == 'done' %}aria-current="page"{% endif %}>Done</a>
    </nav>

    {% if visible %}
    <ul>
      {% for t in visible %}
      <li class="{{ 'done' if t.done else '' }}">
        <form method="post" action="/toggle/{{ t.id }}">
          <button class="check" aria-label="{{ 'Mark as to do' if t.done else 'Mark as done' }}">
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8.5l3.2 3.2L13 4.8"/></svg>
          </button>
        </form>
        <span class="text">{{ t.text }}</span>
        <form method="post" action="/delete/{{ t.id }}">
          <button class="del" aria-label="Delete task">&times;</button>
        </form>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <div class="empty">
      {% if total == 0 %}
        <strong>No tasks yet</strong>
        Type something above and press Add task.
      {% elif current == 'done' %}
        <strong>Nothing finished yet</strong>
        Tick a task to see it here.
      {% else %}
        <strong>All clear</strong>
        Every task is done.
      {% endif %}
    </div>
    {% endif %}

    {% if done_count %}
    <footer class="tools">
      <span>{{ total - done_count }} left</span>
      <form method="post" action="/clear"><button class="link-btn">Clear completed</button></form>
    </footer>
    {% endif %}
  </section>
</main>
</body>
</html>
"""


@app.route("/")
def index():
    current = request.args.get("filter", "all")
    if current not in ("all", "active", "done"):
        current = "all"

    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    percent = round(done_count / total * 100) if total else 0

    if current == "active":
        visible = [t for t in tasks if not t["done"]]
    elif current == "done":
        visible = [t for t in tasks if t["done"]]
    else:
        visible = tasks

    return render_template_string(
        PAGE,
        visible=visible,
        total=total,
        done_count=done_count,
        percent=percent,
        current=current,
        version=APP_VERSION,
    )


@app.route("/add", methods=["POST"])
def add():
    global next_id
    text = request.form.get("task", "").strip()[:140]
    if text:
        tasks.append({"id": next_id, "text": text, "done": False})
        next_id += 1
    return redirect(url_for("index"))


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle(task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = not t["done"]
            break
    return redirect(request.referrer or url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return redirect(request.referrer or url_for("index"))


@app.route("/clear", methods=["POST"])
def clear():
    global tasks
    tasks = [t for t in tasks if not t["done"]]
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return jsonify(status="ok", version=APP_VERSION)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)