from pets_api import app
import json
import uuid

def test_cart_add_requires_token():
    client = app.test_client()
    r = client.post(
        "/cart/add",
        data=json.dumps({"product_id": 1, "quantity_of_product": 1}),
        content_type="application/json",
    )
    assert r.status_code == 403

def test_cart_get_ok():
    client = app.test_client()
    username = "cart_user_" + uuid.uuid4().hex[:8]
    password = "123"
    r1 = client.post(
        "/register",
        data=json.dumps({"username": username, "password": password}),
        content_type="application/json",
    )
    assert r1.status_code == 200
    token = r1.get_json()["token"]
    r2 = client.get(
        "/cart",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    data = r2.get_json()
    assert isinstance(data, list) or data is None
