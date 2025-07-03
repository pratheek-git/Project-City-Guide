from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Query
from sqlalchemy.orm import Session
from models import Spot
from db import SessionLocal, engine, Base
from users_routes import router as user_router
import random

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_router)
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    db = next(get_db())
    new_spot = Spot(name=name, city=city, category=category, rating=rating, description=description)
    db.add(new_spot)
    db.commit()
    return RedirectResponse(url="/view-spots", status_code=302)

@app.get("/view-spots", response_class=HTMLResponse)
def view_spots(request: Request, q: str = Query("", description="Search by city or category")):
    db = next(get_db())
    if q:
        spots = db.query(Spot).filter(
            (Spot.city.ilike(f"%{q}%")) | (Spot.category.ilike(f"%{q}%"))
        ).all()
    else:
        spots = db.query(Spot).all()
    return templates.TemplateResponse("index.html", {"request": request, "spots": spots})

@app.get("/spots")
def list_spots(city: str = None, category: str = None):
    db = next(get_db())
    query = db.query(Spot)
    if city:
        query = query.filter(Spot.city.ilike(city))
    if category:
        query = query.filter(Spot.category.ilike(category))
    return query.all()

@app.get("/spot/{id}", response_class=HTMLResponse)
def view_spot_detail(request: Request, id: int):
    db = next(get_db())
    spot = db.query(Spot).filter(Spot.id == id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    return templates.TemplateResponse("spot_detail.html", {"request": request, "spot": spot})

@app.get("/edit-spot-form/{id}", response_class=HTMLResponse)
def edit_spot_form(request: Request, id: int):
    db = next(get_db())
    spot = db.query(Spot).filter(Spot.id == id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    return templates.TemplateResponse("edit_spot.html", {"request": request, "spot": spot})

@app.post("/edit-spot/{id}")
def edit_spot(id: int, name: str = Form(...), city: str = Form(...),
              category: str = Form(...), rating: float = Form(...), description: str = Form("")):
    db = next(get_db())
    spot = db.query(Spot).filter(Spot.id == id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    spot.name = name
    spot.city = city
    spot.category = category
    spot.rating = rating
    spot.description = description
    db.commit()
    return RedirectResponse(url="/view-spots", status_code=302)

@app.get("/delete-spot/{id}")
def delete_spot_from_ui(id: int):
    db = next(get_db())
    spot = db.query(Spot).filter(Spot.id == id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    db.delete(spot)
    db.commit()
    return RedirectResponse(url="/view-spots", status_code=302)

@app.get("/spot-of-the-day", response_class=HTMLResponse)
def spot_of_the_day(request: Request):
    db = next(get_db())
    spots = db.query(Spot).all()
    if not spots:
        raise HTTPException(status_code=404, detail="No spots available")
    selected_spot = random.choice(spots)
    return templates.TemplateResponse("spot_of_the_day.html", {
        "request": request,
        "spot": selected_spot
    })
