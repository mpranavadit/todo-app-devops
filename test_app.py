from app import app

def test_home_page():
    client = app.test_client()
    assert client.get("/").status_code == 200

def test_health():
    client = app.test_client()
    assert client.get("/health").get_json()["status"] == "ok"

def test_add_task():
    client = app.test_client()
    client.post("/add", data={"task": "Buy milk"})
    assert b"Buy milk" in client.get("/").data