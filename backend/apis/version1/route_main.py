from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request
from fastapi.templating import Jinja2Templates

from db.session import get_db
from db.repository.login import get_user
from db.models.users import Users
from core.security import create_access_token
from core.hashing import Hasher

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("general_pages/homepage.html",
                                      {"request": request})


@router.get("/register")
async def registration(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("general_pages/register.html", {"request": request})


@router.post("/register")
async def registration(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")
    user = Users(username=username, email=email, hashed_password=Hasher.get_password_hash(password), is_active=True,
                 is_superuser=False)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return templates.TemplateResponse(
            "general_pages/homepage.html", {"request": request, "msg": "Your register successed"}
        )
    except IntegrityError:
        return templates.TemplateResponse("general_pages/register.html",
                                          {"request": request, "msg": "User already exist"})


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username=username, db=db)
    print(user)
    if not user:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("general_pages/login.html", {"request": request})


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    login_form = await request.form()
    username = login_form.get("username")
    password = login_form.get("password")

    auth = authenticate_user(username, password, db)
    if not auth:
        return templates.TemplateResponse("general_pages/login.html",
                                          {"request": request, "msg": "Invalid user"})
    token = create_access_token(data={"sub": username})
    response = templates.TemplateResponse(
        "general_pages/homepage.html", {"request": request, "msg": "Your login successed"}
    )
    response.set_cookie(key='access_token', value=f"Bearer {token}", httponly=True)
    return response
