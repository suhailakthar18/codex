class AdminCatalogService:
    def __init__(self, repository):
        self.repository = repository

    def create_product(self, payload: dict):
        name = str(payload.get("name", "")).strip()
        description = str(payload.get("description", "")).strip()
        try:
            price = float(payload.get("price", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("Price must be a number") from exc

        if not name:
            raise ValueError("Name is required")
        if not description:
            raise ValueError("Description is required")
        if price < 0:
            raise ValueError("Price must be non-negative")

        return self.repository.add_product(name, description, price)
