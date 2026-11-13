from flask import Flask, request, redirect, render_template_string, jsonify

app = Flask(__name__)
tasks = []          # in-memory list; resets on container restart
next_id = 1

PAGE = """
<!doctype html>
<title>To-Do App</title>
<h1>My To-Do List (v1)</h1>
<form method="post" action="/add">
  <input name="task" placeholder="New task" required>
  <button>Add</button>
</form>
<ul>
{% for t in tasks %}
  <li>{{ t.text }} <a href="/delete/{{ t.id }}">[delete]</a></li>
{% endfor %}
</ul>
"""

@app.route("/")
def index():
    return render_template_string(PAGE, tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    global next_id
    text = request.form.get("task", "").strip()
    if text:
        tasks.append({"id": next_id, "text": text})
        next_id += 1
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return redirect("/")

@app.route("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
