import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool  # <-- Novo import necessário

from src.main import app, get_session

# 1. Configura o motor SQLite com StaticPool para manter a memória persistente
sqlite_url = "sqlite:///:memory:"
test_engine = create_engine(
    sqlite_url, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # <-- Impede que o SQLite destrua o banco entre as conexões
)

# 2. Sobrescreve a sessão
def get_session_override():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = get_session_override

@pytest.fixture(name="client")
def client_fixture():
    # Cria as tabelas no banco de memória persistente
    SQLModel.metadata.create_all(test_engine)
    
    with TestClient(app) as client:
        yield client
        
    # Limpa as tabelas ao final do teste
    SQLModel.metadata.drop_all(test_engine)

# --- TESTES ---

def test_create_usuario(client: TestClient):
    response = client.post(
        "/usuarios/",
        json={
            "nome": "Mateus Costa",
            "email": "mateus.costa@ufmg.br",
            "senha": "senha_super_segura",
            "is_freelancer": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Mateus Costa"
    assert data["is_freelancer"] is True
    assert data["saldo_conta"] == 0.0
    assert "id" in data

def test_read_usuario(client: TestClient):
    post_response = client.post(
        "/usuarios/",
        json={
            "nome": "Felipe Gomide",
            "email": "felipe@teste.com",
            "senha": "123",
            "is_freelancer": False
        }
    )
    user_id = post_response.json()["id"]

    get_response = client.get(f"/usuarios/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["nome"] == "Felipe Gomide"

def test_read_usuario_not_found(client: TestClient):
    response = client.get("/usuarios/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuario não encontrado"}