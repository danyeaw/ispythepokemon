from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, or_, select

from ispythepokemon.database import create_db_and_tables, engine
from ispythepokemon.models import Pokemon

app = FastAPI()
templates = Jinja2Templates(directory="ispythepokemon/templates")


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with Session(engine) as session:
        pokemon = all_pokemon()
        return templates.TemplateResponse(
            "index.html", {"request": request, "pokemon": pokemon}
        )


def get_pokemon_by_type(pokemon_types: str):
    with Session(engine) as session:
        if " " in pokemon_types:
            types_list = pokemon_types.split()
            reversed_types = f"{types_list[1]} {types_list[0]}"

        statement = select(Pokemon).where(
            or_(Pokemon.type == pokemon_types, Pokemon.type == reversed_types)
        )

        results = session.exec(statement)
        return results.all()


@app.get("/pokemon/")
def all_pokemon():
    with Session(engine) as session:
        return session.exec(select(Pokemon)).all()


@app.get("/type/")
def read_pokemon_by_type(request: Request, pokemon_types: str):
    pokemon = get_pokemon_by_type(pokemon_types)
    return templates.TemplateResponse(
        "index.html", {"request": request, "pokemon": pokemon}
    )
