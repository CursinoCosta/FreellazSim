import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar.jsx'
import ServiceGrid from '../components/ServiceGrid.jsx'
import { buscarUsuario, listarServicos, criarServico } from '../services/api.js'
import { useAuth } from '../context/useAuth.js'
import './DashboardFreelancer.css'

function formatarPreco(preco) {
  return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export default function DashboardFreelancer() {
  const { usuario } = useAuth()
  const [saldo, setSaldo] = useState(0)
  const [meusServicos, setMeusServicos] = useState([])
  
  // Estados do formulário
  const [titulo, setTitulo] = useState('')
  const [descricao, setDescricao] = useState('')
  const [preco, setPreco] = useState('')
  const [mensagem, setMensagem] = useState(null)

  const carregarDados = async () => {
    if (!usuario) return
    try {
      const dadosUsuario = await buscarUsuario(usuario.id)
      setSaldo(dadosUsuario.saldo_conta)

      const todosServicos = await listarServicos()
      // Filtra para exibir apenas os serviços que pertencem a este freelancer
      const filtrados = todosServicos.filter(s => s.freelancer_id === usuario.id)
      setMeusServicos(filtrados)
    } catch (error) {
      console.error("Erro ao carregar dados", error)
    }
  }

  useEffect(() => {
    carregarDados()
  }, [usuario])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setMensagem(null)

    try {
      await criarServico({
        titulo,
        descricao,
        preco: parseFloat(preco)
      })
      setMensagem({ tipo: 'sucesso', texto: 'Serviço publicado com sucesso!' })
      setTitulo('')
      setDescricao('')
      setPreco('')
      carregarDados() // Recarrega a grade para o serviço aparecer na hora
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: error.message })
    }
  }

  return (
    <div className="dashboard-freelancer">
      <Navbar />
      <section className="dashboard-freelancer-conteudo">
        
        <div className="dashboard-freelancer-saldo">
          <h2>Meu Saldo: {formatarPreco(saldo)}</h2>
        </div>

        <div className="dashboard-freelancer-layout">
          {/* Coluna Esquerda: Formulário de Novo Serviço */}
          <div className="dashboard-freelancer-form-card">
            <h3>Publicar Novo Serviço</h3>
            <form onSubmit={handleSubmit} className="freelancer-form">
              <label>Título do Serviço</label>
              <input 
                type="text" 
                value={titulo} 
                onChange={e => setTitulo(e.target.value)} 
                required 
              />

              <label>Descrição</label>
              <textarea 
                value={descricao} 
                onChange={e => setDescricao(e.target.value)} 
                required 
                rows="4"
              />

              <label>Preço (R$)</label>
              <input 
                type="number" 
                step="0.01" 
                min="0.01" 
                value={preco} 
                onChange={e => setPreco(e.target.value)} 
                required 
              />

              {mensagem && (
                <p className={`mensagem-${mensagem.tipo}`}>
                  {mensagem.texto}
                </p>
              )}

              <button type="submit">Publicar</button>
            </form>
          </div>

          {/* Coluna Direita: Grade de Serviços */}
          <div className="dashboard-freelancer-servicos">
            <h3>Meus serviços anunciados</h3>
            <div className="dashboard-grid-container">
               <ServiceGrid servicos={meusServicos} />
            </div>
          </div>
        </div>

      </section>
    </div>
  )
}