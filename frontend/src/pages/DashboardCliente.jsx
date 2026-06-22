import Navbar from '../components/Navbar.jsx'
import './DashboardCliente.css'

function formatarPreco(preco) {
  return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function DashboardCliente({ saldo = 0, contratos = [] }) {
  return (
    <div className="dashboard-cliente">
      <Navbar />
      <section className="dashboard-cliente-conteudo">
        <div className="dashboard-cliente-saldo">
          <h2>Saldo disponível</h2>
          <span>{formatarPreco(saldo)}</span>
        </div>

        <h2>Meus contratos</h2>
        {contratos.length === 0 ? (
          <p className="dashboard-cliente-vazio">
            Você ainda não contratou nenhum serviço.
          </p>
        ) : (
          <ul className="dashboard-cliente-lista">
            {contratos.map((contrato) => (
              <li key={contrato.id}>
                <span>{contrato.servico_titulo}</span>
                <span>{formatarPreco(contrato.valor_pago)}</span>
                <span>{contrato.status}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}

export default DashboardCliente
