from sqlalchemy.orm import Session

from schemas.users import UserCreate, UserUpdate
from db.models.users import Users
from core.hashing import Hasher


def create_new_user(user: UserCreate, db: Session):
    user = Users(username=user.username,
                 email=user.email,
                 hashed_password=Hasher.get_password_hash(user.password),
                 is_active=True,
                 is_superuser=False
                 )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def retreive_user(id: int, db: Session):
    item = db.query(Users).filter(Users.id == id).first()
    return item


def list_users(db: Session):  # new
    users = db.query(Users).all()
    return users


def list_users_sorted(db: Session):  # new
    users = db.query(Users).order_by(Users.id)
    return users


def update_user_by_id(id: int, user: UserUpdate, db: Session):
    existing_user = db.query(Users).filter(Users.id == id)
    if not existing_user.first():
        return 0

    existing_user.update(user.__dict__)
    db.commit()
    return 1


def delete_user_by_id(id: int, db: Session):
    existing_user = db.query(Users).filter(Users.id == id)
    if not existing_user.first():
        return 0
    existing_user.delete(synchronize_session=False)
    db.commit()
    return 1
