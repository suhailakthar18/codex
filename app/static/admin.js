const form = document.getElementById("admin-product-form");
const statusEl = document.getElementById("admin-status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);

  try {
    const res = await fetch("/api/admin/products", {
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
      throw new Error(payload.error || "Failed to create product");
    }

    statusEl.textContent = `Created product #${payload.id}: ${payload.name}`;
    form.reset();
  } catch (error) {
    statusEl.textContent = error.message;
  }
});
