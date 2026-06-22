import ServiceCard from './ServiceCard.jsx'
import './ServiceGrid.css'

function ServiceGrid({ servicos }) {
  if (servicos.length === 0) {
    return <p className="service-grid-vazio">Nenhum serviço disponível por aqui ainda.</p>
  }

  return (
    <div className="service-grid">
      {servicos.map((servico) => (
        <ServiceCard
          key={servico.id}
          id={servico.id}
          titulo={servico.titulo}
          descricao={servico.descricao}
          preco={servico.preco}
        />
      ))}
    </div>
  )
}

export default ServiceGrid
