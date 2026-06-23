export const API_BASE_URL = 'http://localhost:8000'

// Função auxiliar para injetar o token JWT nas requisições privadas
function getAuthHeaders() {
  const bruto = localStorage.getItem('freellazsim.auth')
  const headers = { 'Content-Type': 'application/json' }

  if (bruto) {
    const sessao = JSON.parse(bruto)
    if (sessao.token) {
      headers['Authorization'] = `Bearer ${sessao.token}`
    }
  }
  return headers
}

export async function criarUsuario(usuario) {
  const response = await fetch(`${API_BASE_URL}/usuarios/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(usuario),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail ?? 'Não foi possível criar o usuário')
  return data
}

export async function login(credenciais) {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credenciais),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail ?? 'Não foi possível entrar')
  return data
}

export async function buscarUsuario(usuarioId) {
  const response = await fetch(`${API_BASE_URL}/usuarios/${usuarioId}`, {
    headers: getAuthHeaders()
  })
  if (!response.ok) throw new Error('Não foi possível carregar os dados do perfil')
  return response.json()
}

export async function depositarFundos(usuarioId, valor) {
  const response = await fetch(`${API_BASE_URL}/usuarios/${usuarioId}/depositar`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify({ valor }),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail ?? 'Erro ao depositar')
  return data
}

export async function listarServicos() {
  const response = await fetch(`${API_BASE_URL}/servicos/`)
  if (!response.ok) throw new Error('Não foi possível carregar os serviços')
  return response.json()
}

export async function criarServico(servico) {
  const response = await fetch(`${API_BASE_URL}/servicos/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(servico),
  })
  const data = await response.json()
  
  if (!response.ok) {
    // Se o FastAPI devolver um array de erros (422), pegamos a mensagem exata
    const msg = Array.isArray(data.detail) ? data.detail[0].msg : (data.detail ?? 'Erro ao publicar serviço')
    throw new Error(msg)
  }
  
  return data
}

export async function contratarServico(contrato) {
  const response = await fetch(`${API_BASE_URL}/contratos/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(contrato),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail ?? 'Erro ao contratar serviço')
  return data
}

export async function cancelarContrato(contratoId) {
  const response = await fetch(`${API_BASE_URL}/contratos/${contratoId}/cancelar`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail ?? 'Erro ao cancelar')
  return data
}

export async function validarContrato(contratoId) {
  const response = await fetch(`${API_BASE_URL}/contratos/${contratoId}/validar`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail ?? 'Erro ao validar entrega')
  return data
}