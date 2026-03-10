from smtpd import Options
from typing import Optional
from fastapi import FastAPI, HTTPException

sample_product_1 = {
    "product_id": 123,
    "name": "Smartphone",
    "category": "Electronics",
    "price": 599.99
}

sample_product_2 = {
    "product_id": 456,
    "name": "Phone Case",
    "category": "Accessories",
    "price": 19.99
}

sample_product_3 = {
    "product_id": 789,
    "name": "Iphone",
    "category": "Electronics",
    "price": 1299.99
}

sample_product_4 = {
    "product_id": 101,
    "name": "Headphones",
    "category": "Accessories",
    "price": 99.99
}

sample_product_5 = {
    "product_id": 202,
    "name": "Smartwatch",
    "category": "Electronics",
    "price": 299.99
}

sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]
app = FastAPI()

@app.get("/products/search")
async def search_products(keyword: str ,category: Optional[str] = None, limit: int = 10):
    list = []

    for product in sample_products:
      if keyword.lower() in product.get("name").lower() and product.get("category").lower() == category.lower():
        list.append(product)

    return list[:limit]
@app.get("/products/{product_id}")
async def read_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
        else:
            raise HTTPException(status_code=404, detail="Product not found")

