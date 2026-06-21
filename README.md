# FreellazSim

## Integrantes

- Felipe Lopes Gomide
- João Correia Costa
- Mateus Cursino Gomes Costa

## Sobre o Sistema

O FreellazSim é um marketplace simplificado inspirado no Fiverr, conectando freelancers e clientes. As funcionalidades centrais incluem cadastro de usuários, publicação de anúncios de serviços e um fluxo básico de contratação e validação do trabalho realizado para repasse financeiro. Nosso objetivo principal é priorizar a testabilidade, utilizando uma suíte de testes automatizados para validar regras de negócio e fluxos de interface, evidenciando como a cobertura de testes facilita a manutenção do software.

## Tecnologias Utilizadas

- **Backend e Banco de Dados:** FastAPI (Python) e SQLite para criação de um banco em memória rápido e isolado para testes.
- **Frontend:** React configurado via Vite.
- **Testes de Backend:** Pytest (testes unitários e de integração utilizando a interface TestClient do FastAPI).
- **Testes de Interface (E2E):** Playwright para simular a interação real do usuário no navegador.
- **Versionamento e CI/CD:** GitHub Actions para execução automatizada de testes multiplataforma e Codecov para publicação dos relatórios de cobertura.

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
3. (Em breve) Execute a suíte de testes: `npm run test`
