class CatalogService:
    def __init__(self, repository):
        self.repository = repository

    def list_products(self):
        return self.repository.list_products()

    def like_product(self, product_id: int):
        product = self.repository.change_metric(product_id, "likes")
        if not product:
            raise LookupError("Product not found")
        return product

    def save_product(self, product_id: int):
        product = self.repository.change_metric(product_id, "saved")
        if not product:
            raise LookupError("Product not found")
        return product

    def add_to_cart(self, product_id: int):
        cart = self.repository.add_to_cart(product_id)
        if cart is None:
            raise LookupError("Product not found")
        return cart

    def get_cart(self):
        return self.repository.get_cart()
