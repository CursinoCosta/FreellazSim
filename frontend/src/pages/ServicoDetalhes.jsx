import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'
import { 
  listarServicos, 
  listarContratos, 
  contratarServico, 
  cancelarContrato, 
  validarContrato 
} from '../services/api.js'
import { useAuth } from '../context/useAuth.js'
import './ServicoDetalhes.css'

function formatarPreco(preco) {
  return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export default function ServicoDetalhes() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { usuario } = useAuth()
  
  const [servico, setServico] = useState(null)
  const [contratos, setContratos] = useState([])
  const [loading, setLoading] = useState(true)
  const [mensagem, setMensagem] = useState(null)

  // Função que busca os dados e recarrega a tela sem dar F5
  const carregarDados = async () => {
    setMensagem(null)
    try {
      // 1. Busca os dados do serviço atual
      const listaServicos = await listarServicos()
      const servicoEncontrado = listaServicos.find(s => s.id === Number(id))
      
      if (!servicoEncontrado) {
        setServico(null)
        setLoading(false)
        return
      }
      setServico(servicoEncontrado)

      // 2. Se o usuário estiver logado, busca os contratos relacionados a este serviço
      if (usuario) {
        const listaContratos = await listarContratos()
        const contratosDesteServico = listaContratos.filter(c => c.servico_id === servicoEncontrado.id)
        setContratos(contratosDesteServico)
      }
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: 'Erro ao carregar dados do servidor.' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    carregarDados()
  }, [id, usuario])

  // --- AÇÕES DO CLIENTE ---
  async function handleContratar() {
    if (!usuario) {
      setMensagem({ tipo: 'erro', texto: 'Faça login para contratar.' })
      return
    }
    try {
      await contratarServico({
        servico_id: servico.id,
        cliente_id: usuario.id,
        valor_pago: servico.preco
      })
      setMensagem({ tipo: 'sucesso', texto: 'Serviço contratado! O freelancer foi notificado.' })
      carregarDados() // Atualiza a tela para mostrar o botão de cancelar
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: error.message })
    }
  }

  async function handleCancelar(contratoId) {
    try {
      await cancelarContrato(contratoId)
      setMensagem({ tipo: 'sucesso', texto: 'Contrato cancelado e dinheiro estornado para sua carteira.' })
      carregarDados()
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: error.message })
    }
  }

  // --- AÇÕES DO FREELANCER ---
  async function handleValidar(contratoId) {
    try {
      await validarContrato(contratoId)
      setMensagem({ tipo: 'sucesso', texto: 'Entrega validada! O pagamento (com taxa) já está no seu saldo.' })
      carregarDados()
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: error.message })
    }
  }

  // Telas de carregamento e erro
  if (loading) return <div><Navbar /><p style={{padding: '2rem', textAlign: 'center'}}>Carregando detalhes...</p></div>
  if (!servico) return <div><Navbar /><p style={{padding: '2rem', textAlign: 'center'}}>Serviço não encontrado.</p></div>

  // Variáveis de controle de exibição
  const isDonoDoServico = usuario && usuario.id === servico.freelancer_id
  const meuContratoPendente = !isDonoDoServico && contratos.find(c => c.cliente_id === usuario?.id && c.status === 'pendente')

  return (
    <div className="servico-detalhes">
      <Navbar />
      <section className="servico-detalhes-conteudo">
        
        {/* Coluna Esquerda: Informações do Serviço */}
        <div className="servico-detalhes-info">
          <h1>{servico.titulo}</h1>
          <p className="servico-detalhes-descricao">{servico.descricao}</p>
        </div>
        
        {/* Coluna Direita: Painel de Ações (Muda se for Dono ou Cliente) */}
        <aside className="servico-detalhes-resumo">
          <span className="servico-detalhes-preco">
            {formatarPreco(servico.preco)}
          </span>

          {/* VISÃO DO CLIENTE */}
          {!isDonoDoServico && (
            <>
              {meuContratoPendente ? (
                <div style={{ marginTop: '1rem', borderTop: '1px solid #ccc', paddingTop: '1rem' }}>
                  <p style={{ color: '#d97706', fontWeight: 'bold', marginBottom: '1rem' }}>
                    Você já tem um pedido pendente para este serviço.
                  </p>
                  <button 
                    type="button" 
                    style={{ backgroundColor: '#ef4444' }} // Botão vermelho
                    onClick={() => handleCancelar(meuContratoPendente.id)}
                  >
                    Cancelar Pedido e Estornar
                  </button>
                </div>
              ) : (
                <button type="button" onClick={handleContratar}>
                  Contratar serviço
                </button>
              )}
            </>
          )}

          {/* VISÃO DO FREELANCER DONO DO ANÚNCIO */}
          {isDonoDoServico && (
            <div style={{ marginTop: '1rem', borderTop: '1px solid #e5e7eb', paddingTop: '1rem' }}>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Pedidos Recebidos</h3>
              
              {contratos.length === 0 ? (
                <p style={{ fontSize: '0.9rem', color: '#6b7280' }}>Nenhum cliente contratou ainda.</p>
              ) : (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                  {contratos.map(c => (
                    <li key={c.id} style={{ border: '1px solid #e5e7eb', padding: '0.8rem', borderRadius: '4px', fontSize: '0.9rem' }}>
                      <strong>Cliente ID:</strong> {c.cliente_id} <br/>
                      <strong>Status:</strong> <span style={{ color: c.status === 'pendente' ? '#d97706' : c.status === 'validado' ? '#10b981' : '#ef4444' }}>{c.status.toUpperCase()}</span>
                      
                      {c.status === 'pendente' && (
                        <button 
                          style={{ marginTop: '0.5rem', padding: '0.4rem', fontSize: '0.8rem', width: '100%', backgroundColor: '#10b981' }}
                          onClick={() => handleValidar(c.id)}
                        >
                          Concluir Entrega
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Feedback Visual */}
          {mensagem && (
            <p style={{ marginTop: '1rem', textAlign: 'center', color: mensagem.tipo === 'erro' ? '#ef4444' : '#10b981', fontWeight: 'bold' }}>
              {mensagem.texto}
            </p>
          )}
        </aside>

      </section>
    </div>
  )
}