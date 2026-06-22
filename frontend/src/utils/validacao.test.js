import { describe, it, expect } from 'vitest'
import { validarSenha } from './validacao.js'

describe('validarSenha', () => {
  it('rejeita senhas com menos de 6 caracteres', () => {
    expect(validarSenha('123')).toBe(false)
  })

  it('aceita senhas com 6 ou mais caracteres', () => {
    expect(validarSenha('123456')).toBe(true)
  })
})
