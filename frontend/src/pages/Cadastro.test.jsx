import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import Cadastro from './Cadastro.jsx'

describe('Cadastro', () => {
  it('mantém o botão de cadastro desabilitado quando o formulário está vazio', () => {
    render(<Cadastro />, { wrapper: MemoryRouter })

    expect(screen.getByRole('button', { name: 'Cadastrar' })).toBeDisabled()
  })

  it('habilita o botão de cadastro quando todos os campos são válidos', async () => {
    const user = userEvent.setup()
    render(<Cadastro />, { wrapper: MemoryRouter })

    await user.type(screen.getByLabelText('Nome'), 'Maria Silva')
    await user.type(screen.getByLabelText('E-mail'), 'maria@teste.com')
    await user.type(screen.getByLabelText('Senha'), 'senha123')

    expect(screen.getByRole('button', { name: 'Cadastrar' })).toBeEnabled()
  })

  it('exibe mensagem de erro quando a senha é muito curta', async () => {
    const user = userEvent.setup()
    render(<Cadastro />, { wrapper: MemoryRouter })

    await user.type(screen.getByLabelText('Senha'), '123')
    await user.tab()

    expect(
      screen.getByText('A senha deve ter no mínimo 6 caracteres')
    ).toBeInTheDocument()
  })
})
