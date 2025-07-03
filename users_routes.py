from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import SessionLocal
from models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Signup - GET
@router.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "message": None})

# Signup - POST
@router.post("/signup")
def signup(request: Request, username: str = Form(...), password: str = Form(...)):
    db = next(get_db())

    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "message": "Username already exists!"
        })

    # Create new user
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/", status_code=302)

# Login - GET
@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": None})

# Login - POST
@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = next(get_db())
    user = db.query(User).filter(User.username == username, User.password == password).first()

    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Invalid username or password!"
        })

    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": f"Welcome back, {username}!"
    })

