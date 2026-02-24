# 4-Tier Mini E-Commerce App (Microservices)

This project is split into **microservices**:
- **Frontend service** (Nginx) for UI
- **Backend service** (Python API/business logic)
- **Database service** (PostgreSQL)

Features:
- Admin-only product creation
- Users can view, like/save, and add products to cart
- No payment flow yet

## Quick start (Docker)

```bash
docker compose up --build
```

Open:
- Frontend: `http://localhost:3000/`
- Admin page: `http://localhost:3000/admin.html`

Default admin token: `admin123`.
You can change it in `docker-compose.yml` (`backend.environment.ADMIN_TOKEN`).

## Local backend run (without Docker)

```bash
python -m app.app
```

Then open `http://localhost:5000/`.

> Note: If `DB_ENGINE=postgres` is set but Postgres/driver is unavailable, the app automatically falls back to SQLite so the server still starts locally.

## Local test

```bash
python -m pytest -q
```


If you get `Admin access required`, open the admin page and enter the token.
Default is `admin123` unless you changed `ADMIN_TOKEN`.
