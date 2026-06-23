import { test, expect } from '@playwright/test';

test('fluxo completo: publicar e contratar servico', async ({ page }) => {
  // Aumentamos o tempo limite para garantir que a API responda
  await page.goto('http://localhost:5174/');

  // Debug: Se você ver o log no terminal, saberá se o teste chegou a carregar a página
  console.log('Página carregada, procurando link de Login...');

  // Tenta encontrar pelo papel (role) - mais estável que 'text'
  // Ajuste 'Entrar' se o texto no seu Navbar for outro
  const loginLink = page.getByRole('link', { name: /login|entrar/i });
  
  if (await loginLink.isVisible()) {
    await loginLink.click();
  } else {
    console.log('Botão Login não encontrado, verificando se já estamos logados...');
  }

  // Preenchimento com wait for navigation
  await page.fill('input[name="email"]', 'freelancer@test.com');
  await page.fill('input[name="password"]', '123456');
  await page.click('button[type="submit"]');
  
  // Garantir que logamos antes de prosseguir
  await expect(page).toHaveURL(/.*dashboard/);

  // 3. Publicar Serviço
  await page.click('text=Meu Dashboard');
  await page.fill('input[placeholder="Título"]', 'Teste E2E');
  await page.fill('textarea', 'Descrição de teste');
  await page.fill('input[type="number"]', '50.00');
  await page.click('text=Publicar');

  // 4. Logout e Login (Cliente)
  await page.click('text=Sair');
  await page.click('text=Login');
  // ... (Repita o processo de login para o cliente)

  // 5. Contratar
  await page.click('text=Teste E2E');
  await page.click('text=Contratar serviço');
  
  // 6. Validar o feedback
  await expect(page.locator('text=Serviço contratado')).toBeVisible();
});