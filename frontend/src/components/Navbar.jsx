import { Link } from 'react-router-dom'
import './Navbar.css'

function Navbar() {
  return (
    <header className="navbar">
      <Link className="navbar-logo" to="/">
        FreellazSim
      </Link>
      <nav className="navbar-links">
        <Link to="/">Início</Link>
        <Link to="/login">Entrar</Link>
        <Link className="navbar-cta" to="/cadastro">
          Cadastrar
        </Link>
      </nav>
    </header>
  )
}

export default Navbar
