import Navbar from '../components/Navbar.jsx'
import ServiceGrid from '../components/ServiceGrid.jsx'
import './DashboardFreelancer.css'

function formatarPreco(preco) {
  return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function DashboardFreelancer({ saldo = 0, servicos = [] }) {
  return (
    <div className="dashboard-freelancer">
      <Navbar />
      <section className="dashboard-freelancer-conteudo">
        <div className="dashboard-freelancer-saldo">
          <h2>Saldo disponível</h2>
          <span>{formatarPreco(saldo)}</span>
        </div>

        <h2>Meus serviços anunciados</h2>
        <ServiceGrid servicos={servicos} />
      </section>
    </div>
  )
}

export default DashboardFreelancer
