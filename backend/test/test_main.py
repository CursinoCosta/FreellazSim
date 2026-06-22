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
            "senha": "senha123",
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


# (Adicione isso no final do arquivo test/test_main.py)

def test_create_servico_integracao(client: TestClient):
    """Teste de integração: valida a rota POST de serviços."""
    # Primeiro criamos um usuário para ser o dono do serviço
    client.post("/usuarios/", json={"nome": "Free", "email": "f@f.com", "senha": "senha123", "is_freelancer": True})
    
    response = client.post(
        "/servicos/",
        json={
            "titulo": "Desenvolvimento de API",
            "descricao": "API em FastAPI",
            "preco": 1200.50,
            "freelancer_id": 1
        }
    )
    assert response.status_code == 200
    assert response.json()["titulo"] == "Desenvolvimento de API"

def test_create_servico_preco_invalido(client: TestClient):
    """Teste de integração: valida a regra de negócio da rota (HTTP 400)."""
    response = client.post(
        "/servicos/",
        json={
            "titulo": "Serviço Grátis (Erro)",
            "descricao": "Não deve passar",
            "preco": 0,
            "freelancer_id": 1
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "O preço deve ser maior que zero"}

def test_fluxo_completo_contrato_e_repasse(client: TestClient):
    """Teste de integração: valida a criação do contrato e a atualização correta do saldo."""
    # 1. Cria Freelancer
    res_freela = client.post("/usuarios/", json={"nome": "Freela", "email": "freela@f.com", "senha": "senha123", "is_freelancer": True})
    freela_id = res_freela.json()["id"]

    # 2. Cria Cliente
    res_cliente = client.post("/usuarios/", json={"nome": "Cliente", "email": "cliente@c.com", "senha": "senha123", "is_freelancer": False})
    cliente_id = res_cliente.json()["id"]
    
    # 3. Deposita fundos na conta do Cliente (NOVO PASSO)
    client.patch(f"/usuarios/{cliente_id}/depositar", json={"valor": 1000.0})

    # 4. Cria Serviço
    res_servico = client.post("/servicos/", json={"titulo": "Site", "descricao": "React", "preco": 1000.0, "freelancer_id": freela_id})
    servico_id = res_servico.json()["id"]

    # 5. Cria Contrato
    res_contrato = client.post("/contratos/", json={"servico_id": servico_id, "cliente_id": cliente_id, "valor_pago": 1000.0})
    assert res_contrato.status_code == 200
    contrato_id = res_contrato.json()["id"]

    # 6. Valida Contrato (Patch)
    res_validar = client.patch(f"/contratos/{contrato_id}/validar")
    assert res_validar.status_code == 200
    assert res_validar.json()["contrato"]["status"] == "validado"

    # 7. Checa saldo do Freelancer (Deve ser 900.0, já que a taxa é 10%)
    res_freela_atualizado = client.get(f"/usuarios/{freela_id}")
    assert res_freela_atualizado.json()["saldo_conta"] == 900.0

def test_depositar_fundos(client: TestClient):
    """Testa se o depósito incrementa o saldo corretamente."""
    res_user = client.post("/usuarios/", json={"nome": "Investidor", "email": "inv@c.com", "senha": "senha123", "is_freelancer": False})
    user_id = res_user.json()["id"]

    res_deposito = client.patch(f"/usuarios/{user_id}/depositar", json={"valor": 500.0})
    assert res_deposito.status_code == 200
    assert res_deposito.json()["saldo_atual"] == 500.0

def test_atualizar_servico(client: TestClient):
    """Testa se o freelancer pode alterar o preço e a descrição do serviço."""
    res_user = client.post("/usuarios/", json={"nome": "Editor", "email": "ed@f.com", "senha": "senha123", "is_freelancer": True})
    user_id = res_user.json()["id"]

    res_servico = client.post("/servicos/", json={"titulo": "Edição de Vídeo", "descricao": "Básico", "preco": 100.0, "freelancer_id": user_id})
    servico_id = res_servico.json()["id"]

    # Altera apenas a descrição para string vazia (removendo) e atualiza o preço
    res_update = client.patch(f"/servicos/{servico_id}", json={"descricao": "", "preco": 150.0})
    assert res_update.status_code == 200
    assert res_update.json()["preco"] == 150.0
    assert res_update.json()["descricao"] == ""

def test_criar_contrato_sem_saldo(client: TestClient):
    """Testa se o sistema barra a criação de contrato se o cliente não tiver dinheiro."""
    res_user = client.post("/usuarios/", json={"nome": "Pobre", "email": "p@p.com", "senha": "senha123", "is_freelancer": False})
    cliente_id = res_user.json()["id"]
    
    # Criamos um serviço qualquer
    res_freela = client.post("/usuarios/", json={"nome": "F", "email": "f2@f.com", "senha": "senha123", "is_freelancer": True})
    res_servico = client.post("/servicos/", json={"titulo": "S", "descricao": "D", "preco": 500.0, "freelancer_id": res_freela.json()["id"]})

    res_contrato = client.post("/contratos/", json={"servico_id": res_servico.json()["id"], "cliente_id": cliente_id, "valor_pago": 500.0})
    assert res_contrato.status_code == 400
    assert res_contrato.json()["detail"] == "Saldo insuficiente para contratar este serviço"

def test_login_sucesso(client: TestClient):
    """Testa se o login funciona com email e senha corretos."""
    client.post("/usuarios/", json={"nome": "Login", "email": "login@teste.com", "senha": "senha123", "is_freelancer": False})

    response = client.post("/login", json={"email": "login@teste.com", "senha": "senha123"})
    assert response.status_code == 200
    assert response.json()["email"] == "login@teste.com"

def test_login_usuario_nao_encontrado(client: TestClient):
    """Testa se o login retorna 404 quando o email não existe."""
    response = client.post("/login", json={"email": "naoexiste@teste.com", "senha": "senha123"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuario não encontrado"}

def test_login_senha_incorreta(client: TestClient):
    """Testa se o login retorna 401 quando a senha está errada."""
    client.post("/usuarios/", json={"nome": "Login2", "email": "login2@teste.com", "senha": "senha123", "is_freelancer": False})

    response = client.post("/login", json={"email": "login2@teste.com", "senha": "errada"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Senha incorreta"}

def test_cancelar_contrato_e_estorno(client: TestClient):
    """Testa o cancelamento de um contrato e a devolução do dinheiro para o cliente."""
    res_freela = client.post("/usuarios/", json={"nome": "F", "email": "f3@f.com", "senha": "senha123", "is_freelancer": True})
    freela_id = res_freela.json()["id"]
    
    res_cliente = client.post("/usuarios/", json={"nome": "C", "email": "c3@c.com", "senha": "senha123", "is_freelancer": False})
    cliente_id = res_cliente.json()["id"]
    
    # Adiciona fundos para o cliente
    client.patch(f"/usuarios/{cliente_id}/depositar", json={"valor": 200.0})

    res_servico = client.post("/servicos/", json={"titulo": "S", "descricao": "D", "preco": 200.0, "freelancer_id": freela_id})
    servico_id = res_servico.json()["id"]

    res_contrato = client.post("/contratos/", json={"servico_id": servico_id, "cliente_id": cliente_id, "valor_pago": 200.0})
    contrato_id = res_contrato.json()["id"]

    # Cancela o contrato
    res_cancelar = client.patch(f"/contratos/{contrato_id}/cancelar")
    assert res_cancelar.status_code == 200
    assert res_cancelar.json()["contrato"]["status"] == "cancelado"

    # Verifica se o cliente recebeu os 200 de volta
    cliente_atualizado = client.get(f"/usuarios/{cliente_id}")
    assert cliente_atualizado.json()["saldo_conta"] == 200.0