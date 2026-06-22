import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool  # <-- Novo import necessário

from src.main import ALGORITHM, SECRET_KEY, app, get_session

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

def _signup_e_login(client: TestClient, nome, email, senha="senha123", is_freelancer=False):
    """Cadastra e loga um usuário, devolvendo (usuario_id, headers com o Bearer token)."""
    client.post(
        "/usuarios/",
        json={"nome": nome, "email": email, "senha": senha, "is_freelancer": is_freelancer},
    )
    login_response = client.post("/login", json={"email": email, "senha": senha})
    usuario = login_response.json()["usuario"]
    token = login_response.json()["access_token"]
    return usuario["id"], {"Authorization": f"Bearer {token}"}

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
    assert "senha" not in data
    assert "senha_hash" not in data

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
    assert "senha" not in get_response.json()
    assert "senha_hash" not in get_response.json()

def test_read_usuario_not_found(client: TestClient):
    response = client.get("/usuarios/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuario não encontrado"}

def test_list_usuarios_nao_expoe_senha(client: TestClient):
    """Garante que a listagem de usuários nunca devolve a senha/hash."""
    client.post(
        "/usuarios/",
        json={"nome": "Anyone", "email": "anyone@teste.com", "senha": "senha123"},
    )

    response = client.get("/usuarios/")
    assert response.status_code == 200
    usuarios = response.json()
    assert len(usuarios) >= 1
    for usuario in usuarios:
        assert "senha" not in usuario
        assert "senha_hash" not in usuario


# (Adicione isso no final do arquivo test/test_main.py)

