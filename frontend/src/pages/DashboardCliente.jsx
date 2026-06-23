import { useState, useEffect } from 'react'
import Navbar from '../components/Navbar.jsx'
import { buscarUsuario, listarContratos, depositarFundos } from '../services/api.js'
import { useAuth } from '../context/useAuth.js'
import './DashboardCliente.css'

function formatarPreco(preco) {
  return preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export default function DashboardCliente() {
  const { usuario } = useAuth()
  const [saldo, setSaldo] = useState(0)
  const [meusContratos, setMeusContratos] = useState([])
  const [loading, setLoading] = useState(true)

  const carregarDados = async () => {
    if (!usuario) return
    try {
      // Busca saldo atualizado
      const dadosUsuario = await buscarUsuario(usuario.id)
      setSaldo(dadosUsuario.saldo_conta)

      // Busca histórico de contratos deste cliente
      const todosContratos = await listarContratos()
      const filtrados = todosContratos.filter(c => c.cliente_id === usuario.id)
      setMeusContratos(filtrados)
    } catch (error) {
      console.error("Erro ao carregar dados", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    carregarDados()
  }, [usuario])

  // Função disparada pelo novo botão
  async function handleAdicionarSaldo() {
    const valorDigitado = window.prompt("Digite o valor a ser depositado (Ex: 500):")
    const valor = parseFloat(valorDigitado)
    
    if (isNaN(valor) || valor <= 0) return

    try {
      await depositarFundos(usuario.id, valor)
      carregarDados() // Recarrega o saldo na tela imediatamente
    } catch (error) {
      alert("Erro ao depositar: " + error.message)
    }
  }

  return (
    <div className="dashboard-cliente">
      <Navbar />
      <section className="dashboard-cliente-conteudo" style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        
        <div className="dashboard-cliente-saldo" style={{ backgroundColor: '#fff', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ margin: 0, color: '#8b5cf6' }}>Saldo disponível</h2>
            <span style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{formatarPreco(saldo)}</span>
          </div>
          <button 
            onClick={handleAdicionarSaldo}
            style={{ backgroundColor: '#10b981', color: 'white', padding: '0.75rem 1.5rem', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            + Adicionar Fundos
          </button>
        </div>

        <h2 style={{ marginTop: '2rem' }}>Meus contratos</h2>
        {loading ? (
          <p>Carregando contratos...</p>
        ) : meusContratos.length === 0 ? (
          <p className="dashboard-cliente-vazio">Você ainda não contratou nenhum serviço.</p>
        ) : (
          <ul className="dashboard-cliente-lista" style={{ listStyle: 'none', padding: 0 }}>
            {meusContratos.map((contrato) => (
              <li key={contrato.id} style={{ display: 'flex', gap: '2rem', border: '1px solid #e5e7eb', backgroundColor: '#fff', padding: '1rem', marginBottom: '1rem', borderRadius: '4px' }}>
                <span><strong>Serviço ID:</strong> {contrato.servico_id}</span>
                <span><strong>Valor Pago:</strong> {formatarPreco(contrato.valor_pago)}</span>
                <span>
                  <strong>Status: </strong> 
                  <span style={{ color: contrato.status === 'pendente' ? '#d97706' : contrato.status === 'validado' ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                    {contrato.status.toUpperCase()}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}