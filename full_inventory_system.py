from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Your Neon database URL
DATABASE_URL = "postgresql://neondb_owner:npg_0vcpmQGA4jox@ep-steep-mouse-am4yvwe6-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Product(Base):
    __tablename__ = "inventory_products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Transaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    transaction_type = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    transaction_date = Column(DateTime, server_default=func.now())

# Pydantic Schemas
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: str
    price: float
    stock: int = 0
    reorder_level: int = 10

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    category: str
    price: float
    stock: int
    reorder_level: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class TransactionCreate(BaseModel):
    product_id: int
    transaction_type: str
    quantity: int
    unit_price: float
    notes: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    product_id: int
    transaction_type: str
    quantity: int
    unit_price: float
    notes: Optional[str] = None
    transaction_date: datetime

# Create FastAPI app
app = FastAPI(title="Inventory Management System", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints

@app.post("/api/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        db_product = Product(
            sku=product.sku,
            name=product.name,
            description=product.description,
            category=product.category,
            price=product.price,
            stock=product.stock,
            reorder_level=product.reorder_level
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/products", response_model=List[ProductResponse])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.sku = product.sku
    db_product.name = product.name
    db_product.description = product.description
    db_product.category = product.category
    db_product.price = product.price
    db_product.stock = product.stock
    db_product.reorder_level = product.reorder_level
    
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

@app.post("/api/transactions")
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    # Check if product exists
    product = db.query(Product).filter(Product.id == transaction.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update stock
    if transaction.transaction_type.upper() == "IN":
        product.stock += transaction.quantity
    elif transaction.transaction_type.upper() == "OUT":
        if product.stock < transaction.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {product.stock}")
        product.stock -= transaction.quantity
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type. Use 'IN' or 'OUT'")
    
    # Record transaction
    db_transaction = Transaction(
        product_id=transaction.product_id,
        transaction_type=transaction.transaction_type.upper(),
        quantity=transaction.quantity,
        unit_price=transaction.unit_price,
        notes=transaction.notes
    )
    db.add(db_transaction)
    db.commit()
    
    return {
        "message": "Transaction recorded successfully",
        "product_id": product.id,
        "product_name": product.name,
        "new_stock": product.stock,
        "transaction_type": transaction.transaction_type,
        "quantity": transaction.quantity
    }

@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions

@app.get("/api/transactions/product/{product_id}", response_model=List[TransactionResponse])
def get_product_transactions(product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.product_id == product_id).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions

@app.get("/api/analytics/summary")
def get_summary(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    total_products = len(products)
    total_value = sum(p.price * p.stock for p in products)
    low_stock = [p for p in products if p.stock <= p.reorder_level]
    
    # Get recent transactions
    recent_transactions = db.query(Transaction).order_by(Transaction.transaction_date.desc()).limit(10).all()
    
    return {
        "total_products": total_products,
        "total_inventory_value": total_value,
        "low_stock_count": len(low_stock),
        "low_stock_items": [
            {
                "product_id": p.id,
                "product_name": p.name,
                "current_stock": p.stock,
                "reorder_level": p.reorder_level
            } for p in low_stock
        ],
        "recent_transactions": [
            {
                "id": t.id,
                "product_id": t.product_id,
                "type": t.transaction_type,
                "quantity": t.quantity,
                "date": t.transaction_date
            } for t in recent_transactions
        ]
    }

@app.get("/api/analytics/top-products")
def get_top_products(limit: int = 5, db: Session = Depends(get_db)):
    # Get products with highest inventory value
    products = db.query(Product).all()
    sorted_products = sorted(products, key=lambda x: x.price * x.stock, reverse=True)[:limit]
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "stock": p.stock,
            "price": p.price,
            "value": p.price * p.stock
        }
        for p in sorted_products
    ]

@app.get("/")
def root():
    return {
        "message": "Inventory Management System API",
        "version": "1.0.0",
        "endpoints": [
            "/api/products",
            "/api/transactions",
            "/api/analytics/summary",
            "/api/analytics/top-products"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)