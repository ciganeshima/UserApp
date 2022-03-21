from typing import List

import jwt
from fastapi import APIRouter, Request, responses, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from schemas.users import ShowUser, UserUpdate

from db.session import get_db
from db.repository.users import retreive_user, list_users_sorted, update_user_by_id, delete_user_by_id
from db.models.users import Users
from core.config import settings
from core.hashing import Hasher

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post("/", response_model=ShowUser)
async def create_user(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    email = form.get("email")
    password = form.get("password")

    token = request.cookies.get("access_token")
    if not token:
        return templates.TemplateResponse(
            "general_pages/user_create.html", {"request": request, "msg": "Authorize required"}
        )
    scheme, _, param = token.partition(" ")
    payload = jwt.decode(param, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    user = payload.get("sub")
    if user is None:
        return templates.TemplateResponse(
            "create_item.html", {"request": request, "msg": "Authorize required"}
        )
    else:
        user = db.query(Users).filter(Users.username == user).first()
        if user is None:
            return templates.TemplateResponse(
                "create_item.html", {"request": request, "msg": "Authorize required"}
            )
        else:
            add_user = Users(
                username=username,
                email=email,
                hashed_password=Hasher.get_password_hash(password),
            )
            db.add(add_user)
            db.commit()
            db.refresh(add_user)
            return responses.RedirectResponse(
                f"/users/get/{add_user.id}/", status_code=status.HTTP_302_FOUND
            )


@router.get("/")
def create_user(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("general_pages/user_create.html", {'request': request})


@router.get("/get/{id}", response_model=ShowUser)
def read_user(request: Request, id: int, db: Session = Depends(get_db)):
    user = retreive_user(id=id, db=db)
    return templates.TemplateResponse("general_pages/user_detail.html", {'request': request, 'user': user})


@router.get("/all", response_model=List[ShowUser])
def read_users(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get('access_token')
    if not token:
        return templates.TemplateResponse("general_pages/users.html",
                                          {"request": request, "msg": "You have to login"})
    users = list_users_sorted(db=db)
    return templates.TemplateResponse("general_pages/users.html", {"request": request, "users": users})


@router.put("/update/{id}")
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    message = update_user_by_id(id=id, user=user, db=db)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} not found")
    return {"message": "Successfully updated data."}


@router.get("/update/{id}")
def update_item(id: int, request: Request, db: Session = Depends(get_db)):
    user = retreive_user(id=id, db=db)
    return templates.TemplateResponse(
        "general_pages/user_update.html", {"request": request, "user": user}
    )


@router.get("/delete/")
def show_items_to_delete(request: Request, db: Session = Depends(get_db)):
    errors = []
    token = request.cookies.get("access_token")
    if token is None:
        return templates.TemplateResponse(
            "general_pages/user_update_delete.html", {"request": request, "msg": "Authorization required"}
        )
    scheme, _, param = token.partition(" ")
    payload = jwt.decode(
        param, settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )
    user = payload.get("sub")
    if user is None:
        return templates.TemplateResponse(
            "general_pages/user_update_delete.html", {"request": request, "msg": "Authorize required"}
        )
    users = list_users_sorted(db=db)
    print(users)
    return templates.TemplateResponse(
        "general_pages/user_update_delete.html", {"request": request, "users": users}
    )


@router.delete("/delete/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    message = delete_user_by_id(id=id, db=db)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} not found")
    return {"message": "Successfully deleted."}
