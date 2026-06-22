import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ServiceGrid from './ServiceGrid.jsx'

const servicosFalsos = [
  { id: 1, titulo: 'Design de Logo', descricao: 'Logo profissional', preco: 150 },
  { id: 2, titulo: 'Desenvolvimento de API', descricao: 'API em FastAPI', preco: 1200.5 },
]

describe('ServiceGrid', () => {
  it('renderiza um card para cada serviço recebido', () => {
    render(<ServiceGrid servicos={servicosFalsos} />)

    expect(screen.getByText('Design de Logo')).toBeInTheDocument()
    expect(screen.getByText('Desenvolvimento de API')).toBeInTheDocument()
    expect(screen.getAllByRole('article')).toHaveLength(2)
  })

  it('mostra uma mensagem quando não há serviços', () => {
    render(<ServiceGrid servicos={[]} />)

    expect(
      screen.getByText('Nenhum serviço disponível por aqui ainda.')
    ).toBeInTheDocument()
  })
})
