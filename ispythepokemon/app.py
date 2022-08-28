from fastapi import FastAPI
from sqlmodel import Session, or_, select

from ispythepokemon.database import create_db_and_tables, engine
from ispythepokemon.models import Pokemon

app = FastAPI()


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/pokemon/")
def read_pokemon():
    with Session(engine) as session:
        return session.exec(select(Pokemon)).all()


@app.get("/type/{pokemon_types}")
def read_pokemon_by_type(pokemon_types: str):
    with Session(engine) as session:
        if " " in pokemon_types:
            types_list = pokemon_types.split()
            reversed_types = f"{types_list[1]} {types_list[0]}"

        statement = select(Pokemon).where(
            or_(Pokemon.type == pokemon_types, Pokemon.type == reversed_types)
        )

        results = session.exec(statement)
        return results.all()
