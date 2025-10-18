# ✅ CHECKLIST DE DEPLOY - Railway + Vercel

Marque cada item conforme completa!

---

## 📋 PARTE 1: Railway - Criar Conta

- [ ] Acessei https://railway.app/
- [ ] Cliquei em "Start a New Project"
- [ ] Fiz login com GitHub
- [ ] Autorizei o Railway
- [ ] ✅ Estou no Dashboard do Railway

---

## 📋 PARTE 2: Railway - Criar Banco

- [ ] Cliquei em "New Project"
- [ ] Escolhi "Provision PostgreSQL"
- [ ] Aguardei 30 segundos (banco criando)
- [ ] ✅ Card PostgreSQL (roxo) apareceu

---

## 📋 PARTE 3: Railway - Copiar String

- [ ] Cliquei no card PostgreSQL
- [ ] Cliquei na aba "Connect" (barra lateral direita)
- [ ] Encontrei "Postgres Connection URL"
- [ ] Copiei a string completa
- [ ] ✅ String copiada (ex: postgresql://postgres:abc123@...)

---

## 📋 PARTE 4: Testar Localmente

- [ ] Abri PowerShell
- [ ] Rodei: `cd C:\Users\darkl\Desktop\Stoke\estoque_project`
- [ ] Rodei: `$env:DATABASE_URL="minha-string-railway"`
- [ ] Rodei: `python manage.py migrate`
- [ ] ✅ Migrations rodaram com sucesso! (viu "OK" várias vezes)

---

## 📋 PARTE 5: Git - Atualizar Código

- [ ] Rodei: `cd ..` (voltar para diretório raiz)
- [ ] Rodei: `git add .`
- [ ] Rodei: `git commit -m "Deploy com Railway"`
- [ ] Rodei: `git push origin main`
- [ ] ✅ Código enviado para GitHub

---

## 📋 PARTE 6: Vercel - Criar Conta

- [ ] Acessei https://vercel.com/
- [ ] Cliquei em "Sign Up"
- [ ] Fiz login com GitHub (mesmo do Railway)
- [ ] Autorizei o Vercel
- [ ] ✅ Estou no Dashboard do Vercel

---

## 📋 PARTE 7: Vercel - Importar Projeto

- [ ] Cliquei em "Add New..." → "Project"
- [ ] Encontrei o repositório "Stoke"
- [ ] Cliquei em "Import"
- [ ] ✅ Estou na página de configuração

---

## 📋 PARTE 8: Vercel - Variáveis de Ambiente

- [ ] Expandi a seção "Environment Variables"
- [ ] Adicionei: `SECRET_KEY = 7^9hoti#xz57__5$tjcjh89mz9i$!v3_40o8b7ppyzdhzs5)s0`
- [ ] Adicionei: `DEBUG = False`
- [ ] Adicionei: `ALLOWED_HOSTS = .vercel.app`
- [ ] Adicionei: `DJANGO_SETTINGS_MODULE = estoque_project.settings`
- [ ] Adicionei: `DATABASE_URL = [minha-string-railway]`
- [ ] ✅ 5 variáveis adicionadas!

---

## 📋 PARTE 9: Vercel - Deploy

- [ ] Cliquei em "Deploy" (botão azul)
- [ ] Aguardei 2-3 minutos (build rodando)
- [ ] ✅ Vi "Congratulations! Your project is live!"
- [ ] Copiei o link (ex: https://stoke-xxx.vercel.app)

---

## 📋 PARTE 10: Testar Funcionamento

- [ ] Abri o link no PC
- [ ] Criei um produto de teste
- [ ] Fiz uma venda de teste
- [ ] ✅ App funcionou no PC!

- [ ] Abri o MESMO link no celular
- [ ] Vi o produto criado no PC
- [ ] Criei um produto no celular
- [ ] Atualizei a página no PC
- [ ] ✅ Produto do celular apareceu no PC!

---

## 📋 PARTE 11: PWA (Opcional)

### No Celular:
- [ ] Menu (⋮) → "Adicionar à tela inicial"
- [ ] ✅ Ícone criado na tela inicial!

### No PC:
- [ ] Cliquei no ícone de instalação na barra de endereço
- [ ] Cliquei em "Instalar"
- [ ] ✅ App instalado no Windows!

---

## 🎉 DEPLOY COMPLETO!

- [ ] ✅ App online e funcionando
- [ ] ✅ Banco Railway conectado
- [ ] ✅ Sincronização PC + Celular testada
- [ ] ✅ PWA instalado (opcional)

---

## 📊 RESUMO FINAL

✅ URL do app: `https://_____________________________.vercel.app`

✅ Banco de dados: Railway PostgreSQL

✅ Status: **FUNCIONANDO!** 🎉

---

**Parabéns! Você conseguiu!** 🎊

Agora você tem um sistema de estoque profissional, instalável, com sincronização entre dispositivos, hospedado gratuitamente!

---

## 📞 Problemas?

Se marcou TODOS os checkboxes mas algo não funciona:
1. Copie o erro completo
2. Me envie
3. Vou te ajudar a resolver!

---

**Data do deploy:** ___/___/2025


