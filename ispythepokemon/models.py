from sqlmodel import create_engine, Field, SQLModel


class Pokemon(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    type: str


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)
