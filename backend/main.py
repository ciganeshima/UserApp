from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from sqlalchemy import event

from core.config import settings
from db.session import engine
from db.base import Base
from db.models.users import Users
from apis.base import api_router


def include_router(app):
    app.include_router(api_router)


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def create_tables():
    Base.metadata.create_all(bind=engine)


# This method receives a table, a connection and inserts data to that table.
def initialize_table(target, connection, **kw):
    table_name = str(target)
    if table_name in settings.INITIAL_DATA and len(settings.INITIAL_DATA[table_name]) > 0:
        connection.execute(target.insert(), settings.INITIAL_DATA[table_name])


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    configure_static(app)
    # set up this event before table creation
    event.listen(Users.__table__, 'after_create', initialize_table)
    create_tables()
    return app


app = start_application()
