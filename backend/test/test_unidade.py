import jwt
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError

from src.main import (
    Usuario, UsuarioCreate, Servico, Contrato, Deposito, ServicoUpdate, LoginRequest,
    calcular_repasse_freelancer, hash_senha, criar_token, get_usuario_atual,
    create_usuario, read_usuario, depositar_fundos, list_usuarios,
    create_servico, update_servico, list_servicos,
    create_contrato, validar_contrato, cancelar_contrato, login
)

# ==========================================
# 1. TESTES DE MODELOS (PYDANTIC)
# ==========================================

def test_usuario_valido():
    # model_validate força o Pydantic a rodar todas as validações no dicionário
    usuario = UsuarioCreate.model_validate({
        "nome": "João",
        "email": "joao@teste.com",
        "senha": "senha_segura"
    })
    assert usuario.is_freelancer is False

def test_usuario_senha_curta():
    with pytest.raises(ValidationError, match="mínimo 6 caracteres"):
        UsuarioCreate.model_validate({
            "nome": "João",
            "email": "joao@teste.com",
            "senha": "123"  # Senha menor que 6 caracteres
        })

def test_usuario_email_invalido():
    with pytest.raises(ValidationError, match="formato inválido"):
        UsuarioCreate.model_validate({
            "nome": "João",
            "email": "joaosemarroba.com", # E-mail sem @
            "senha": "senha_segura"
        })

# ==========================================
# 2. TESTES DE LÓGICA DE NEGÓCIO PURA
# ==========================================

def test_calcular_repasse_padrao():
    assert calcular_repasse_freelancer(100.0) == 90.0

def test_calcular_repasse_customizado():
    assert calcular_repasse_freelancer(150.0, taxa_plataforma=0.20) == 120.0

def test_calcular_repasse_isencao_taxa():
    assert calcular_repasse_freelancer(100.0, taxa_plataforma=0.0) == 100.0

# ==========================================
# 3. TESTES DE ROTAS MOCKADAS (USUÁRIOS)
# ==========================================

def test_mock_create_usuario():
    session_mock = MagicMock()
    dados = UsuarioCreate(nome="Mock", email="m@m.com", senha="123456")
    resultado = create_usuario(dados, session_mock)
    session_mock.add.assert_called_once()
    session_mock.commit.assert_called_once()
    assert resultado.nome == "Mock"
    assert resultado.senha_hash != "123456"

def test_mock_read_usuario_encontrado():
    session_mock = MagicMock()
    user_fake = Usuario(id=1, nome="Mock", email="m@m.com", senha_hash="hash")
    session_mock.get.return_value = user_fake
    resultado = read_usuario(1, session_mock)
    assert resultado.id == 1

def test_mock_read_usuario_nao_encontrado():
    session_mock = MagicMock()
    session_mock.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        read_usuario(99, session_mock)
    assert exc.value.status_code == 404

def test_mock_list_usuario_vazia():
    session_mock = MagicMock()
    # Simula o retorno de um iterável vazio
    session_mock.exec.return_value.all.return_value = []
    resultado = list_usuarios(session_mock)
    assert resultado == []

def test_mock_depositar_fundos_sucesso():
    session_mock = MagicMock()
    user_fake = Usuario(id=1, nome="Mock", email="m@m.com", senha_hash="hash", saldo_conta=0.0)
    session_mock.get.return_value = user_fake
    resultado = depositar_fundos(1, Deposito(valor=100.0), session_mock)
    assert resultado["saldo_atual"] == 100.0

def test_mock_depositar_fundos_valor_negativo():
    session_mock = MagicMock()
    with pytest.raises(HTTPException) as exc:
        depositar_fundos(1, Deposito(valor=-50.0), session_mock)
    assert exc.value.status_code == 400

def test_mock_depositar_fundos_nao_encontrado():
    session_mock = MagicMock()
    session_mock.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        depositar_fundos(99, Deposito(valor=100.0), session_mock)
    assert exc.value.status_code == 404

def test_mock_login_sucesso():
    session_mock = MagicMock()
    user_fake = Usuario(id=1, nome="Mock", email="m@m.com", senha_hash=hash_senha("123456"))
    session_mock.exec.return_value.first.return_value = user_fake
    resultado = login(LoginRequest(email="m@m.com", senha="123456"), session_mock)
    assert resultado.usuario.id == 1
    assert resultado.token_type == "bearer"
    assert resultado.access_token

