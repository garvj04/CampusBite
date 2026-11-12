# CampusBite

A full-stack restaurant ordering and delivery platform built with React, FastAPI, SQLAlchemy, JWT authentication, and Docker.

## Technology Stack
- Frontend: React, JavaScript ES6+, React Hooks, React Router, Axios, Vite
- Backend: Python, FastAPI, Pydantic
- Database and ORM: SQLite, PostgreSQL support, SQLAlchemy
- Authentication: JWT and bcrypt password hashing
- Deployment: Docker, Docker Compose, Nginx

## Main Features
- Registration, login, JWT authentication, and role-based access
- Restaurant and menu management
- Customer cart, orders, and order history
- Order status management, filtering, and pagination
- Delivery partner assignment and delivery updates
- Restaurant statistics, reviews, and ratings
- Dummy payments, payment ledger, cancellations, and refunds
- Admin dashboard and reminder logs
- Background stale-order reminders
- OpenAI-powered customer order insights with fallback
- Protected React routes and responsive dashboards

## User Roles
- CUSTOMER: browse restaurants, order food, pay, view orders, and review restaurants
- RESTAURANT_OWNER: manage menus, view statistics, and process orders
- DELIVERY_PARTNER: view eligible deliveries and update delivery status
- ADMIN: manage platform-level operations, reminders, and refunds

## Order Lifecycle
`PLACED -> ACCEPTED -> PREPARING -> READY -> ASSIGNED -> OUT_FOR_DELIVERY -> DELIVERED`

Orders may also be cancelled or refunded according to backend rules.

## Main Database Tables
Users, Restaurants, Menu Items, Orders, Order Items, Reviews, Payment Ledger, Admin Reminder Logs.

## Project Structure
```text
CampusBite/
  backend/app/core/       Configuration and security
  backend/app/database/   Database connection
  backend/app/models/     SQLAlchemy models
  backend/app/routers/    FastAPI endpoints
  backend/app/schemas/    Pydantic schemas
  backend/app/services/   Application services
  backend/app/tasks/      Background tasks
  frontend/src/components/ Shared components
  frontend/src/context/    Authentication context
  frontend/src/pages/      React pages and dashboards
  frontend/src/services/   API client
  docker-compose.yml
  README.md
```\n
## Docker Setup

Requirements: Docker and Docker Compose.

1. Copy the root environment example:
   `cp .env.example .env`
2. Edit `.env` and set a secure `SECRET_KEY`.
3. Add an `OPENAI_API_KEY` if OpenAI insights are required.
4. Build and start:
   `docker compose up -d --build`
5. Check containers:
   `docker compose ps`
6. View logs:
   `docker compose logs -f`
7. Stop:
   `docker compose down`

Docker Compose stores database data in the persistent `campusbite_data` volume. To delete the database volume as well as stop the containers, run `docker compose down -v`. This permanently deletes its stored data.

## Application URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:8080 |
| Backend API | http://localhost:8001 |
| Swagger documentation | http://localhost:8001/docs |
| ReDoc documentation | http://localhost:8001/redoc |
| Swagger through frontend proxy | http://localhost:8080/api/docs |

In GitHub Codespaces, open the forwarded ports 8080 and 8001.

## Local Development

### Backend

From the repository root:

`cd backend`

Create and activate a virtual environment:

`python -m venv .venv`

`source .venv/bin/activate`

Install dependencies:

`pip install -r requirements.txt`

Configure `backend/.env` using `backend/.env.example`, then start:

`uvicorn app.main:app --reload --port 8000`

### Frontend

Open another terminal:

`cd frontend`

`npm install`

`npm run dev`

Vite displays the development URL. Its `/api` proxy forwards requests to the backend at `http://127.0.0.1:8000`.

Frontend checks:

- Production build: `npm run build`
- Lint: `npm run lint`

## Important API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/users/` | Register a customer |
| POST | `/auth/login` | Log in |
| GET, POST | `/restaurants/` | List or create restaurants |
| GET | `/restaurants/{id}/statistics` | Restaurant statistics |
| GET, POST | `/menu-items/` | List or create menu items |
| POST | `/orders/` | Place an order |
| GET | `/orders/` | List and filter orders |
| PATCH | `/orders/{id}/status` | Update order status |
| PATCH | `/orders/{id}/assign-delivery` | Assign delivery partner |
| POST | `/order-items/` | Add order item |
| POST | `/reviews/` | Submit a review |
| POST | `/payments/` | Create dummy payment |
| PATCH | `/payments/{id}/refund` | Refund an eligible payment |
| GET, POST | `/admin-reminder-logs/` | Administrator reminder logs |
| GET | `/order-insight/` | Customer order insights |

Protected endpoints require a JWT access token in the `Authorization: Bearer YOUR_ACCESS_TOKEN` header. Order listing supports status, restaurant ID, page, and page-size parameters, subject to role-based access.

## Security and Application Notes

- Passwords are hashed before storage.
- JWT authentication and backend role checks protect restricted operations.
- Customers, restaurant owners, delivery partners, and administrators have different permissions.
- A background task checks for orders still in `PLACED` status and creates pending administrator reminders every 60 seconds.
- The backend middleware logs requests and adds an `X-Process-Time` response header.
- The payment workflow is a dummy implementation, not a real payment gateway.
- Eligible refunds update both the payment record and associated order.
- OpenAI insights use customer order history. A fallback response is available when a usable API key is unavailable.
- Set secure environment variables before public deployment.

## Verification

Development checks completed include backend Python compilation, FastAPI route loading, API and authentication tests, Docker builds, container HTTP checks, frontend production build, and frontend lint.

The frontend lint check completed with zero errors and some warnings.
