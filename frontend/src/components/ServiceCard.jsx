import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth.js'

export default function ServiceCard({ servico }) {
  const navigate = useNavigate()
  const { usuario } = useAuth()
  
  // PROTEÇÃO: Se o objeto "servico" não existir, não tentamos renderizar nada
  if (!servico) return null 

  const isDono = usuario && usuario.id === servico.freelancer_id

  return (
    <div className="service-card">
      <h3>{servico.titulo || 'Serviço sem título'}</h3>
      <p>{servico.descricao || 'Sem descrição'}</p>
      <div className="service-card-footer">
        <strong>R$ {servico.preco ? servico.preco.toFixed(2) : '0.00'}</strong>
        
        {isDono ? (
          <button 
            className="btn-edit" 
            onClick={() => navigate(`/editar-servico/${servico.id}`)}
          >
            Editar
          </button>
        ) : (
           <button onClick={() => navigate(`/servicos/${servico.id}`)}>Ver Detalhes</button>
        )}
      </div>
    </div>
  )
}