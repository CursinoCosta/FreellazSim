import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'
import ServiceGrid from '../components/ServiceGrid.jsx'
import { listarServicos } from '../services/api.js'
import { useAuth } from '../context/useAuth.js'
import './Home.css'

export default function Home() {
  const [servicos, setServicos] = useState([])
  const { usuario } = useAuth()

  useEffect(() => {
    listarServicos()
      .then(setServicos)
      .catch(() => setServicos([]))
  }, [])

  return (
    <div className="home">
      <Navbar />
      <main>
        {/* Banner Principal (Hero) */}
        <section className="home-hero">
          <div className="home-hero-content">
            <h1>Encontre o talento certo para o seu projeto</h1>
            <p>
              Milhares de profissionais prontos para transformar sua ideia em realidade. 
              Contrate especialistas ou ofereça seus serviços na FreellazSim.
            </p>
            
            {/* Esconde os botões se o usuário já estiver logado */}
            {!usuario && (
              <div className="home-hero-actions">
                <Link to="/cadastro" className="btn-primary">Começar agora</Link>
                <Link to="/login" className="btn-secondary">Já tenho conta</Link>
              </div>
            )}
          </div>
        </section>

        {/* Vitrine de Serviços */}
        <section className="home-servicos">
          <div className="home-section-header">
            <h2>Serviços em Destaque</h2>
            <p>Explore as opções disponíveis e encontre o que você precisa.</p>
          </div>
          
          <ServiceGrid servicos={servicos.filter(s => s && s.id)} />
        </section>
      </main>
    </div>
  )
}