from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Product(BaseModel):
    sku: str
    name: str
    price: float

@app.post("/api/products")
def create_product(product: Product):
    return {"message": f"Product {product.name} created", "data": product}

@app.get("/")
def root():
    return {"message": "API is working!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)