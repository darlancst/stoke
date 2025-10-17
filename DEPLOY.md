# Guia de Deploy - Vercel + Supabase

## 📋 Pré-requisitos

1. Conta no [Vercel](https://vercel.com)
2. Conta no [Supabase](https://supabase.com)
3. Git instalado

## 🗄️ Configurar Banco de Dados no Supabase

### 1. Criar Projeto no Supabase

1. Acesse [Supabase](https://supabase.com) e faça login
2. Clique em "New Project"
3. Preencha:
   - **Name**: `estoque-system` (ou nome de sua preferência)
   - **Database Password**: Anote essa senha!
   - **Region**: Escolha o mais próximo (Brazil East)
   - **Pricing Plan**: Free (suficiente para estudos)

### 2. Obter String de Conexão

1. No projeto criado, vá em **Settings** > **Database**
2. Em "Connection string", selecione **Transaction Mode**
3. Copie a string que aparece (formato: `postgresql://...`)
4. Substitua `[YOUR-PASSWORD]` pela senha que você criou

**Exemplo da string:**
```
postgresql://postgres.xxxxx:SUA_SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

## 🚀 Deploy no Vercel

### 1. Preparar Repositório

```bash
# Já fizemos o commit, agora envie para o GitHub
git push origin main
```

### 2. Importar no Vercel

1. Acesse [Vercel](https://vercel.com) e faça login
2. Clique em "Add New..." > "Project"
3. Selecione seu repositório do GitHub
4. Configure as variáveis de ambiente

### 3. Configurar Variáveis de Ambiente no Vercel

Na tela de configuração do projeto, adicione estas variáveis:

| Key | Value | Exemplo |
|-----|-------|---------|
| `SECRET_KEY` | Use o gerador abaixo | `django-insecure-abc123...` |
| `DEBUG` | `False` | `False` |
| `ALLOWED_HOSTS` | `.vercel.app` | `.vercel.app` |
| `DATABASE_URL` | String do Supabase | `postgresql://postgres...` |
| `SECURE_SSL_REDIRECT` | `True` | `True` |
| `SESSION_COOKIE_SECURE` | `True` | `True` |
| `CSRF_COOKIE_SECURE` | `True` | `True` |

**Para gerar SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Deploy

1. Clique em "Deploy"
2. Aguarde o build (pode levar 2-3 minutos)
3. Pronto! Seu app estará online em `https://seu-projeto.vercel.app`

## 📝 Primeiro Acesso

### Criar Superusuário

Após o primeiro deploy bem-sucedido, você precisará criar um admin:

1. No Vercel, vá em seu projeto
2. Clique na aba "Settings" > "Functions"
3. Use o Vercel CLI para executar comando:

```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer login
vercel login

# Navegar até o projeto
cd seu-projeto

# Executar comando remoto
vercel exec -- python estoque_project/manage.py createsuperuser
```

Ou use uma função serverless para criar o admin (mais simples):

1. Acesse: `https://seu-projeto.vercel.app/admin`
2. Use o Django admin para criar o primeiro usuário

## 💰 Custos do Supabase

### Plano Gratuito (Free Tier)
- ✅ 500 MB de armazenamento de banco de dados
- ✅ 1 GB de armazenamento de arquivos
- ✅ 2 GB de transferência de dados/mês
- ✅ Múltiplos projetos permitidos
- ✅ Ideal para estudos e projetos pessoais

**Resposta à sua pergunta:** Sim, pode ter vários projetos no plano gratuito sem problemas! Cada projeto tem seus próprios limites.

### Quando precisará pagar?
- Se ultrapassar 500 MB no banco
- Se precisar de mais performance
- Se tiver muito tráfego (improvável em uso pessoal)

## 🔧 Desenvolvimento Local

Para rodar localmente com Supabase:

1. Crie arquivo `.env` na raiz:
```env
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://sua-string-do-supabase
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

2. Execute:
```bash
cd estoque_project
python manage.py migrate
python manage.py runserver
```

## 📱 Recursos do Deploy

- ✅ **Auto SSL/HTTPS**: Vercel fornece automaticamente
- ✅ **CDN Global**: Seus arquivos estáticos são servidos via CDN
- ✅ **Auto Deploy**: Cada push em `main` faz deploy automático
- ✅ **Preview Deploys**: Cada PR gera uma URL de preview
- ✅ **Logs em tempo real**: Veja logs no dashboard do Vercel
- ✅ **Backup automático**: Supabase faz backup diário

## 🎨 Upload de Imagens

**Atenção**: O Vercel tem sistema de arquivos efêmero (não persiste uploads).

Para upload de imagens de produtos em produção, você tem duas opções:

### Opção 1: Supabase Storage (Recomendado)
- Configurar Django Storages com Supabase
- Armazenamento persistente
- Incluído no plano gratuito

### Opção 2: Cloudinary (Mais simples)
- Plano gratuito: 25 GB armazenamento
- Fácil integração com Django
- Otimização automática de imagens

Por enquanto, o sistema funcionará 100%, mas sem persistência de imagens entre deploys.

## 🐛 Troubleshooting

### Erro de ALLOWED_HOSTS
Adicione seu domínio do Vercel em `ALLOWED_HOSTS` nas variáveis de ambiente.

### Erro de Database
Verifique se a `DATABASE_URL` está correta e se o Supabase está ativo.

### Erro 500
Verifique os logs no Vercel Dashboard > Functions > Logs

### Static files não carregam
Execute: `python manage.py collectstatic` localmente e faça commit do `staticfiles/`

## 📞 Suporte

- Documentação Vercel: https://vercel.com/docs
- Documentação Supabase: https://supabase.com/docs
- Django Deploy: https://docs.djangoproject.com/en/5.2/howto/deployment/

