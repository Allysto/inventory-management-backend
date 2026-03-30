from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, func
from sqlalchemy.orm import declarative_base
import psycopg2

# Your database URL
DATABASE_URL = "postgresql://neondb_owner:npg_0vcpmQGA4jox@ep-steep-mouse-am4yvwe6-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Create engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define Product table
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

# Define Transaction table
class Transaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    transaction_type = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    transaction_date = Column(DateTime, server_default=func.now())

# Create tables
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

# Verify
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables in database: {tables}")