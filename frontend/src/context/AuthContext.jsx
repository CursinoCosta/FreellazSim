import { createContext, useState } from 'react'

// 1. Criamos a raiz do Contexto aqui (única fonte da verdade)
export const AuthContext = createContext()

const CHAVE_STORAGE = 'freellazsim.auth'

function carregarSessaoSalva() {
  const bruto = localStorage.getItem(CHAVE_STORAGE)
  try {
    const dados = bruto ? JSON.parse(bruto) : null
    return dados || { usuario: null, token: null }
  } catch (error) {
    return { usuario: null, token: null }
  }
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

  // Blindagem: Garante que o objeto "value" sempre tenha chaves válidas, mesmo se "sessao" quebrar
  const value = {
    usuario: sessao?.usuario || null,
    token: sessao?.token || null,
    entrar,
    sair
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}