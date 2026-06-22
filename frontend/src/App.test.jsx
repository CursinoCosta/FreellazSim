import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App.jsx'

describe('App routing', () => {
  it('navega da Home para o Login ao clicar em "Entrar" na Navbar', async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByRole('link', { name: 'Entrar' }))

    expect(screen.getByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('navega da Home para o Cadastro ao clicar em "Cadastrar" na Navbar', async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByRole('link', { name: 'Cadastrar' }))

    expect(screen.getByRole('heading', { name: 'Criar conta' })).toBeInTheDocument()
  })
})
