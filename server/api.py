from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil

app = FastAPI()

# Enable CORS for everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Dummy API key (Replace this with a secure key)
API_KEY = "am-4F8Y7JX9LQ2ZMTN3K6VCPWD5G1HABRES"

# Dependency for API key authentication
def api_key_auth(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

# Sample data store
items = [
    {"id": 0, "name": "Spoon", "price": 3.9, "image": "images/0.jpg"},
    {"id": 1, "name": "Fork", "price": 2.7, "image": "images/1.png"}
]

@app.get("/health")


def test_health():
    return {"result": "healthy"}

# GET item by ID (Requires API Key)
@app.get("/{item_id}")
def get_item_by_id(item_id: int, api_key: str = Depends(api_key_auth)):
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# GET all items with pagination (Requires API Key)
@app.get("/")
def get_all_items(page: int = 0, limit: int = 8, api_key: str = Depends(api_key_auth)):
    start_index = page * limit
    end_index = (page + 1) * limit
    return items[start_index:end_index]

@app.get("/{item_id}/image")
def get_image(item_id, api_key: str = Depends(api_key_auth)):
    item_id = int(item_id)
    for item in items:
        if item["id"] == item_id:
            image_path = item["image"]
            return FileResponse(image_path, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Item not found")

# Pydantic model for items
class Item(BaseModel):
    id: int
    name: str
    price: float  # Changed "grade" to "price" for consistency

# POST new item (Requires API Key)
@app.post("/")
def add_item(item: Item, api_key: str = Depends(api_key_auth)):
    global items
    items.append(item.model_dump())
    return {"message": "Item added", "item": item}

@app.post("/{item_id}/image")
def upload_image(item_id, file: UploadFile = File(...), api_key: str = Depends(api_key_auth)):
    item_id = int(item_id)
    global items
    file_extension = os.path.splitext(file.filename)[1]
    for index, item in enumerate(items):
        if item["id"] == item_id:
            with open(f"images/{item_id}{file_extension}", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            items[index]["image"] = f"images/{item_id}{file_extension}"
            return {"message": "Image added"}
    raise HTTPException(status_code=404, detail="Item not found")

# PUT (update full item)
@app.put("/{item_id}")
def change_item(item_id: int, changed_item: Item, api_key: str = Depends(api_key_auth)):
    global items
    for index, item in enumerate(items):
        if item["id"] == item_id:
            items[index] = changed_item.model_dump()
            return {"message": "Item updated", "item": changed_item}
    raise HTTPException(status_code=404, detail="Item not found")

# PATCH (update item name)
@app.patch("/{item_id}")
def update_item_name(item_id: int, item_name: str, api_key: str = Depends(api_key_auth)):
    global items
    for item in items:
        if item["id"] == item_id:
            item["name"] = item_name
            return {"message": "Item name updated", "item": item}
    raise HTTPException(status_code=404, detail="Item not found")

# DELETE item
@app.delete("/{item_id}")
def delete_item(item_id: int, api_key: str = Depends(api_key_auth)):
    global items
    for item in items:
        if item["id"] == item_id:
            items.remove(item)
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")
