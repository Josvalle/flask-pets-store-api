from pets_api import app
import json
import uuid

def test_products_list_ok():
    client = app.test_client()
    resp = client.get("/products/list")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)

def test_products_new_product_requires_admin():
    client = app.test_client()
    username = "client_for_products_" + uuid.uuid4().hex[:8]
    password = "123"
    r1 = client.post(
        "/register",
        data=json.dumps({"username": username, "password": password}),
        content_type="application/json",
    )
    assert r1.status_code == 200
    client_token = r1.get_json()["token"]
    payload = {"name": "Ball", "price": 1000, "entry_date": "08/08/2025", "quantity": 10}
    r2 = client.post(
        "/products/new_product",
        data=json.dumps(payload),
        content_type="application/json",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert r2.status_code == 403
