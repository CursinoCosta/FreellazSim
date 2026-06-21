from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- MODELAGEM DE DADOS ---
class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    senha: str
    is_freelancer: bool = Field(default=False)
    saldo_conta: float = Field(default=0.0)

# --- CONFIGURAÇÃO DO BANCO ---
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# --- ROTAS (ENDPOINTS) ---

@app.post("/usuarios/")
def create_usuario(usuario: Usuario, session: SessionDep) -> Usuario:
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@app.get("/usuarios/{usuario_id}")
def read_usuario(usuario_id: int, session: SessionDep) -> Usuario:
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    return usuario

@app.get("/usuarios/")
def list_usuarios(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Usuario]:
    usuarios = session.exec(select(Usuario).offset(offset).limit(limit)).all()
    return usuarios