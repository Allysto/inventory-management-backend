# Inventory Management System - Backend API

A RESTful API for inventory management built with FastAPI and PostgreSQL.

## Features

- ✅ Product Management (CRUD operations)
- ✅ Stock Transaction Recording (IN/OUT)
- ✅ Real-time Analytics Dashboard
- ✅ Automatic Inventory Valuation
- ✅ Low Stock Alerts
- ✅ PostgreSQL Database with SQLAlchemy ORM

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/products` | Create new product |
| GET | `/api/products` | Get all products |
| GET | `/api/products/{id}` | Get product by ID |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |
| POST | `/api/transactions` | Record stock transaction |
| GET | `/api/transactions` | Get all transactions |
| GET | `/api/analytics/summary` | Get inventory analytics |

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/inventory-management-backend.git
cd inventory-management-backend