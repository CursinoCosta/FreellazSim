import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider } from './AuthContext.jsx'
import { useAuth } from './useAuth.js'

const CHAVE_STORAGE = 'freellazsim.auth'

function Consumidor() {
  const { usuario, token, entrar, sair } = useAuth()

  return (
    <div>
      <p data-testid="usuario">{usuario ? usuario.nome : 'deslogado'}</p>
      <p data-testid="token">{token ?? 'sem-token'}</p>
      <button onClick={() => entrar({ id: 1, nome: 'Maria' }, 'abc123')}>Entrar</button>
      <button onClick={sair}>Sair</button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('começa deslogado quando não há sessão salva', () => {
    render(<AuthProvider><Consumidor /></AuthProvider>)

    expect(screen.getByTestId('usuario')).toHaveTextContent('deslogado')
    expect(screen.getByTestId('token')).toHaveTextContent('sem-token')
  })

  it('entrar() atualiza o contexto e persiste no localStorage', async () => {
    const user = userEvent.setup()
    render(<AuthProvider><Consumidor /></AuthProvider>)

    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(screen.getByTestId('usuario')).toHaveTextContent('Maria')
    expect(screen.getByTestId('token')).toHaveTextContent('abc123')
    expect(JSON.parse(localStorage.getItem(CHAVE_STORAGE))).toEqual({
      usuario: { id: 1, nome: 'Maria' },
      token: 'abc123',
    })
  })

  it('sair() limpa o contexto e o localStorage', async () => {
    const user = userEvent.setup()
    render(<AuthProvider><Consumidor /></AuthProvider>)

    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await user.click(screen.getByRole('button', { name: 'Sair' }))

    expect(screen.getByTestId('usuario')).toHaveTextContent('deslogado')
    expect(localStorage.getItem(CHAVE_STORAGE)).toBeNull()
  })

  it('recupera a sessão salva no localStorage ao montar', () => {
    localStorage.setItem(
      CHAVE_STORAGE,
      JSON.stringify({ usuario: { id: 2, nome: 'João' }, token: 'xyz' })
    )

    render(<AuthProvider><Consumidor /></AuthProvider>)

    expect(screen.getByTestId('usuario')).toHaveTextContent('João')
    expect(screen.getByTestId('token')).toHaveTextContent('xyz')
  })
})
