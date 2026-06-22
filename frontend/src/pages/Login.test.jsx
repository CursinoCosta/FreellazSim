import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Login from './Login.jsx'

describe('Login', () => {
  it('exibe mensagem de erro quando a senha é muito curta', async () => {
    const user = userEvent.setup()
    render(<Login />)

    await user.type(screen.getByLabelText('Senha'), '123')
    await user.tab()

    expect(
      screen.getByText('A senha deve ter no mínimo 6 caracteres')
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeDisabled()
  })

  it('não exibe mensagem de erro quando a senha é válida', async () => {
    const user = userEvent.setup()
    render(<Login />)

    await user.type(screen.getByLabelText('Senha'), 'senha123')
    await user.tab()

    expect(
      screen.queryByText('A senha deve ter no mínimo 6 caracteres')
    ).not.toBeInTheDocument()
  })
})
