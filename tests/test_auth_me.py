from pets_api import app
import json
import uuid

def test_register_with_missing_fields():
    client = app.test_client()
    resp = client.post(
        "/register",
        data=json.dumps({"username": "user_without_password"}),
        content_type="application/json"
    )
    assert resp.status_code == 400

def test_register_login_and_me_ok():
    client = app.test_client()
    username = "user_demo_" + uuid.uuid4().hex[:8]
    password = "123"
    r1 = client.post(
        "/register",
        data=json.dumps({"username": username, "password": password}),
        content_type="application/json",
    )
    assert r1.status_code == 200
    token_register = r1.get_json()["token"]
    assert isinstance(token_register, str)
    r2 = client.post(
        "/login",
        data=json.dumps({"username": username, "password": password}),
        content_type="application/json",
    )
    assert r2.status_code == 200
    token_login = r2.get_json()["token"]
    assert isinstance(token_login, str)
    r3 = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token_login}"}
    )
    assert r3.status_code == 200
    body = r3.get_json()
    assert "id" in body and "username" in body and "role" in body
    assert body["username"] == username

def test_me_without_token():
    client = app.test_client()
    r = client.get("/me")
    assert r.status_code == 403
