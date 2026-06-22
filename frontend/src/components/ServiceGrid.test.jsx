import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import ServiceGrid from './ServiceGrid.jsx'

const servicosFalsos = [
  { id: 1, titulo: 'Design de Logo', descricao: 'Logo profissional', preco: 150 },
  { id: 2, titulo: 'Desenvolvimento de API', descricao: 'API em FastAPI', preco: 1200.5 },
]

describe('ServiceGrid', () => {
  it('renderiza um card para cada serviço recebido', () => {
    render(<ServiceGrid servicos={servicosFalsos} />, { wrapper: MemoryRouter })

    expect(screen.getByText('Design de Logo')).toBeInTheDocument()
    expect(screen.getByText('Desenvolvimento de API')).toBeInTheDocument()
    expect(screen.getAllByRole('article')).toHaveLength(2)
  })

  it('cada card aponta para a página de detalhes do respectivo serviço', () => {
    render(<ServiceGrid servicos={servicosFalsos} />, { wrapper: MemoryRouter })

    expect(screen.getByRole('link', { name: /Design de Logo/ })).toHaveAttribute(
      'href',
      '/servicos/1'
    )
    expect(
      screen.getByRole('link', { name: /Desenvolvimento de API/ })
    ).toHaveAttribute('href', '/servicos/2')
  })

  it('clicar em um card navega para a rota de detalhes do serviço', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<ServiceGrid servicos={servicosFalsos} />} />
          <Route path="/servicos/:id" element={<p>Página de detalhes</p>} />
        </Routes>
      </MemoryRouter>
    )

    await user.click(screen.getByRole('link', { name: /Design de Logo/ }))

    expect(screen.getByText('Página de detalhes')).toBeInTheDocument()
  })

  it('mostra uma mensagem quando não há serviços', () => {
    render(<ServiceGrid servicos={[]} />, { wrapper: MemoryRouter })

    expect(
      screen.getByText('Nenhum serviço disponível por aqui ainda.')
    ).toBeInTheDocument()
  })
})
