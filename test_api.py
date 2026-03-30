from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Your Neon database URL
DATABASE_URL = "postgresql://neondb_owner:npg_0vcpmQGA4jox@ep-steep-mouse-am4yvwe6-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Simple Product Model
class SimpleProduct(Base):
    __tablename__ = "simple_products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

# Create table
Base.metadata.create_all(bind=engine)

# Pydantic Models
class ProductCreate(BaseModel):
    sku: str
    name: str
    price: float
    stock: int = 0

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    price: float
    stock: int

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = SimpleProduct(
        sku=product.sku,
        name=product.name,
        price=product.price,
        stock=product.stock
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/api/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(SimpleProduct).all()

@app.get("/")
def root():
    return {"message": "API is working!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)