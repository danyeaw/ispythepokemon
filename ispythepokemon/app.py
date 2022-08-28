from fastapi import FastAPI, Depends
from sqlmodel import Session, select

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
        pokemon = session.exec(select(Pokemon)).all()
        print(pokemon)
        return pokemon


@app.post("/pokemon/")
def create_hero(hero: Pokemon):
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


def select_pokemon():
    with Session(engine) as session:
        statement = select(Pokemon).where(Pokemon.type == "Fire")
        results = session.exec(statement)
        pokemon = results.one()
        print(f"Pokemon: {pokemon}")


def main():
    create_db_and_tables()
    select_pokemon()


if __name__ == "__main__":
    main()
