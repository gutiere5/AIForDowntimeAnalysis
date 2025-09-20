from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# In memory storage for items
items = []

# Pydantic model for Item
class Item(BaseModel):
    name: str
    description: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Creating a new item
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    items.append(item)
    return item

# Getting an item by item_id
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

# Updating an item by item_id
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = item
    return items[item_id]

# Deleting an item by item_id
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    deleted_item = items.pop(item_id)
    return deleted_item