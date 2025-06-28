from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")
USERS_FILE = "users.json"

# Load users from file
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Save users to file
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# -------------------------------
# Signup - GET
# -------------------------------
@router.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "message": None})

# -------------------------------
# Signup - POST
# -------------------------------
@router.post("/signup")
def signup(request: Request, username: str = Form(...), password: str = Form(...)):
    users = load_users()

    if any(u["username"] == username for u in users):
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "message": "Username already exists!"
        })

    users.append({"username": username, "password": password})
    save_users(users)

    return templates.TemplateResponse("signup.html", {
        "request": request,
        "message": "Account created successfully!"
    })

# -------------------------------
# Login - GET
# -------------------------------
@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# -------------------------------
# Login - POST
# -------------------------------
@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    users = load_users()
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)

    if user:
        return RedirectResponse(url="/", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid credentials"
        })
