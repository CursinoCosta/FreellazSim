import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext.jsx'
import RotaPrivada from './RotaPrivada.jsx'

const CHAVE_STORAGE = 'freellazsim.auth'

function PaginaPrivada() {
  return <p>Conteúdo privado</p>
}

function PaginaLogin() {
  return <p>Tela de login</p>
}

function renderizarComEntradaEm(rotaInicial) {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={[rotaInicial]}>
        <Routes>
          <Route path="/login" element={<PaginaLogin />} />
          <Route
            path="/privada"
            element={
              <RotaPrivada>
                <PaginaPrivada />
              </RotaPrivada>
            }
          />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  )
}

describe('RotaPrivada', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('redireciona para /login quando não há usuário autenticado', () => {
    renderizarComEntradaEm('/privada')

    expect(screen.getByText('Tela de login')).toBeInTheDocument()
    expect(screen.queryByText('Conteúdo privado')).not.toBeInTheDocument()
  })

  it('renderiza a rota normalmente quando o usuário já está autenticado', () => {
    localStorage.setItem(
      CHAVE_STORAGE,
      JSON.stringify({ usuario: { id: 1, nome: 'Maria' }, token: 'token-valido' })
    )

    renderizarComEntradaEm('/privada')

    expect(screen.getByText('Conteúdo privado')).toBeInTheDocument()
  })
})
