import pytest

import app as app_module


@pytest.fixture
def client(tmp_path):
    app_module.app.config["DB_PATH"] = str(tmp_path / "test.db")
    app_module.app.config["TESTING"] = True
    app_module.init_db()
    return app_module.app.test_client()


def add(client, text):
    client.post("/add", data={"task": text})


def test_home_page(client):
    assert client.get("/").status_code == 200


def test_health(client):
    data = client.get("/health").get_json()
    assert data["status"] == "ok"
    assert data["version"] == app_module.APP_VERSION


def test_add_task(client):
    add(client, "Buy milk")
    assert b"Buy milk" in client.get("/").data


def test_empty_task_is_ignored(client):
    add(client, "   ")
    assert b"No tasks yet" in client.get("/").data


def test_html_is_escaped(client):
    add(client, "<b>bold</b>")
    assert b"&lt;b&gt;" in client.get("/").data


def test_toggle_and_filters(client):
    add(client, "Write report")
    client.post("/toggle/1")
    assert b"Write report" in client.get("/?filter=done").data
    assert b"Write report" not in client.get("/?filter=active").data
    client.post("/toggle/1")
    assert b"Write report" in client.get("/?filter=active").data


def test_edit_task(client):
    add(client, "Old title")
    assert client.get("/edit/1").status_code == 200
    client.post("/edit/1", data={"task": "New title"})
    page = client.get("/").data
    assert b"New title" in page and b"Old title" not in page


def test_edit_missing_task_returns_404(client):
    assert client.get("/edit/99").status_code == 404


def test_delete_task(client):
    add(client, "Temporary")
    client.post("/delete/1")
    assert b"Temporary" not in client.get("/").data


def test_clear_completed(client):
    add(client, "Done one")
    add(client, "Open one")
    client.post("/toggle/1")
    client.post("/clear")
    page = client.get("/").data
    assert b"Done one" not in page and b"Open one" in page


def test_data_persists_in_database(client):
    add(client, "Persistent")
    fresh = app_module.app.test_client()   # new client, same database file
    assert b"Persistent" in fresh.get("/").data


def test_stats_page(client):
    add(client, "One")
    add(client, "Two")
    client.post("/toggle/1")
    page = client.get("/stats")
    assert page.status_code == 200
    assert b"Total tasks" in page.data and b"50%" in page.data


def test_about_page(client):
    assert client.get("/about").status_code == 200
