from fastapi.testclient import TestClient
from src.main import app

# O TestClient simula requisições para a nossa API sem precisar subir o servidor localmente
client = TestClient(app)

def test_read_heroes_empty():
    """
    Testa se a rota de listagem retorna uma lista vazia quando o banco está limpo.
    """
    response = client.get("/heroes/")
    
    assert response.status_code == 200
    assert response.json() == []