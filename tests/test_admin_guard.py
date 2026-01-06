from pets_api import app
import json
import uuid

def test_admin_modify_user_with_client_token_returns_403():
    client = app.test_client()
    username = "client_user_" + uuid.uuid4().hex[:8]
    password = "123"
    r1 = client.post(
        "/register",
        data=json.dumps({"username": username, "password": password}),
        content_type="application/json",
    )
    assert r1.status_code == 200
    client_token = r1.get_json()["token"]
    r2 = client.post(
        "/user/modification",
        data=json.dumps({"user_id": 999, "column": "username", "new_value": "x"}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r2.status_code == 403

def test_admin_modify_user_without_token_returns_403():
    client = app.test_client()
    r = client.post(
        "/user/modification",
        data=json.dumps({"user_id": 1, "column": "username", "new_value": "X"}),
        content_type="application/json",
    )
    assert r.status_code == 403
