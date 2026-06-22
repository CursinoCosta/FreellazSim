import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DashboardCliente from './DashboardCliente.jsx'

describe('DashboardCliente', () => {
  it('mostra mensagem de estado vazio quando não há contratos', () => {
    render(<DashboardCliente saldo={0} contratos={[]} />, { wrapper: MemoryRouter })

    expect(
      screen.getByText('Você ainda não contratou nenhum serviço.')
    ).toBeInTheDocument()
  })

  it('lista os contratos quando existem', () => {
    render(
      <DashboardCliente
        saldo={100}
        contratos={[
          { id: 1, servico_titulo: 'Logo', valor_pago: 100, status: 'pendente' },
        ]}
      />,
      { wrapper: MemoryRouter }
    )

    expect(screen.getByText('Logo')).toBeInTheDocument()
    expect(
      screen.queryByText('Você ainda não contratou nenhum serviço.')
    ).not.toBeInTheDocument()
  })
})
