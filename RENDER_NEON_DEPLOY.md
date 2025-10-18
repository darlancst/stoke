# 🚀 Deploy Gratuito: Render.com + Neon.tech

Este guia mostra como fazer deploy do **Stoke** de forma **100% gratuita** usando Render.com (hospedagem) + Neon.tech (PostgreSQL).

---

## 📋 Pré-requisitos

- Conta no GitHub (para conectar o repositório)
- Conta no Neon.tech (PostgreSQL gratuito)
- Conta no Render.com (hospedagem gratuita)

**💰 Custo Total: R$ 0,00/mês (para sempre)**

---

## Parte 1️⃣: Configurar PostgreSQL no Neon.tech

### Passo 1: Criar conta no Neon

1. Acesse: https://neon.tech
2. Clique em **"Sign Up"**
3. Faça login com GitHub (recomendado) ou email
4. ✅ **Não precisa de cartão de crédito**

### Passo 2: Criar projeto

1. No dashboard do Neon, clique em **"Create Project"**
2. Preencha:
   - **Project name:** `stoke`
   - **Database name:** `stoke`
   - **Region:** Escolha a mais próxima (ex: `aws-us-east-1`)
3. Clique em **"Create Project"**

### Passo 3: Copiar Connection String

1. Após criar o projeto, você verá a página de **"Connection Details"**
2. Procure por **"Connection string"** ou **"Postgres connection string"**
3. Copie a string que começa com `postgres://` ou `postgresql://`

**Exemplo:**
```
postgresql://user:password@ep-example-123456.us-east-1.aws.neon.tech/stoke?sslmode=require
```

4. ⚠️ **GUARDE ESSA STRING** - você vai precisar dela no Render!

---

## Parte 2️⃣: Deploy no Render.com

### Passo 1: Criar conta no Render

1. Acesse: https://render.com
2. Clique em **"Get Started for Free"**
3. Faça login com GitHub (recomendado)
4. Autorize o Render a acessar seus repositórios

### Passo 2: Conectar repositório

1. No dashboard do Render, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório do GitHub:
   - Clique em **"Connect account"** se necessário
   - Procure por `Stoke` (nome do seu repositório)
   - Clique em **"Connect"**

### Passo 3: Configurar o serviço

Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Name** | `stoke` (ou qualquer nome único) |
| **Region** | `Oregon (US West)` ou mais próximo |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `cd estoque_project && gunicorn estoque_project.wsgi:application --bind 0.0.0.0:$PORT` |
| **Instance Type** | **Free** ✅ |

### Passo 4: Adicionar variáveis de ambiente

Role a página até **"Environment Variables"** e adicione:

#### 1. DATABASE_URL
- **Key:** `DATABASE_URL`
- **Value:** Cole a connection string do Neon que você copiou antes
- Exemplo: `postgresql://user:password@ep-example-123456.us-east-1.aws.neon.tech/stoke?sslmode=require`

#### 2. ALLOWED_HOSTS
- **Key:** `ALLOWED_HOSTS`
- **Value:** `127.0.0.1,localhost,.onrender.com`

#### 3. SECRET_KEY
- **Key:** `SECRET_KEY`
- **Value:** Clique em **"Generate"** (Render gera automaticamente)

#### 4. DEBUG
- **Key:** `DEBUG`
- **Value:** `False`

#### 5. PYTHON_VERSION
- **Key:** `PYTHON_VERSION`
- **Value:** `3.11.7`

### Passo 5: Fazer Deploy

1. Clique em **"Create Web Service"** no final da página
2. Aguarde o build (5-10 minutos na primeira vez)
3. Acompanhe os logs em tempo real

**Você verá algo assim nos logs:**
```
==> Installing Python dependencies...
==> Navigating to Django project...
==> Collecting static files...
==> Running database migrations...
==> Build completed successfully!
```

### Passo 6: Acessar o app

1. Quando o deploy terminar, você verá um link no topo:
   - Exemplo: `https://stoke.onrender.com`
2. Clique no link ou copie e abra no navegador
3. 🎉 **Seu app está no ar!**

---

## Parte 3️⃣: Instalar PWA no Celular

Agora que seu app está online, você pode instalá-lo como um aplicativo:

👉 **Veja o guia completo:** [INSTALAR_PWA.md](INSTALAR_PWA.md)

---

## 🔧 Configurações Pós-Deploy

### Criar superusuário (admin)

Para acessar o painel administrativo do Django:

1. No dashboard do Render, vá em seu serviço **stoke**
2. Clique na aba **"Shell"** (no menu lateral)
3. Digite os comandos:

```bash
cd estoque_project
python manage.py createsuperuser
```

4. Preencha:
   - **Username:** (seu nome de usuário)
   - **Email:** (seu email)
   - **Password:** (senha segura)

5. Acesse: `https://stoke.onrender.com/admin`

---

## 📊 Monitoramento e Logs

### Ver logs em tempo real

