import './ServiceCard.css'

function formatarPreco(preco) {
  return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function ServiceCard({ titulo, descricao, preco }) {
  return (
    <article className="service-card">
      <h3 className="service-card-titulo">{titulo}</h3>
      <p className="service-card-descricao">{descricao}</p>
      <span className="service-card-preco">{formatarPreco(preco)}</span>
    </article>
  )
}

export default ServiceCard
