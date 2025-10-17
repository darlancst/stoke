# 🔧 Como Corrigir Erro 500 no Vercel

## Passo 1: Ver os Logs (Descobrir o Problema) 🔍

1. **Acesse o Vercel Dashboard:** https://vercel.com/dashboard
2. **Clique no seu projeto** (stoke)
3. **Vá na aba "Functions"** (ou "Deployments" → último deploy → "Functions")
4. **Clique em "Logs"** ou "View Function Logs"
5. **Procure por linhas em VERMELHO** - essas têm o erro

### O que procurar nos logs:

#### ❌ **Erro comum 1: DATABASE_URL**
```
django.db.utils.OperationalError: connection to server failed
```
**Solução:** DATABASE_URL está errada

#### ❌ **Erro comum 2: SECRET_KEY**
```
KeyError: 'SECRET_KEY'
```
**Solução:** Faltou adicionar a variável

#### ❌ **Erro comum 3: ALLOWED_HOSTS**
```
DisallowedHost at /
```
**Solução:** ALLOWED_HOSTS não tem seu domínio

---

## Passo 2: Soluções Rápidas 🚀

### 🔧 **Solução A: Usar SQLite (Mais Simples)**

Se o erro for no banco de dados, **remova** a variável `DATABASE_URL`:

1. Vercel → Seu Projeto → **Settings**
2. **Environment Variables**
3. **Delete** a variável `DATABASE_URL` (se existir)
4. Vá em **Deployments** → ⋮ (três pontinhos) → **Redeploy**

Isso fará o sistema usar SQLite (temporário, mas funciona!).

---

### 🔧 **Solução B: Adicionar TODAS as Variáveis Necessárias**

Certifique-se de ter **TODAS** estas variáveis:

```
Key: SECRET_KEY
Value: 7^9hoti#xz57__5$tjcjh89mz9i$!v3_40o8b7ppyzdhzs5)s0

Key: DEBUG
Value: False

Key: ALLOWED_HOSTS
Value: .vercel.app

Key: PYTHONUNBUFFERED
Value: 1

Key: DJANGO_SETTINGS_MODULE
Value: estoque_project.settings
```

**Não precisa de DATABASE_URL** se quiser usar SQLite!

---

### 🔧 **Solução C: Corrigir ALLOWED_HOSTS**

O ALLOWED_HOSTS precisa ter seu domínio Vercel:

1. Copie a URL do erro (ex: `stoke-abc123.vercel.app`)
2. Vá em **Settings → Environment Variables**
3. Edite `ALLOWED_HOSTS`
4. **Novo valor:**
```
.vercel.app,stoke-abc123.vercel.app
```
(substitua `stoke-abc123` pelo seu domínio real)

5. **Redeploy**

---

## Passo 3: Forçar Redeploy 🔄

Depois de qualquer mudança nas variáveis:

1. Vá em **Deployments**
2. Clique no **último deploy**
3. Clique nos **⋮** (três pontinhos)
4. **Redeploy**
5. Aguarde 2-3 minutos

---

## 🎯 **Configuração Mínima Funcional**

Use APENAS estas 4 variáveis para funcionar:

```
1. SECRET_KEY = 7^9hoti#xz57__5$tjcjh89mz9i$!v3_40o8b7ppyzdhzs5)s0
2. DEBUG = False
3. ALLOWED_HOSTS = .vercel.app
4. PYTHONUNBUFFERED = 1
```

**NÃO PRECISA** de mais nada para teste inicial!

---

## 📊 **Checklist de Verificação**

Execute estes checks:

### ✅ **No Vercel → Settings → Environment Variables:**

- [ ] `SECRET_KEY` existe e tem valor longo
- [ ] `DEBUG` = False (exatamente assim, com F maiúsculo)
- [ ] `ALLOWED_HOSTS` tem `.vercel.app`
- [ ] `PYTHONUNBUFFERED` = 1

### ✅ **No Vercel → Deployments:**

- [ ] Último deploy tem status "Ready" (não "Error")
- [ ] Build logs não têm erros vermelhos
- [ ] Function logs carregam

---

## 🔥 **Solução GARANTIDA (Reset Completo)**

Se nada funcionou, faça reset:

### 1. **Delete TODAS as variáveis**
Settings → Environment Variables → Delete All

### 2. **Adicione APENAS estas 4:**
```
SECRET_KEY: 7^9hoti#xz57__5$tjcjh89mz9i$!v3_40o8b7ppyzdhzs5)s0
DEBUG: False
ALLOWED_HOSTS: .vercel.app
PYTHONUNBUFFERED: 1
```

### 3. **Redeploy**
Deployments → último → ⋮ → Redeploy

### 4. **Aguarde 3 minutos**

### 5. **Teste novamente**

---

## 🆘 **Me Envie os Logs**

Se ainda não funcionar, faça isso:

1. **Vercel** → Seu Projeto → **Functions** → **Logs**
2. **Copie as últimas 20-30 linhas** (especialmente as vermelhas)
3. **Cole aqui no chat**
4. Eu te ajudo a identificar o problema exato!

---

## 💡 **Dica: Testando Localmente**

Antes de fazer deploy, sempre teste local:

```bash
cd estoque_project
python manage.py runserver
```

Se funcionar local mas não na Vercel = problema nas variáveis de ambiente.

---

## 🎓 **Erros Comuns e Soluções**

| Erro | Causa | Solução |
|------|-------|---------|
| 500 FUNCTION_INVOCATION_FAILED | Variáveis erradas | Reset variáveis |
| DisallowedHost | ALLOWED_HOSTS | Adicionar domínio |
| Database error | DATABASE_URL | Remover variável |
| KeyError SECRET_KEY | Falta variável | Adicionar |
| Build failed | Código com erro | Verificar último commit |

---

## ✅ **Como Saber se Funcionou?**

Quando corrigir, você verá:

✅ Página de login/dashboard do Stoke
✅ Nenhum erro 500
✅ CSS carregando
✅ Ícone do PWA aparece

---

**Me envie os logs que eu te ajudo a resolver rapidinho!** 🚀

