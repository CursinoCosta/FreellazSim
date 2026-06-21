from src.main import Servico, Usuario

def test_instanciacao_usuario_padrao():
    """Teste de unidade puro: verifica se o valor padrão de is_freelancer é False."""
    user = Usuario(nome="João", email="joao@teste.com", senha="123")
    assert user.is_freelancer is False
    assert user.saldo_conta == 0.0

def test_instanciacao_servico():
    """Teste de unidade puro: verifica a atribuição correta dos campos do modelo Servico."""
    servico = Servico(titulo="Logo design", descricao="Faço sua logo", preco=150.0, freelancer_id=1)
    assert servico.titulo == "Logo design"
    assert servico.preco == 150.0
    assert servico.freelancer_id == 1