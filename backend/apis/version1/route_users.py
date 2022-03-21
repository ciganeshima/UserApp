from typing import List
from distutils.util import strtobool

import jwt
from fastapi import APIRouter, Request, responses, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from schemas.users import ShowUser, UserUpdate

from db.session import get_db
from db.repository.users import retrieve_user, retrieve_user_raw, list_users_sorted, update_user_by_id, delete_user_by_id
from db.models.users import Users
from core.config import settings
from core.hashing import Hasher
from core.security import get_user_from_token

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/", response_model=ShowUser)
async def create_user(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")
    is_superuser = strtobool(form.get("is_superuser"))

    token = request.cookies.get("access_token")
    if not token:
        return templates.TemplateResponse(
            "general_pages/user_create.html", {"request": request, "msg": "No access token, login first please"}
        )
    user_from_token = get_user_from_token(token)
    if user_from_token is None:
        return templates.TemplateResponse(
            "general_pages/user_create.html",
            {"request": request, "msg": "No such user from this token, relogin please"}
        )
    user_from_db = db.query(Users).filter(Users.username == user_from_token).first()
    if user_from_db is None:
        return templates.TemplateResponse(
            "general_pages/user_create.html",
            {"request": request, "msg": "No such user in db with this token, relogin please"}
        )
    if not user_from_db.is_superuser:
        return templates.TemplateResponse(
            "general_pages/user_create.html",
            {"request": request, "msg": "You don't have permission to this action"}
        )
    add_user = Users(
        username=username,
        email=email,
        hashed_password=Hasher.get_password_hash(password),
        is_superuser=is_superuser
    )
    db.add(add_user)
    db.commit()
    db.refresh(add_user)
    return responses.RedirectResponse(
        f"/users/get/{add_user.id}/", status_code=status.HTTP_302_FOUND
    )


@router.get("/")
async def create_user(request: Request):
    return templates.TemplateResponse("general_pages/user_create.html", {'request': request})


@router.get("/get/{id}", response_model=ShowUser)
async def read_user(request: Request, id: int):
    user = retrieve_user_raw(id=id)
    return templates.TemplateResponse("general_pages/user_detail.html", {'request': request, 'user': user})


@router.get("/all", response_model=List[ShowUser])
async def read_users(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get('access_token')
    if not token:
        return templates.TemplateResponse("general_pages/users.html",
                                          {"request": request, "msg": "You have to login"})
    users = list_users_sorted(db=db)
    return templates.TemplateResponse("general_pages/users.html", {"request": request, "users": users})


@router.put("/update/{id}")
async def update_user(request: Request, id: int, user: UserUpdate, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return {"message": "No access token, login first please"}
    user_from_token = get_user_from_token(token)
    if user_from_token is None:
        return {"message": "No such user from this token, relogin please"}

    user_from_db = db.query(Users).filter(Users.username == user_from_token).first()
    if user_from_db is None:
        return {"message": "No such user in db with this token, relogin please"}

    if not user_from_db.is_superuser:
        return {"message": "You don't have permission to this action"}
    user.is_superuser = strtobool(user.is_superuser)
    message = update_user_by_id(id=id, user=user, db=db)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} not found")
    return {"message": "Successfully updated data."}


@router.get("/update/{id}")
async def update_item(id: int, request: Request, db: Session = Depends(get_db)):
    user = retrieve_user(id=id, db=db)
    return templates.TemplateResponse(
        "general_pages/user_update.html", {"request": request, "user": user}
    )


@router.get("/update_delete/")
async def show_items_to_delete(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if token is None:
        return templates.TemplateResponse(
            "general_pages/user_update_delete.html", {"request": request, "msg": "Authorization required"}
        )
    user_from_token = get_user_from_token(token)
    if user_from_token is None:
        return templates.TemplateResponse(
            "general_pages/user_update_delete.html", {"request": request, "msg": "No such user from this token, relogin please"}
        )

    user_from_db = db.query(Users).filter(Users.username == user_from_token).first()
    if user_from_db is None:
        return templates.TemplateResponse(
            "general_pages/user_update_delete.html", {"request": request, "msg": "No such user in db with this token, relogin please"}
        )

    if not user_from_db.is_superuser:
        return templates.TemplateResponse(
            "general_pages/user_update_delete.html", {"request": request, "msg": "You don't have permission to this action"}
        )

    users = list_users_sorted(db=db)
    print(users)
    return templates.TemplateResponse(
        "general_pages/user_update_delete.html", {"request": request, "users": users}
    )


@router.delete("/delete/{id}")
async def delete_user(request: Request, id: int, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return templates.TemplateResponse(
            "general_pages/user_create.html", {"request": request, "msg": "No access token, login first please"}
        )
    user_from_token = get_user_from_token(token)
    if user_from_token is None:
        return {"message": "No such user from this token, relogin please"}
    user_from_db = db.query(Users).filter(Users.username == user_from_token).first()
    if user_from_db is None:
        return {"message": "No such user in db with this token, relogin please"}

    if not user_from_db.is_superuser:
        return {"message": "You don't have permission to this action"}

    message = delete_user_by_id(id=id, db=db)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} not found")
    return {"message": "Successfully deleted."}
