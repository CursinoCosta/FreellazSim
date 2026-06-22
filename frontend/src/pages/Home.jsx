import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar.jsx'
import ServiceGrid from '../components/ServiceGrid.jsx'
import { listarServicos } from '../services/api.js'
import heroImage from '../assets/hero.png'
import './Home.css'

function Home() {
  const [servicos, setServicos] = useState([])

  useEffect(() => {
    listarServicos()
      .then(setServicos)
      .catch(() => setServicos([]))
  }, [])

  return (
    <div className="home">
      <Navbar />
      <section className="home-hero">
        <div className="home-hero-text">
          <h1>Encontre o freelancer certo para o seu projeto</h1>
          <p>
            Contrate serviços de qualidade ou ofereça o seu talento na
            FreellazSim.
          </p>
        </div>
        <img className="home-hero-image" src={heroImage} alt="" />
      </section>
      <ServiceGrid servicos={servicos} />
    </div>
  )
}

export default Home
