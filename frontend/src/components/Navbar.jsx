import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth.js'
import './Navbar.css'

export default function Navbar() {
  const { usuario, sair } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    sair()
    navigate('/')
  }

  return (
    <nav style={styles.nav}>
      <div style={styles.logoContainer}>
        <Link to="/" style={styles.logo}>FreellazSim</Link>
      </div>
      
      <div style={styles.linksContainer}>
        {usuario ? (
          <>
            <span style={styles.greeting}>Perfil: {usuario.nome}</span>
            <Link 
              to={usuario.is_freelancer ? '/dashboard/freelancer' : '/dashboard/cliente'} 
              style={styles.link}
            >
              Meu Dashboard
            </Link>
            <button onClick={handleLogout} style={styles.logoutButton}>
              Sair
            </button>
          </>
        ) : (
          <>
            <Link to="/cadastro" style={styles.link}>Cadastro</Link>
            <Link to="/login" style={styles.link}>Entrar</Link>
          </>
        )}
      </div>
    </nav>
  )
}

const styles = {
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 2rem',
    backgroundColor: 'var(--white, #ffffff)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  logo: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: 'var(--primary, #8b5cf6)',
    textDecoration: 'none'
  },
  linksContainer: {
    display: 'flex',
    gap: '1.5rem',
    alignItems: 'center',
  },
  link: {
    fontWeight: '500',
    textDecoration: 'none',
    color: 'inherit'
  },
  greeting: {
    fontWeight: 'bold',
    color: '#374151',
  },
  logoutButton: {
    fontWeight: 'bold',
    padding: '0.5rem 1rem',
    borderRadius: '4px',
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    cursor: 'pointer',
  }
}