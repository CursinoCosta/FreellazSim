# FreellazSim

[![Testes](https://github.com/CursinoCosta/FreellazSim/actions/workflows/ci.yml/badge.svg)](https://github.com/CursinoCosta/FreellazSim/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CursinoCosta/FreellazSim/branch/main/graph/badge.svg)](https://codecov.io/gh/CursinoCosta/FreellazSim)

## Integrantes

- Felipe Lopes Gomide
- João Correia Costa
- Mateus Cursino Gomes Costa

## Sobre o Sistema

O FreellazSim é um marketplace simplificado inspirado no Fiverr, conectando freelancers e clientes. As funcionalidades centrais incluem cadastro e autenticação de usuários, publicação de anúncios de serviços e um fluxo de contratação, validação e cancelamento de serviços com repasse financeiro (descontando uma taxa de plataforma). Nosso objetivo principal é priorizar a testabilidade, utilizando uma suíte de testes automatizados para validar regras de negócio e fluxos de interface, evidenciando como a cobertura de testes facilita a manutenção do software.

## Tecnologias Utilizadas

- **Backend e Banco de Dados:** FastAPI (Python) e SQLite para criação de um banco em memória rápido e isolado para testes.
- **Autenticação:** Senhas com hash via bcrypt e sessões via tokens JWT.
- **Frontend:** React configurado via Vite, com roteamento via React Router.
- **Testes de Backend:** Pytest (testes unitários e de integração utilizando a interface TestClient do FastAPI).
- **Testes de Frontend:** Vitest e React Testing Library para testes de componentes.
- **Versionamento e CI/CD:** GitHub Actions para execução automatizada de testes multiplataforma e Codecov para publicação dos relatórios de cobertura.

## Contribuindo

Instruções para configurar o ambiente e executar os testes localmente estão em [CONTRIBUTING.md](./CONTRIBUTING.md).
