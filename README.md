# 4-Tier Mini E-Commerce App (Microservices)

This project is now split into **microservices**:
- **Frontend service** (Nginx) for UI
- **Backend service** (Python API/business logic)
- **Database service** (PostgreSQL)

Features:
- Admin-only product creation
- Users can view, like/save, and add products to cart
- No payment flow yet

## Architecture

1. **Presentation tier**: `frontend/` (served by Nginx)
2. **API tier**: `app/api/routes.py`
3. **Business tier**: `app/services/`
4. **Data tier**: PostgreSQL (`db` service in compose) with repository layer in `app/data/repository.py`

## Run with Docker Compose

```bash
docker compose up --build
```

Open:
- Frontend: `http://localhost:3000/`
- Admin page: `http://localhost:3000/admin.html`

Default admin token: `admin123`.
You can change it in `docker-compose.yml` (`backend.environment.ADMIN_TOKEN`).

## Local test (without Docker)

The automated tests run on SQLite mode for fast local validation:

```bash
python -m pytest -q
```
