import './Navbar.css'

function Navbar() {
  return (
    <header className="navbar">
      <a className="navbar-logo" href="#">
        FreellazSim
      </a>
      <nav className="navbar-links">
        <a href="#">Início</a>
        <a href="#">Serviços</a>
        <a href="#">Entrar</a>
        <a className="navbar-cta" href="#">
          Cadastrar
        </a>
      </nav>
    </header>
  )
}

export default Navbar
