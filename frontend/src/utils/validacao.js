const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function validarEmail(email) {
  return EMAIL_REGEX.test(email)
}

export function validarSenha(senha) {
  return senha.length >= 6
}
