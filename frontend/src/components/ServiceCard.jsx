import { Link } from 'react-router-dom'
import './ServiceCard.css'

function formatarPreco(preco) {
  return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function ServiceCard({ id, titulo, descricao, preco }) {
  return (
    <Link className="service-card-link" to={`/servicos/${id}`}>
      <article className="service-card">
        <h3 className="service-card-titulo">{titulo}</h3>
        <p className="service-card-descricao">{descricao}</p>
        <span className="service-card-preco">{formatarPreco(preco)}</span>
      </article>
    </Link>
  )
}

export default ServiceCard
