from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, or_, select

from ispythepokemon.database import create_db_and_tables, engine
from ispythepokemon.models import Pokemon

app = FastAPI()
app.mount("/static", StaticFiles(directory="ispythepokemon/static"), name="static")
templates = Jinja2Templates(directory="ispythepokemon/templates")


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    pokemon = []
    types = all_types()
    return templates.TemplateResponse(
        "index.html", {"request": request, "pokemon": pokemon, "types": types}
    )


def get_pokemon_by_type(type1: str, type2: str | None):
    with Session(engine) as session:
        if type2:
            statement = select(Pokemon).where(
                or_(Pokemon.type == f"{type1} {type2}", Pokemon.type == f"{type2} {type1}")
            )
        else:
            statement = select(Pokemon).where(Pokemon.type == type1)

        results = session.exec(statement)
        return results.all()


@app.get("/pokemon/")
def all_pokemon():
    with Session(engine) as session:
        return session.exec(select(Pokemon)).all()


def all_types():
    with Session(engine) as session:
        statement = select(Pokemon.type).distinct()
        distinct_types = session.exec(statement).all()
        single_types = set()
        for type in distinct_types:
            single_types.update(type.split())
        return single_types


@app.get("/type/")
def read_pokemon_by_type(request: Request, type1: str, type2: str | None = None):
    pokemon = get_pokemon_by_type(type1, type2)
    types = all_types()
    return templates.TemplateResponse(
        "index.html", {"request": request, "pokemon": pokemon, "types": types, "type1": type1, "type2": type2}
    )
