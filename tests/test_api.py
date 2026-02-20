import json

from app.api.routes import handle_api_request
from app.app import create_services


def call(service, admin_service, method, path, payload=None, headers=None, admin_token="admin123"):
    body = json.dumps(payload).encode("utf-8") if payload is not None else b""
    return handle_api_request(method, path, body, service, admin_service, headers or {}, admin_token)


def test_product_flow_admin_only_create(tmp_path):
    service, admin_service = create_services(str(tmp_path / "test.db"))

    forbidden_status, _, _ = call(
        service,
        admin_service,
        "POST",
        "/api/admin/products",
        {"name": "Phone", "description": "Budget phone", "price": 99.99},
    )
    assert forbidden_status == 403

    status, _, body = call(
        service,
        admin_service,
        "POST",
        "/api/admin/products",
        {"name": "Phone", "description": "Budget phone", "price": 99.99},
        {"X-Admin-Token": "admin123"},
    )
    assert status == 201
    product = json.loads(body)
    product_id = product["id"]

    like_status, _, _ = call(service, admin_service, "POST", f"/api/products/{product_id}/like")
    save_status, _, _ = call(service, admin_service, "POST", f"/api/products/{product_id}/save")
    assert like_status == 200
    assert save_status == 200

    cart_status, _, cart_body = call(service, admin_service, "POST", f"/api/cart/{product_id}")
    assert cart_status == 200
    cart = json.loads(cart_body)
    assert len(cart["items"]) == 1

    list_status, _, list_body = call(service, admin_service, "GET", "/api/products")
    assert list_status == 200
    products = json.loads(list_body)
    assert products[0]["likes"] == 1
    assert products[0]["saved"] == 1
