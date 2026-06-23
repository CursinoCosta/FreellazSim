import ServiceCard from './ServiceCard.jsx'
import './ServiceCard.css'

export default function ServiceGrid({ servicos }) {
  console.log("ServiceGrid recebeu:", servicos); // Debug: Veja no console o que está a chegar

  if (!servicos || servicos.length === 0) {
    return <p>Nenhum serviço disponível no momento.</p>
  }

  return (
    <div className="service-grid">
      {servicos.map((s) => (
        <ServiceCard key={s.id} servico={s} />
      ))}
    </div>
  )
}