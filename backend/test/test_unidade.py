from src.main import Servico, Usuario, Contrato, calcular_repasse_freelancer

def test_instanciacao_usuario_padrao():
    user = Usuario(nome="João", email="joao@teste.com", senha="123")
    assert user.is_freelancer is False
    assert user.saldo_conta == 0.0

def test_instanciacao_servico():
    servico = Servico(titulo="Logo design", descricao="Faço sua logo", preco=150.0, freelancer_id=1)
    assert servico.titulo == "Logo design"
    assert servico.preco == 150.0
    assert servico.freelancer_id == 1

def test_instanciacao_contrato():
    """Teste de unidade: verifica inicialização de status pendente."""
    contrato = Contrato(servico_id=1, cliente_id=2, valor_pago=100.0)
    assert contrato.status == "pendente"
    assert contrato.valor_pago == 100.0

def test_calculo_repasse_freelancer():
    """Teste de unidade puro: valida a regra financeira de retenção de taxa da plataforma."""
    # Cenário 1: 10% de taxa padrão sobre 100.0 deve repassar 90.0
    repasse_padrao = calcular_repasse_freelancer(100.0)
    assert repasse_padrao == 90.0

    # Cenário 2: Forçando uma taxa diferente (ex: 20%) sobre 150.0
    repasse_customizado = calcular_repasse_freelancer(150.0, taxa_plataforma=0.20)
    assert repasse_customizado == 120.0