import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DashboardFreelancer from './DashboardFreelancer.jsx'

describe('DashboardFreelancer', () => {
  it('mostra mensagem de estado vazio quando não há serviços', () => {
    render(<DashboardFreelancer saldo={0} servicos={[]} />, { wrapper: MemoryRouter })

    expect(
      screen.getByText('Nenhum serviço disponível por aqui ainda.')
    ).toBeInTheDocument()
  })

  it('lista os serviços quando existem', () => {
    render(
      <DashboardFreelancer
        saldo={500}
        servicos={[{ id: 1, titulo: 'Logo', descricao: 'Logo top', preco: 150 }]}
      />,
      { wrapper: MemoryRouter }
    )

    expect(screen.getByText('Logo')).toBeInTheDocument()
  })
})
