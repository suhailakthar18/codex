const productsEl = document.getElementById("products");
const cartEl = document.getElementById("cart");

async function api(path, method = "GET", body) {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: "Request failed" }));
    throw new Error(err.error || "Request failed");
  }
  return res.json();
}

function productTemplate(product) {
  return `
    <article class="product">
      <h3>${product.name}</h3>
      <p>${product.description}</p>
      <p><strong>$${Number(product.price).toFixed(2)}</strong></p>
      <p>❤️ ${product.likes} · 💾 ${product.saved}</p>
      <div class="actions">
        <button data-action="like" data-id="${product.id}">Like</button>
        <button data-action="save" data-id="${product.id}">Save</button>
        <button data-action="cart" data-id="${product.id}">Add to Cart</button>
      </div>
    </article>
  `;
}

function cartTemplate(cart) {
  if (!cart.items.length) {
    return "<p>Cart is empty.</p>";
  }
  const lines = cart.items
    .map(
      (item) =>
        `<li>${item.name} × ${item.quantity} = $${Number(item.line_total).toFixed(2)}</li>`
    )
    .join("");
  return `<ul>${lines}</ul><p><strong>Total: $${Number(cart.total).toFixed(2)}</strong></p>`;
}

async function loadProducts() {
  const products = await api("/api/products");
  productsEl.innerHTML = products.map(productTemplate).join("") || "<p>No products yet.</p>";
}

async function loadCart() {
  const cart = await api("/api/cart");
  cartEl.innerHTML = cartTemplate(cart);
}

productsEl.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = button.dataset.id;
  const action = button.dataset.action;

  try {
    if (action === "like") await api(`/api/products/${id}/like`, "POST");
    if (action === "save") await api(`/api/products/${id}/save`, "POST");
    if (action === "cart") await api(`/api/cart/${id}`, "POST");

    await Promise.all([loadProducts(), loadCart()]);
  } catch (error) {
    alert(error.message);
  }
});

Promise.all([loadProducts(), loadCart()]);
