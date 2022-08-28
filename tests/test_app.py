import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ispythepokemon.app import app, get_session
from ispythepokemon.models import Pokemon


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_pokemon(client: TestClient):
    response = client.post(
        "/pokemon/", json={"name": "Pikachu", "type": "Electric"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Pikachu"
    assert data["type"] == "Electric"
    assert data["id"] is not None


def test_read_pokemon(session: Session, client: TestClient):
    pokemon_1 = Pokemon(name="Pikachu", type="Electric")
    pokemon_2 = Pokemon(name="Bulbasaur", type="Grass Poison")
    session.add(pokemon_1)
    session.add(pokemon_2)
    session.commit()

    response = client.get("/pokemon/")
    data = response.json()

    assert response.status_code == 200

    assert data[0]["name"] == pokemon_1.name
    assert data[0]["type"] == pokemon_1.type
    assert data[0]["id"] == pokemon_1.id
    assert data[1]["name"] == pokemon_2.name
    assert data[1]["type"] == pokemon_2.type
    assert data[1]["id"] == pokemon_2.id