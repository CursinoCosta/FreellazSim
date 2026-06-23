import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'
import { listarServicos, API_BASE_URL } from '../services/api.js'
import { useAuth } from '../context/useAuth.js'

export default function EditarServico() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({ descricao: '', preco: '' })
  
  useEffect(() => {
    listarServicos().then(servicos => {
      const s = servicos.find(item => item.id === Number(id))
      if (s) setFormData({ descricao: s.descricao, preco: s.preco })
    })
  }, [id])

  async function handleSubmit(e) {
    e.preventDefault()
    const { token } = JSON.parse(localStorage.getItem('freellazsim.auth'))
    
    await fetch(`${API_BASE_URL}/servicos/${id}`, {
      method: 'PATCH',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      },
      body: JSON.stringify(formData)
    })
    navigate('/dashboard/freelancer')
  }

  return (
    <div>
      <Navbar />
      <form onSubmit={handleSubmit} style={{ padding: '2rem' }}>
        <h2>Editar Serviço</h2>
        <label>Nova Descrição</label>
        <textarea value={formData.descricao} onChange={e => setFormData({...formData, descricao: e.target.value})} />
        
        <label>Novo Preço</label>
        <input type="number" value={formData.preco} onChange={e => setFormData({...formData, preco: parseFloat(e.target.value)})} />
        
        <button type="submit">Salvar Alterações</button>
      </form>
    </div>
  )
}