1. No dashboard do Render, clique em **"Logs"** (menu lateral)
2. Veja requisições, erros e avisos em tempo real
3. Use para debugar problemas

### Métricas gratuitas

- **CPU:** Uso do processador
- **Memory:** Consumo de memória
- **Requests:** Número de requisições
- **Response Time:** Tempo de resposta

Acesse em: **"Metrics"** no menu lateral

---

## 🔄 Atualizações Automáticas

### Deploy automático

O Render faz deploy automático sempre que você fizer **push** para o GitHub:

```bash
git add .
git commit -m "Minha atualização"
git push origin main
```

O Render detecta automaticamente e faz o deploy!

---

## ⚠️ Limitações do Tier Gratuito

### Render.com (Free)

| Recurso | Limite |
|---------|--------|
| **Tempo de CPU** | 750 horas/mês (suficiente para 1 app 24/7) |
| **Cold Start** | Após 15min inativo, app "dorme" (~30s para acordar) |
| **Bandwidth** | 100GB/mês |
| **Builds** | Ilimitados |
| **Domínio** | `.onrender.com` (gratuito) |

### Neon.tech (Free)

| Recurso | Limite |
|---------|--------|
| **Storage** | 0.5GB por projeto |
| **Projetos** | 10 projetos gratuitos |
| **Compute** | Suspende após 5 dias inativo (acorda em <1s) |
| **Backup** | 7 dias de retenção |

**💡 Dica:** Para evitar cold starts no Render, use um serviço de "ping" como:
- UptimeRobot (pinga seu app a cada 5 minutos)
- Cron-job.org (pinga periodicamente)

---

## 🐛 Troubleshooting

### ❌ Erro: "Application failed to respond"

**Causa:** O app não conseguiu iniciar corretamente.

**Solução:**
1. Verifique os logs no Render
2. Confirme que `DATABASE_URL` está correta
3. Verifique se as migrations rodaram: `python manage.py migrate`

### ❌ Erro: "DisallowedHost"

**Causa:** O domínio não está em `ALLOWED_HOSTS`.

**Solução:**
1. Vá em **"Environment"** no Render
2. Edite `ALLOWED_HOSTS` para incluir `.onrender.com`
3. Salve e aguarde o redeploy automático

### ❌ Erro: "Static files not found"

**Causa:** Arquivos estáticos não foram coletados.

**Solução:**
1. Verifique se `build.sh` tem permissão de execução:
   ```bash
   chmod +x build.sh
   git add build.sh
   git commit -m "Fix build.sh permissions"
   git push
   ```

### ❌ App muito lento na primeira requisição

**Causa:** Cold start (app "dormiu" após 15min de inatividade).

**Solução:**
- É normal no tier gratuito
- Use UptimeRobot para pingar a cada 5-10 minutos
- Ou considere upgrade para plano pago ($7/mês) para evitar sleep

### ❌ Banco de dados desconectado

**Causa:** Neon suspendeu o projeto após 5 dias sem uso.

**Solução:**
- Acesse o dashboard do Neon
- O projeto acorda automaticamente ao fazer login
- Ou faça uma requisição ao app para acordar

---

## 🔐 Segurança

### Checklist de Segurança

- ✅ `DEBUG = False` em produção
- ✅ `SECRET_KEY` gerado aleatoriamente pelo Render
- ✅ `ALLOWED_HOSTS` configurado corretamente
- ✅ SSL/HTTPS automático (Render fornece)
- ✅ PostgreSQL com SSL obrigatório (Neon)
- ✅ Variáveis de ambiente (não hardcoded)

### Recomendações

1. **Nunca commit** arquivos `.env` com credenciais
2. **Mude o SECRET_KEY** se for exposto
3. **Use senhas fortes** para superusuário
4. **Monitore os logs** regularmente

---

## 🎯 Próximos Passos

1. ✅ Deploy concluído
2. 📱 [Instalar PWA no celular](INSTALAR_PWA.md)
3. 👥 Criar usuários no Django admin
4. 📊 Começar a usar o sistema
5. 🔄 Testar sincronização entre dispositivos

---

## 💡 Dicas Extras

### Domínio Personalizado

Quer usar seu próprio domínio? (ex: `estoque.seusite.com`)

1. No Render, vá em **"Settings"** → **"Custom Domain"**
2. Adicione seu domínio
3. Configure os DNS records no seu provedor de domínio
4. Aguarde propagação (até 24h)

### Backup Manual

Para fazer backup do PostgreSQL:

1. No Neon, vá em seu projeto
2. Clique em **"Backups"**
3. Clique em **"Create Backup"**
4. Download do backup quando necessário

---

## 📞 Suporte

**Render Support:** https://render.com/docs  
**Neon Support:** https://neon.tech/docs  
**Django Docs:** https://docs.djangoproject.com

---

**🎉 Parabéns! Seu sistema está 100% gratuito e funcional na nuvem!**

