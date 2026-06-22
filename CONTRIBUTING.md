# Contribuindo com o FreellazSim

## Como executar os testes localmente

### Pré-requisitos

Certifique-se de ter o Node.js e o Python (3.10+) instalados na sua máquina.

### Testes do Backend (Pytest)

1. Navegue até o diretório do backend: `cd backend`
2. Crie e ative o ambiente virtual:
   - Linux/macOS: `python -m venv venv && source venv/bin/activate`
   - Windows: `python -m venv venv && venv\Scripts\activate`
3. Instale as dependências de desenvolvimento e teste: `pip install -r requirements.txt pytest pytest-cov httpx`
4. Execute os testes com o relatório de cobertura: `pytest --cov=src`

### Testes do Frontend e E2E (Playwright)

1. Navegue até o diretório do frontend: `cd frontend`
2. Instale as dependências: `npm install`
3. Execute a suíte de testes: `npm run test`
