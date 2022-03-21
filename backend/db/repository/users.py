from sqlalchemy.orm import Session
from sqlalchemy import sql
from schemas.users import UserCreate, UserUpdate
from db.models.users import Users
from db.session import engine
from core.hashing import Hasher

USERS_TABLE = 'USERS'


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


def retrieve_user_raw(id: int): # raw sql
    with engine.connect() as connection:
        query = sql.text(f'SELECT * FROM {USERS_TABLE} WHERE ID={id} FETCH FIRST ROW ONLY')

        execute_query = connection.execute(query)
        for field in execute_query:
            user = Users(username=field[1], email=field[2], is_active=field[4], is_superuser=field[5])
        return user


def retrieve_user(id: int, db: Session):
    user = db.query(Users).filter(Users.id == id).first()
    print(user)
    return user


def list_users(db: Session):
    users = db.query(Users).all()
    return users


def list_users_sorted(db: Session):
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
