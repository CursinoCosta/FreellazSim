from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.middleware.cors import CORSMiddleware

# --- MODELAGEM DE DADOS ---
class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    senha: str
    is_freelancer: bool = Field(default=False)
    saldo_conta: float = Field(default=0.0)

class Servico(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)
    descricao: str
    preco: float
    freelancer_id: int = Field(foreign_key="usuario.id")

class Contrato(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    servico_id: int = Field(foreign_key="servico.id")
    cliente_id: int = Field(foreign_key="usuario.id")
    status: str = Field(default="pendente")  # Status possíveis: pendente, validado
    valor_pago: float

def calcular_repasse_freelancer(valor_pago: float, taxa_plataforma: float = 0.10) -> float:
    """Calcula o valor que vai para o freelancer após a retenção da taxa da plataforma."""
    return valor_pago * (1.0 - taxa_plataforma)

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

# Configuração de CORS para permitir que o React se comunique com a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Porta padrão do Vite/React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROTAS DE USUÁRIOS ---
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
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Usuario]:
    return session.exec(select(Usuario).offset(offset).limit(limit)).all()

# --- ROTAS DE SERVIÇOS ---
@app.post("/servicos/")
def create_servico(servico: Servico, session: SessionDep) -> Servico:
    if servico.preco <= 0:
        raise HTTPException(status_code=400, detail="O preço deve ser maior que zero")
    session.add(servico)
    session.commit()
    session.refresh(servico)
    return servico

@app.get("/servicos/")
def list_servicos(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Servico]:
    return session.exec(select(Servico).offset(offset).limit(limit)).all()

# --- ROTAS DE CONTRATOS ---
@app.post("/contratos/")
def create_contrato(contrato: Contrato, session: SessionDep) -> Contrato:
    session.add(contrato)
    session.commit()
    session.refresh(contrato)
    return contrato

@app.patch("/contratos/{contrato_id}/validar")
def validar_contrato(contrato_id: int, session: SessionDep):
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    if contrato.status == "validado":
        raise HTTPException(status_code=400, detail="Contrato já validado")

    servico = session.get(Servico, contrato.servico_id)
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço associado não encontrado")

    freelancer = session.get(Usuario, servico.freelancer_id)
    if not freelancer:
        raise HTTPException(status_code=404, detail="Freelancer associado não encontrado")
    
    contrato.status = "validado"
    valor_repasse = calcular_repasse_freelancer(contrato.valor_pago)
    freelancer.saldo_conta += valor_repasse

    session.add(contrato)
    session.add(freelancer)
    session.commit()
    session.refresh(contrato)
    
    return {"mensagem": "Contrato validado com sucesso", "contrato": contrato}