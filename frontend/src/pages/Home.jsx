import Navbar from '../components/Navbar.jsx'
import heroImage from '../assets/hero.png'
import './Home.css'

function Home() {
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
    </div>
  )
}

export default Home
