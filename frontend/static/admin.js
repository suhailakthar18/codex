const API_BASE = window.__API_BASE__ || "";
const form = document.getElementById("admin-product-form");
const statusEl = document.getElementById("admin-status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);

  const res = await fetch(`${API_BASE}/api/admin/products`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Token": data.get("token"),
    },
    body: JSON.stringify({
      name: data.get("name"),
      description: data.get("description"),
      price: data.get("price"),
    }),
  });

  const payload = await res.json();
  if (!res.ok) {
    statusEl.textContent = payload.error || "Failed to create product";
    return;
  }

  statusEl.textContent = `Created product #${payload.id}: ${payload.name}`;
  form.reset();
});
