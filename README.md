# FreellazSim
Sistema que simula um marketplace para trabalhos freelancers

## Integrantes
- Felipe Lopes Gomide
- João Correia Costa
- Mateus Cursino Gomes Costa
  
## Explicação do sistema
O sistema será um marketplace simplificado inspirado no Fiverr, conectando freelancers e clientes. As funcionalidades centrais incluem cadastro de usuários, autenticação e login, publicação de anúncios de serviços e um fluxo básico de contratação e validação do trabalho realizado, para repasse do dinheiro. O projeto é estruturado para priorizar a testabilidade, utilizando uma suíte de testes automatizados para validar regras de negócio e fluxos de interface, demonstrando como a cobertura de testes facilita a manutenção.

## Explicação das tecnologias utilizadas
- **Backend e Bando de Dados:** FastAPI (Python) e SQLite.

O FastAPI permite uma API rápida e tipada, enquanto o SQLite facilita a criação de bancos de dados em memória para testes isolados e velozes.

- **Frontend:** React para o desenvolvimento de uma interface dinâmica e modular.

Consideramos a  utilização de biblioteca com elementos frontend, como Material UI.

- **Testes de Backend:** Pytest, utilizado para implementar **testes unitários** e de **integração**, garantindo a integridade da lógica de negócios e dos endpoints, o FastApi fornece também uma interface TestClient, que permite fazer testes de integração dos endpoints criados no backend.

- **Testes de Interface (E2E)**: Playwright, responsável pelos testes de ponta a ponta, simulando a interação real do usuário no navegador para validar fluxos completos (como o de cadastro e contratação).

- **Versionamento e CI/CD**: O código e o histórico de evolução do sistema serão gerenciados em um repositório no GitHub, serão configuradas rotinas de execução de testes a cada commit e de cobertura via GitHub Actions.
