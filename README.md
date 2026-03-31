# Inventory Management System - Backend API

A RESTful API for inventory management built with FastAPI and PostgreSQL. This backend powers a complete inventory system with real-time analytics, stock tracking, and transaction management.

## Live Demo

- **API Base URL**: https://inventory-management-backend-2-2h44.onrender.com
- **API Documentation**: https://inventory-management-backend-2-2h44.onrender.com/docs
- **Frontend Demo**: https://inventory-management-frontend-ivory.vercel.app

## ✨ Features

- ✅ **Product Management** - Create, read, update, and delete products
- ✅ **Stock Transactions** - Record inventory IN/OUT movements
- ✅ **Real-time Analytics** - Automatic inventory valuation and low stock alerts
- ✅ **Transaction History** - Complete audit trail of all stock movements
- ✅ **RESTful API** - Clean, well-documented endpoints
- ✅ **PostgreSQL Database** - Reliable data persistence with SQLAlchemy ORM

## 📊 API Endpoints

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
| GET | `/api/analytics/top-products` | Get most valuable products |

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database (hosted on Neon.tech)
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Render** - Cloud deployment

## 📈 Sample Data

The system currently manages:
- **3+ products** with total inventory value of **$43,998.90**
- **Transaction tracking** for all stock movements
- **Real-time analytics** for inventory valuation

## 🏃‍♂️ Local Development

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Allysto/inventory-management-backend.git
cd inventory-management-backend
