import json
from urllib.parse import urlparse


def json_response(status: int, payload: dict | list):
    return status, {"Content-Type": "application/json"}, json.dumps(payload).encode("utf-8")


def parse_json(body: bytes):
    try:
        return json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON") from exc


def is_admin(headers: dict[str, str], admin_token: str):
    supplied = headers.get("X-Admin-Token") or headers.get("x-admin-token")
    return bool(admin_token) and supplied == admin_token


def handle_api_request(method: str, path: str, body: bytes, service, admin_service, headers=None, admin_token=""):
    headers = headers or {}
    parsed = urlparse(path)
    clean_path = parsed.path

    if clean_path == "/api/products" and method == "GET":
        return json_response(200, service.list_products())

    if clean_path == "/api/admin/products" and method == "POST":
        if not is_admin(headers, admin_token):
            return json_response(403, {"error": "Admin access required"})
        try:
            product = admin_service.create_product(parse_json(body))
            return json_response(201, product)
        except ValueError as exc:
            return json_response(400, {"error": str(exc)})

    if clean_path.startswith("/api/products/") and method == "POST":
        parts = clean_path.strip("/").split("/")
        if len(parts) == 4 and parts[3] in {"like", "save"}:
            try:
                product_id = int(parts[2])
                if parts[3] == "like":
                    return json_response(200, service.like_product(product_id))
                return json_response(200, service.save_product(product_id))
            except ValueError:
                return json_response(400, {"error": "Invalid product id"})
            except LookupError as exc:
                return json_response(404, {"error": str(exc)})

    if clean_path == "/api/cart" and method == "GET":
        return json_response(200, service.get_cart())

    if clean_path.startswith("/api/cart/") and method == "POST":
        try:
            product_id = int(clean_path.rsplit("/", 1)[-1])
            return json_response(200, service.add_to_cart(product_id))
        except ValueError:
            return json_response(400, {"error": "Invalid product id"})
        except LookupError as exc:
            return json_response(404, {"error": str(exc)})

    return json_response(404, {"error": "Not found"})
