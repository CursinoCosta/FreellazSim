import { useState } from 'react'
import { AuthContext } from './auth-context.js'

const CHAVE_STORAGE = 'freellazsim.auth'

function carregarSessaoSalva() {
  const bruto = localStorage.getItem(CHAVE_STORAGE)
  return bruto ? JSON.parse(bruto) : { usuario: null, token: null }
}

export function AuthProvider({ children }) {
  const [sessao, setSessao] = useState(carregarSessaoSalva)

  function entrar(usuario, token) {
    const novaSessao = { usuario, token }
    localStorage.setItem(CHAVE_STORAGE, JSON.stringify(novaSessao))
    setSessao(novaSessao)
  }

  function sair() {
    localStorage.removeItem(CHAVE_STORAGE)
    setSessao({ usuario: null, token: null })
  }

  return (
    <AuthContext.Provider value={{ ...sessao, entrar, sair }}>
      {children}
    </AuthContext.Provider>
  )
}
