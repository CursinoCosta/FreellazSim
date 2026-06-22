export const API_BASE_URL = 'http://localhost:8000'

export async function criarUsuario(usuario) {
  const response = await fetch(`${API_BASE_URL}/usuarios/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(usuario),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail ?? 'Não foi possível criar o usuário')
  }

  return data
}

export async function login(credenciais) {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credenciais),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail ?? 'Não foi possível entrar')
  }

  return data
}
