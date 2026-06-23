import { useContext } from 'react'
import { AuthContext } from './AuthContext.jsx'

export function useAuth() {
  const context = useContext(AuthContext)
  
  // Fallback de segurança vital: se o Contexto se desconectar por algum motivo, 
  // devolvemos funções vazias em vez de "null", impedindo a Tela Branca.
  if (!context) {
    return { usuario: null, token: null, entrar: () => {}, sair: () => {} }
  }
  
  return context
}