import re
import bcrypt
from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.middleware.cors import CORSMiddleware
from pydantic import field_validator

# --- ESQUEMAS DE DADOS (Pydantic/SQLModel) ---
class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    senha_hash: str
    is_freelancer: bool = Field(default=False)
    saldo_conta: float = Field(default=0.0)

class UsuarioCreate(SQLModel):
    nome: str
    email: str
    senha: str
    is_freelancer: bool = False

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str):
        if len(v) < 6:
            raise ValueError("A senha deve ter no mínimo 6 caracteres")
        return v

    @field_validator("email")
    @classmethod
    def validar_email(cls, v: str):
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v):
            raise ValueError("E-mail com formato inválido")
        return v

class Deposito(SQLModel):
    valor: float

class LoginRequest(SQLModel):
    email: str
    senha: str

# --- SEGURANÇA: HASH DE SENHA ---
def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())

class Servico(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titulo: str = Field(index=True)
    descricao: str
    preco: float
    freelancer_id: int = Field(foreign_key="usuario.id")

class ServicoUpdate(SQLModel):
    descricao: str | None = None
    preco: float | None = None

class Contrato(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    servico_id: int = Field(foreign_key="servico.id")
    cliente_id: int = Field(foreign_key="usuario.id")
    status: str = Field(default="pendente")  # pendente, validado, cancelado
    valor_pago: float

# --- LÓGICA DE NEGÓCIO PURA ---
def calcular_repasse_freelancer(valor_pago: float, taxa_plataforma: float = 0.10) -> float:
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROTAS DE USUÁRIOS ---
@app.post("/usuarios/")
def create_usuario(dados: UsuarioCreate, session: SessionDep) -> Usuario:
    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        is_freelancer=dados.is_freelancer,
    )
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

@app.patch("/usuarios/{usuario_id}/depositar")
def depositar_fundos(usuario_id: int, deposito: Deposito, session: SessionDep):
    if deposito.valor <= 0:
        raise HTTPException(status_code=400, detail="Valor do depósito deve ser maior que zero")
    
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    
    usuario.saldo_conta += deposito.valor
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return {"mensagem": "Fundos adicionados com sucesso", "saldo_atual": usuario.saldo_conta}

@app.post("/login")
def login(credenciais: LoginRequest, session: SessionDep) -> Usuario:
    usuario = session.exec(
        select(Usuario).where(Usuario.email == credenciais.email)
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")

    if not verificar_senha(credenciais.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Senha incorreta")

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

@app.patch("/servicos/{servico_id}")
def update_servico(servico_id: int, servico_update: ServicoUpdate, session: SessionDep) -> Servico:
    servico_db = session.get(Servico, servico_id)
    if not servico_db:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    if servico_update.preco is not None:
        if servico_update.preco <= 0:
            raise HTTPException(status_code=400, detail="O preço deve ser maior que zero")
        servico_db.preco = servico_update.preco
        
    if servico_update.descricao is not None:
        servico_db.descricao = servico_update.descricao

    session.add(servico_db)
    session.commit()
    session.refresh(servico_db)
    return servico_db

@app.get("/servicos/")
def list_servicos(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[Servico]:
    return session.exec(select(Servico).offset(offset).limit(limit)).all()

# --- ROTAS DE CONTRATOS ---
@app.post("/contratos/")
def create_contrato(contrato: Contrato, session: SessionDep) -> Contrato:
    cliente = session.get(Usuario, contrato.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
    servico = session.get(Servico, contrato.servico_id)
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    if cliente.saldo_conta < servico.preco:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para contratar este serviço")

    cliente.saldo_conta -= servico.preco
    contrato.valor_pago = servico.preco
    contrato.status = "pendente"

    session.add(cliente)
    session.add(contrato)
    session.commit()
    session.refresh(contrato)
    return contrato

@app.patch("/contratos/{contrato_id}/validar")
def validar_contrato(contrato_id: int, session: SessionDep):
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    if contrato.status != "pendente":
        raise HTTPException(status_code=400, detail=f"Contrato não pode ser validado (Status: {contrato.status})")

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

@app.patch("/contratos/{contrato_id}/cancelar")
def cancelar_contrato(contrato_id: int, session: SessionDep):
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    if contrato.status != "pendente":
        raise HTTPException(status_code=400, detail="Apenas contratos pendentes podem ser cancelados")

    cliente = session.get(Usuario, contrato.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    cliente.saldo_conta += contrato.valor_pago
    contrato.status = "cancelado"

    session.add(cliente)
    session.add(contrato)
    session.commit()
    session.refresh(contrato)

    return {"mensagem": "Contrato cancelado e valor estornado", "contrato": contrato}