def test_mock_login_usuario_nao_encontrado():
    session_mock = MagicMock()
    session_mock.exec.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        login(LoginRequest(email="ninguem@m.com", senha="123456"), session_mock)
    assert exc.value.status_code == 404

def test_mock_login_senha_incorreta():
    session_mock = MagicMock()
    user_fake = Usuario(id=1, nome="Mock", email="m@m.com", senha_hash=hash_senha("123456"))
    session_mock.exec.return_value.first.return_value = user_fake
    with pytest.raises(HTTPException) as exc:
        login(LoginRequest(email="m@m.com", senha="errada"), session_mock)
    assert exc.value.status_code == 401

def _credenciais(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

def test_get_usuario_atual_token_valido():
    session_mock = MagicMock()
    user_fake = Usuario(id=1, nome="Mock", email="m@m.com", senha_hash="hash")
    session_mock.get.return_value = user_fake

    resultado = get_usuario_atual(_credenciais(criar_token(1)), session_mock)
    assert resultado.id == 1

def test_get_usuario_atual_token_invalido():
    session_mock = MagicMock()
    with pytest.raises(HTTPException) as exc:
        get_usuario_atual(_credenciais("token.invalido.aqui"), session_mock)
    assert exc.value.status_code == 401

def test_get_usuario_atual_token_expirado():
    session_mock = MagicMock()
    from datetime import datetime, timedelta, timezone
    from src.main import SECRET_KEY, ALGORITHM

    token_expirado = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc:
        get_usuario_atual(_credenciais(token_expirado), session_mock)
    assert exc.value.status_code == 401

def test_get_usuario_atual_usuario_nao_encontrado():
    session_mock = MagicMock()
    session_mock.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        get_usuario_atual(_credenciais(criar_token(999)), session_mock)
    assert exc.value.status_code == 401

# ==========================================
# 4. TESTES DE ROTAS MOCKADAS (SERVIÇOS)
# ==========================================

def test_mock_create_servico_sucesso():
    session_mock = MagicMock()
    servico = Servico(titulo="Logo", descricao="Logo top", preco=150.0, freelancer_id=1)
    resultado = create_servico(servico, session_mock)
    assert resultado.preco == 150.0

def test_mock_create_servico_preco_negativo():
    session_mock = MagicMock()
    servico = Servico(titulo="Logo", descricao="Logo top", preco=-10.0, freelancer_id=1)
    with pytest.raises(HTTPException) as exc:
        create_servico(servico, session_mock)
    assert exc.value.status_code == 400

def test_mock_update_servico_sucesso():
    session_mock = MagicMock()
    servico_fake = Servico(id=1, titulo="Logo", descricao="Antiga", preco=100.0, freelancer_id=1)
    session_mock.get.return_value = servico_fake
    
    update_data = ServicoUpdate(descricao="Nova", preco=200.0)
    resultado = update_servico(1, update_data, session_mock)
    assert resultado.descricao == "Nova"
    assert resultado.preco == 200.0

def test_mock_update_servico_nao_encontrado():
    session_mock = MagicMock()
    session_mock.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        update_servico(99, ServicoUpdate(preco=100.0), session_mock)
    assert exc.value.status_code == 404

def test_mock_update_servico_preco_invalido():
    session_mock = MagicMock()
    servico_fake = Servico(id=1, titulo="Logo", descricao="Antiga", preco=100.0, freelancer_id=1)
    session_mock.get.return_value = servico_fake
    with pytest.raises(HTTPException) as exc:
        update_servico(1, ServicoUpdate(preco=-5.0), session_mock)
    assert exc.value.status_code == 400

def test_mock_list_servicos():
    session_mock = MagicMock()
    session_mock.exec.return_value.all.return_value = []
    resultado = list_servicos(session_mock)
    assert resultado == []

# ==========================================
# 5. TESTES DE ROTAS MOCKADAS (CONTRATOS)
# ==========================================

def test_mock_create_contrato_sucesso():
    session_mock = MagicMock()
    cliente = Usuario(id=1, nome="C", email="c@c", senha_hash="hash", saldo_conta=500.0)
    servico = Servico(id=1, titulo="S", descricao="D", preco=100.0, freelancer_id=2)
    
    # get(Usuario) retorna cliente, get(Servico) retorna servico
    session_mock.get.side_effect = [cliente, servico]
    
    contrato = Contrato(servico_id=1, cliente_id=1, valor_pago=0)
    resultado = create_contrato(contrato, session_mock)
    
    assert resultado.status == "pendente"
    assert cliente.saldo_conta == 400.0 # 500 - 100

def test_mock_create_contrato_cliente_nao_encontrado():
    session_mock = MagicMock()
    session_mock.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        create_contrato(Contrato(servico_id=1, cliente_id=99, valor_pago=0), session_mock)
    assert exc.value.status_code == 404

def test_mock_create_contrato_servico_nao_encontrado():
    session_mock = MagicMock()
    cliente = Usuario(id=1, nome="C", email="c@c", senha_hash="hash", saldo_conta=500.0)
    session_mock.get.side_effect = [cliente, None]
    with pytest.raises(HTTPException) as exc:
        create_contrato(Contrato(servico_id=99, cliente_id=1, valor_pago=0), session_mock)
    assert exc.value.status_code == 404

def test_mock_create_contrato_saldo_insuficiente():
    session_mock = MagicMock()
    cliente = Usuario(id=1, nome="C", email="c@c", senha_hash="hash", saldo_conta=50.0)
    servico = Servico(id=1, titulo="S", descricao="D", preco=100.0, freelancer_id=2)
    session_mock.get.side_effect = [cliente, servico]
    
    with pytest.raises(HTTPException) as exc:
        create_contrato(Contrato(servico_id=1, cliente_id=1, valor_pago=0), session_mock)
    assert exc.value.status_code == 400

def test_mock_validar_contrato_sucesso():
    session_mock = MagicMock()
    contrato = Contrato(id=1, servico_id=1, cliente_id=1, status="pendente", valor_pago=100.0)
    servico = Servico(id=1, titulo="S", descricao="D", preco=100.0, freelancer_id=2)
    freela = Usuario(id=2, nome="F", email="f@f", senha_hash="hash", saldo_conta=0.0)
    
    session_mock.get.side_effect = [contrato, servico, freela]
    
    resultado = validar_contrato(1, session_mock)
    assert resultado["contrato"].status == "validado"
    assert freela.saldo_conta == 90.0

def test_mock_validar_contrato_nao_encontrado():
    session_mock = MagicMock()
    session_mock.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        validar_contrato(99, session_mock)
    assert exc.value.status_code == 404

def test_mock_validar_contrato_ja_validado():
    session_mock = MagicMock()
    contrato = Contrato(id=1, servico_id=1, cliente_id=1, status="validado", valor_pago=100.0)
    session_mock.get.return_value = contrato
    with pytest.raises(HTTPException) as exc:
        validar_contrato(1, session_mock)
    assert exc.value.status_code == 400

def test_mock_validar_contrato_servico_nao_encontrado():
    session_mock = MagicMock()
    contrato = Contrato(id=1, servico_id=1, cliente_id=1, status="pendente", valor_pago=100.0)
    session_mock.get.side_effect = [contrato, None]
    with pytest.raises(HTTPException) as exc:
        validar_contrato(1, session_mock)
    assert exc.value.status_code == 404

def test_mock_validar_contrato_freela_nao_encontrado():
    session_mock = MagicMock()
    contrato = Contrato(id=1, servico_id=1, cliente_id=1, status="pendente", valor_pago=100.0)
    servico = Servico(id=1, titulo="S", descricao="D", preco=100.0, freelancer_id=2)
    session_mock.get.side_effect = [contrato, servico, None]
    with pytest.raises(HTTPException) as exc:
        validar_contrato(1, session_mock)
    assert exc.value.status_code == 404

def test_mock_cancelar_contrato_sucesso():
    session_mock = MagicMock()
    contrato = Contrato(id=1, servico_id=1, cliente_id=1, status="pendente", valor_pago=100.0)
    cliente = Usuario(id=1, nome="C", email="c@c", senha_hash="hash", saldo_conta=0.0)
    
    session_mock.get.side_effect = [contrato, cliente]
    
    resultado = cancelar_contrato(1, session_mock)
    assert resultado["contrato"].status == "cancelado"
    assert cliente.saldo_conta == 100.0

def test_mock_cancelar_contrato_nao_pendente():
    session_mock = MagicMock()
    contrato = Contrato(id=1, servico_id=1, cliente_id=1, status="validado", valor_pago=100.0)
    session_mock.get.return_value = contrato
    with pytest.raises(HTTPException) as exc:
        cancelar_contrato(1, session_mock)
    assert exc.value.status_code == 400