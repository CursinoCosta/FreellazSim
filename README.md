# FreellazSim
Sistema que simula um marketplace de frelancers
## Integrantes
- Felipe Lopes Gomide
- João Correia Costa
- Mateus Cursino Gomes Costa
## Explicação do sistema
O sistema será um marketplace simplificado inspirado no Fiverr, conectando freelancers e clientes. As funcionalidades centrais incluem cadastro de usuários, publicação de anúncios de serviços e um fluxo básico de contratação. O projeto é estruturado para priorizar a testabilidade, utilizando uma suíte de testes automatizados para validar regras de negócio e fluxos de interface, demonstrando como a cobertura de testes facilita a manutenção.
## Explicação das tecnologias utilizadas
Backend e Banco de Dados: FastAPI (Python) e SQLite. O FastAPI permite uma API rápida e tipada, enquanto o SQLite facilita a criação de bancos de dados em memória para testes isolados e velozes.
Frontend: React para o desenvolvimento de uma interface dinâmica e modular.
Testes de Backend: pytest, utilizado para implementar testes unitários e de integração, garantindo a integridade da lógica de negócios e dos endpoints.
Testes de Interface (E2E): Playwright, responsável pelos testes de ponta a ponta, simulando a interação real do usuário no navegador para validar fluxos completos (como o de cadastro e contratação).
Versionamento: O código e o histórico de evolução do sistema serão gerenciados em um repositório no GitHub.
