import { useState } from 'react'
import Navbar from '../components/Navbar.jsx'
import { criarUsuario } from '../services/api.js'
import './Cadastro.css'

function Cadastro() {
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [isFreelancer, setIsFreelancer] = useState(false)
  const [mensagem, setMensagem] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()
    setMensagem(null)

    try {
      await criarUsuario({ nome, email, senha, is_freelancer: isFreelancer })
      setMensagem({ tipo: 'sucesso', texto: 'Cadastro realizado com sucesso!' })
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: error.message })
    }
  }

  return (
    <div className="cadastro">
      <Navbar />
      <form className="cadastro-form" onSubmit={handleSubmit}>
        <h2>Criar conta</h2>

        <label htmlFor="nome">Nome</label>
        <input
          id="nome"
          type="text"
          value={nome}
          onChange={(event) => setNome(event.target.value)}
        />

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
        />

        <label className="cadastro-checkbox">
          <input
            type="checkbox"
            checked={isFreelancer}
            onChange={(event) => setIsFreelancer(event.target.checked)}
          />
          Quero oferecer serviços como freelancer
        </label>

        {mensagem && (
          <p className={`cadastro-mensagem cadastro-mensagem-${mensagem.tipo}`}>
            {mensagem.texto}
          </p>
        )}

        <button type="submit">Cadastrar</button>
      </form>
    </div>
  )
}

export default Cadastro
