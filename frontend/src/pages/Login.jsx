import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar.jsx'
import { login } from '../services/api.js'
import { useAuth } from '../context/useAuth.js'
import { validarEmail, validarSenha } from '../utils/validacao.js'
import './Login.css'

function Login() {
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [senhaTocada, setSenhaTocada] = useState(false)
  const [mensagem, setMensagem] = useState(null)
  const { entrar } = useAuth()
  const navigate = useNavigate()

  const senhaValida = validarSenha(senha)
  const formularioValido = validarEmail(email) && senhaValida

  async function handleSubmit(event) {
    event.preventDefault()
    setMensagem(null)

    try {
      const { access_token, usuario } = await login({ email, senha })
      entrar(usuario, access_token)
      navigate(usuario.is_freelancer ? '/dashboard/freelancer' : '/dashboard/cliente')
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: error.message })
    }
  }

  return (
    <div className="login">
      <Navbar />
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Entrar</h2>

        <label htmlFor="email">E-mail</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <label htmlFor="senha">Senha</label>
        <input
          id="senha"
          type="password"
          value={senha}
          onChange={(event) => setSenha(event.target.value)}
          onBlur={() => setSenhaTocada(true)}
        />
        {senhaTocada && senha.length > 0 && !senhaValida && (
          <p className="login-erro-campo">
            A senha deve ter no mínimo 6 caracteres
          </p>
        )}

        {mensagem && (
          <p className={`login-mensagem login-mensagem-${mensagem.tipo}`}>
            {mensagem.texto}
          </p>
        )}

        <button type="submit" disabled={!formularioValido}>
          Entrar
        </button>
      </form>
    </div>
  )
}

export default Login
