import Navbar from '../components/Navbar.jsx'
import './ServicoDetalhes.css'

function formatarPreco(preco) {
  return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function ServicoDetalhes({ servico = { titulo: '', descricao: '', preco: 0 } }) {
  return (
    <div className="servico-detalhes">
      <Navbar />
      <section className="servico-detalhes-conteudo">
        <div className="servico-detalhes-info">
          <h1>{servico.titulo}</h1>
          <p className="servico-detalhes-descricao">{servico.descricao}</p>
        </div>
        <aside className="servico-detalhes-resumo">
          <span className="servico-detalhes-preco">
            {formatarPreco(servico.preco)}
          </span>
          <button type="button">Contratar serviço</button>
        </aside>
      </section>
    </div>
  )
}

export default ServicoDetalhes
