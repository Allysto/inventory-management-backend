from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Your Neon database URL
DATABASE_URL = "postgresql://neondb_owner:npg_0vcpmQGA4jox@ep-steep-mouse-am4yvwe6-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    unit_price = Column(Float, nullable=False)
    current_stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    transaction_type = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    transaction_date = Column(DateTime, server_default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class ProductCreate(BaseModel):
    sku: str
    product_name: str
    description: Optional[str] = None
    category: str
    unit_price: float
    current_stock: int = 0
    reorder_level: int = 10

class ProductResponse(BaseModel):
    id: int
    sku: str
    product_name: str
    description: Optional[str] = None
    category: str
    unit_price: float
    current_stock: int
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
    db_product = Product(
        sku=product.sku,
        product_name=product.product_name,
        description=product.description,
        category=product.category,
        unit_price=product.unit_price,
        current_stock=product.current_stock,
        reorder_level=product.reorder_level
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

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
    db_product.product_name = product.product_name
    db_product.description = product.description
    db_product.category = product.category
    db_product.unit_price = product.unit_price
    db_product.current_stock = product.current_stock
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
        product.current_stock += transaction.quantity
    elif transaction.transaction_type.upper() == "OUT":
        if product.current_stock < transaction.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        product.current_stock -= transaction.quantity
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
        "new_stock": product.current_stock
    }

@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions

@app.get("/api/analytics/summary")
def get_summary(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    total_products = len(products)
    total_value = sum(p.current_stock * p.unit_price for p in products)
    low_stock = [p for p in products if p.current_stock <= p.reorder_level]
    
    return {
        "total_products": total_products,
        "total_inventory_value": total_value,
        "low_stock_count": len(low_stock),
        "low_stock_items": [
            {
                "product_id": p.id,
                "product_name": p.product_name,
                "current_stock": p.current_stock,
                "reorder_level": p.reorder_level
            } for p in low_stock
        ]
    }

@app.get("/")
def root():
    return {"message": "Inventory Management System API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)