def test_create_servico_integracao(client: TestClient):
    """Teste de integração: valida a rota POST de serviços."""
    freelancer_id, headers = _signup_e_login(client, "Free", "f@f.com", is_freelancer=True)

    response = client.post(
        "/servicos/",
        json={
            "titulo": "Desenvolvimento de API",
            "descricao": "API em FastAPI",
            "preco": 1200.50,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["titulo"] == "Desenvolvimento de API"
    assert response.json()["freelancer_id"] == freelancer_id

def test_create_servico_preco_invalido(client: TestClient):
    """Teste de integração: valida a regra de negócio da rota (HTTP 400)."""
    _, headers = _signup_e_login(client, "Free2", "free2@f.com", is_freelancer=True)

    response = client.post(
        "/servicos/",
        json={
            "titulo": "Serviço Grátis (Erro)",
            "descricao": "Não deve passar",
            "preco": 0,
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "O preço deve ser maior que zero"}

def test_create_servico_sem_ser_freelancer(client: TestClient):
    """Apenas usuários cadastrados como freelancer podem anunciar serviços."""
    _, headers = _signup_e_login(client, "Cliente", "clientex@c.com", is_freelancer=False)

    response = client.post(
        "/servicos/",
        json={"titulo": "Logo", "descricao": "Logo top", "preco": 100.0},
        headers=headers,
    )
    assert response.status_code == 403

def test_create_servico_sem_token(client: TestClient):
    """Rotas protegidas exigem o header Authorization."""
    response = client.post(
        "/servicos/",
        json={"titulo": "Logo", "descricao": "Logo top", "preco": 100.0},
    )
    assert response.status_code == 401

def test_fluxo_completo_contrato_e_repasse(client: TestClient):
    """Teste de integração: valida a criação do contrato e a atualização correta do saldo."""
    # 1. Cria Freelancer
    freela_id, headers_freela = _signup_e_login(client, "Freela", "freela@f.com", is_freelancer=True)

    # 2. Cria Cliente
    cliente_id, headers_cliente = _signup_e_login(client, "Cliente", "cliente@c.com")

    # 3. Deposita fundos na conta do Cliente
    client.patch(f"/usuarios/{cliente_id}/depositar", json={"valor": 1000.0}, headers=headers_cliente)

    # 4. Cria Serviço
    res_servico = client.post(
        "/servicos/", json={"titulo": "Site", "descricao": "React", "preco": 1000.0}, headers=headers_freela
    )
    servico_id = res_servico.json()["id"]

    # 5. Cria Contrato
    res_contrato = client.post("/contratos/", json={"servico_id": servico_id}, headers=headers_cliente)
    assert res_contrato.status_code == 200
    contrato_id = res_contrato.json()["id"]

    # 6. Valida Contrato (Patch)
    res_validar = client.patch(f"/contratos/{contrato_id}/validar", headers=headers_freela)
    assert res_validar.status_code == 200
    assert res_validar.json()["contrato"]["status"] == "validado"

    # 7. Checa saldo do Freelancer (Deve ser 900.0, já que a taxa é 10%)
    res_freela_atualizado = client.get(f"/usuarios/{freela_id}")
    assert res_freela_atualizado.json()["saldo_conta"] == 900.0

def test_depositar_fundos(client: TestClient):
    """Testa se o depósito incrementa o saldo corretamente."""
    user_id, headers = _signup_e_login(client, "Investidor", "inv@c.com")

    res_deposito = client.patch(f"/usuarios/{user_id}/depositar", json={"valor": 500.0}, headers=headers)
    assert res_deposito.status_code == 200
    assert res_deposito.json()["saldo_atual"] == 500.0

def test_depositar_em_conta_de_outro_usuario(client: TestClient):
    """Um usuário não pode depositar fundos na conta de outro."""
    outro_id, _ = _signup_e_login(client, "Outro", "outro@c.com")
    _, headers_atacante = _signup_e_login(client, "Atacante", "atacante@c.com")

    response = client.patch(f"/usuarios/{outro_id}/depositar", json={"valor": 500.0}, headers=headers_atacante)
    assert response.status_code == 403

def test_atualizar_servico(client: TestClient):
    """Testa se o freelancer pode alterar o preço e a descrição do serviço."""
    _, headers = _signup_e_login(client, "Editor", "ed@f.com", is_freelancer=True)

    res_servico = client.post(
        "/servicos/", json={"titulo": "Edição de Vídeo", "descricao": "Básico", "preco": 100.0}, headers=headers
    )
    servico_id = res_servico.json()["id"]

    # Altera apenas a descrição para string vazia (removendo) e atualiza o preço
    res_update = client.patch(
        f"/servicos/{servico_id}", json={"descricao": "", "preco": 150.0}, headers=headers
    )
    assert res_update.status_code == 200
    assert res_update.json()["preco"] == 150.0
    assert res_update.json()["descricao"] == ""

def test_atualizar_servico_de_outro_freelancer(client: TestClient):
    """Um freelancer não pode editar o serviço de outro."""
    _, headers_dono = _signup_e_login(client, "Dono", "dono@f.com", is_freelancer=True)
    res_servico = client.post(
        "/servicos/", json={"titulo": "S", "descricao": "D", "preco": 100.0}, headers=headers_dono
    )
    servico_id = res_servico.json()["id"]

    _, headers_intruso = _signup_e_login(client, "Intruso", "intruso@f.com", is_freelancer=True)
    response = client.patch(f"/servicos/{servico_id}", json={"preco": 1.0}, headers=headers_intruso)
    assert response.status_code == 403

def test_criar_contrato_sem_saldo(client: TestClient):
    """Testa se o sistema barra a criação de contrato se o cliente não tiver dinheiro."""
    _, headers_cliente = _signup_e_login(client, "Pobre", "p@p.com")
    _, headers_freela = _signup_e_login(client, "F", "f2@f.com", is_freelancer=True)
    res_servico = client.post(
        "/servicos/", json={"titulo": "S", "descricao": "D", "preco": 500.0}, headers=headers_freela
    )

    res_contrato = client.post(
        "/contratos/", json={"servico_id": res_servico.json()["id"]}, headers=headers_cliente
    )
    assert res_contrato.status_code == 400
    assert res_contrato.json()["detail"] == "Saldo insuficiente para contratar este serviço"

def test_login_sucesso(client: TestClient):
    """Testa se o login funciona com email e senha corretos e devolve um token."""
    client.post("/usuarios/", json={"nome": "Login", "email": "login@teste.com", "senha": "senha123", "is_freelancer": False})

    response = client.post("/login", json={"email": "login@teste.com", "senha": "senha123"})
    assert response.status_code == 200
    data = response.json()
    assert data["usuario"]["email"] == "login@teste.com"
    assert data["token_type"] == "bearer"
    assert "senha" not in data["usuario"]
    assert "senha_hash" not in data["usuario"]

    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert int(payload["sub"]) == data["usuario"]["id"]

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
    _, headers_freela = _signup_e_login(client, "F", "f3@f.com", is_freelancer=True)
    cliente_id, headers_cliente = _signup_e_login(client, "C", "c3@c.com")

    # Adiciona fundos para o cliente
    client.patch(f"/usuarios/{cliente_id}/depositar", json={"valor": 200.0}, headers=headers_cliente)

    res_servico = client.post(
        "/servicos/", json={"titulo": "S", "descricao": "D", "preco": 200.0}, headers=headers_freela
    )
    servico_id = res_servico.json()["id"]

    res_contrato = client.post("/contratos/", json={"servico_id": servico_id}, headers=headers_cliente)
    contrato_id = res_contrato.json()["id"]

    # Cancela o contrato
    res_cancelar = client.patch(f"/contratos/{contrato_id}/cancelar", headers=headers_cliente)
    assert res_cancelar.status_code == 200
    assert res_cancelar.json()["contrato"]["status"] == "cancelado"

    # Verifica se o cliente recebeu os 200 de volta
    cliente_atualizado = client.get(f"/usuarios/{cliente_id}")
    assert cliente_atualizado.json()["saldo_conta"] == 200.0

def test_validar_contrato_por_freelancer_errado(client: TestClient):
    """Só o freelancer dono do serviço pode validar o contrato."""
    _, headers_freela = _signup_e_login(client, "F4", "f4@f.com", is_freelancer=True)
    cliente_id, headers_cliente = _signup_e_login(client, "C4", "c4@c.com")
    client.patch(f"/usuarios/{cliente_id}/depositar", json={"valor": 100.0}, headers=headers_cliente)
    res_servico = client.post(
        "/servicos/", json={"titulo": "S", "descricao": "D", "preco": 100.0}, headers=headers_freela
    )
    res_contrato = client.post(
        "/contratos/", json={"servico_id": res_servico.json()["id"]}, headers=headers_cliente
    )
    contrato_id = res_contrato.json()["id"]

    _, headers_outro_freela = _signup_e_login(client, "Outro", "outrofreela@f.com", is_freelancer=True)
    response = client.patch(f"/contratos/{contrato_id}/validar", headers=headers_outro_freela)
    assert response.status_code == 403

def test_cancelar_contrato_por_cliente_errado(client: TestClient):
    """Só o cliente dono do contrato pode cancelá-lo."""
    _, headers_freela = _signup_e_login(client, "F5", "f5@f.com", is_freelancer=True)
    cliente_id, headers_cliente = _signup_e_login(client, "C5", "c5@c.com")
    client.patch(f"/usuarios/{cliente_id}/depositar", json={"valor": 100.0}, headers=headers_cliente)
    res_servico = client.post(
        "/servicos/", json={"titulo": "S", "descricao": "D", "preco": 100.0}, headers=headers_freela
    )
    res_contrato = client.post(
        "/contratos/", json={"servico_id": res_servico.json()["id"]}, headers=headers_cliente
    )
    contrato_id = res_contrato.json()["id"]

    _, headers_outro_cliente = _signup_e_login(client, "Outro", "outrocliente@c.com")
    response = client.patch(f"/contratos/{contrato_id}/cancelar", headers=headers_outro_cliente)
    assert response.status_code == 403