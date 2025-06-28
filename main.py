from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi import Request, Query
from fastapi.responses import HTMLResponse

from pydantic import BaseModel
from typing import Optional
from users_routes import router as user_router
import json, os

app = FastAPI()
app.include_router(user_router)
templates = Jinja2Templates(directory="templates")




DATA_FILE = "data.json"

def load_spots():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_spots(spots):
    with open(DATA_FILE, "w") as f:
        json.dump(spots, f, indent=4)

spots = load_spots()
current_id = max([s["id"] for s in spots], default=0) + 1

class Spot(BaseModel):
    name: str
    city: str
    category: str
    rating: float
    description: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/add-spot-form", response_class=HTMLResponse)
def show_add_form(request: Request):
    return templates.TemplateResponse("add_spot.html", {"request": request})

@app.post("/add-spot")
def handle_add_form(
    request: Request,
    name: str = Form(...),
    city: str = Form(...),
    category: str = Form(...),
    rating: float = Form(...),
    description: str = Form("")
):
    global current_id
    new_spot = {
        "id": current_id,
        "name": name,
        "city": city,
        "category": category,
        "rating": rating,
        "description": description
    }
    spots.append(new_spot)
    current_id += 1
    save_spots(spots)
    return RedirectResponse(url="/view-spots", status_code=302)




@app.get("/view-spots", response_class=HTMLResponse)
def view_spots(request: Request, q: str = Query("", description="Search by city or category")):
    if q:
        filtered_spots = [s for s in spots if q.lower() in s["city"].lower() or q.lower() in s["category"].lower()]
    else:
        filtered_spots = spots

    return templates.TemplateResponse("index.html", {"request": request, "spots": filtered_spots})


@app.get("/spots")
def list_spots(city: Optional[str] = None, category: Optional[str] = None):
    filtered = spots
    if city:
        filtered = [s for s in filtered if s["city"].lower() == city.lower()]
    if category:
        filtered = [s for s in filtered if s["category"].lower() == category.lower()]
    return filtered

@app.get("/spot/{id}", response_class=HTMLResponse)
def view_spot_detail(request: Request, id: int):
    for s in spots:
        if s["id"] == id:
            return templates.TemplateResponse("spot_detail.html", {"request": request, "spot": s})
    raise HTTPException(status_code=404, detail="Spot not found")

@app.get("/edit-spot-form/{id}", response_class=HTMLResponse)
def edit_spot_form(request: Request, id: int):
    for spot in spots:
        if spot["id"] == id:
            return templates.TemplateResponse("edit_spot.html", {"request": request, "spot": spot})
    raise HTTPException(status_code=404, detail="Spot not found")

@app.post("/edit-spot/{id}")
def edit_spot(id: int, name: str = Form(...), city: str = Form(...),
              category: str = Form(...), rating: float = Form(...), description: str = Form("")):
    for spot in spots:
        if spot["id"] == id:
            spot["name"] = name
            spot["city"] = city
            spot["category"] = category
            spot["rating"] = rating
            spot["description"] = description
            save_spots(spots)
            return RedirectResponse(url="/view-spots", status_code=302)
    raise HTTPException(status_code=404, detail="Spot not found")

@app.get("/delete-spot/{id}")
def delete_spot_from_ui(id: int):
    global spots
    before = len(spots)
    spots = [s for s in spots if s["id"] != id]
    if len(spots) == before:
        raise HTTPException(status_code=404, detail="Spot not found")
    save_spots(spots)
    return RedirectResponse(url="/view-spots", status_code=302)
