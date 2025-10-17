# 🚀 Guia de Deploy - Passo a Passo

## ✅ Pré-requisitos
- [x] Código no GitHub (https://github.com/darlancst/stoke) ✓
- [x] PWA completo com ícones ✓
- [ ] Conta no Supabase
- [ ] Conta no Vercel

---

## PARTE 1: SUPABASE (Banco de Dados) 🗄️

### Passo 1.1: Criar Conta no Supabase

1. Acesse: **https://supabase.com**
2. Clique em **"Start your project"** ou **"Sign In"**
3. Escolha fazer login com **GitHub** (mais fácil)
4. Autorize o Supabase

### Passo 1.2: Criar Novo Projeto

1. No dashboard do Supabase, clique em **"New Project"**
2. Preencha os dados:
   ```
   Name: stoke-estoque
   Database Password: [CRIE UMA SENHA FORTE E ANOTE!]
   Region: South America (São Paulo) - sa-east-1
   Pricing Plan: Free
   ```
3. Clique em **"Create new project"**
4. ⏳ Aguarde 2-3 minutos (está criando o banco)

### Passo 1.3: Obter String de Conexão

1. Quando o projeto estiver pronto (Status: Active)
2. Vá em **Settings** (⚙️ na barra lateral)
3. Clique em **Database**
4. Role até **"Connection string"**
5. Selecione **"Transaction"** (não URI!)
6. Copie a string que aparece:
   ```
   postgresql://postgres.xxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
   ```
7. **IMPORTANTE**: Substitua `[YOUR-PASSWORD]` pela senha que você criou no passo 1.2

**Exemplo da string final:**
```
postgresql://postgres.abcdefghij:minhaSenha123@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

8. **ANOTE ESSA STRING!** Você vai precisar dela no Vercel.

---

## PARTE 2: VERCEL (Hospedagem) 🌐

### Passo 2.1: Criar Conta no Vercel

1. Acesse: **https://vercel.com**
2. Clique em **"Sign Up"**
3. Escolha **"Continue with GitHub"**
4. Autorize o Vercel

### Passo 2.2: Importar Projeto do GitHub

1. No dashboard do Vercel, clique em **"Add New..."**
2. Selecione **"Project"**
3. Na lista de repositórios, procure por **"stoke"**
4. Clique em **"Import"**

### Passo 2.3: Configurar Variáveis de Ambiente

**ATENÇÃO: Esta é a parte mais importante!**

Na tela de configuração do projeto, role até **"Environment Variables"**

Adicione TODAS estas variáveis (uma por vez):

#### Variável 1: SECRET_KEY
```
Key: SECRET_KEY
Value: [GERE UMA CHAVE ABAIXO]
```

**Para gerar a chave, execute no seu terminal:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copie o resultado e cole em "Value"

#### Variável 2: DEBUG
```
Key: DEBUG
Value: False
```

#### Variável 3: ALLOWED_HOSTS
```
Key: ALLOWED_HOSTS
Value: .vercel.app
```

#### Variável 4: DATABASE_URL
```
Key: DATABASE_URL
Value: [COLE A STRING DO SUPABASE AQUI]
```
(A string que você anotou no Passo 1.3)

#### Variável 5: SECURE_SSL_REDIRECT
```
Key: SECURE_SSL_REDIRECT
Value: True
```

#### Variável 6: SESSION_COOKIE_SECURE
```
Key: SESSION_COOKIE_SECURE
Value: True
```

#### Variável 7: CSRF_COOKIE_SECURE
```
Key: CSRF_COOKIE_SECURE
Value: True
```

### Passo 2.4: Deploy!

1. Depois de adicionar TODAS as variáveis, clique em **"Deploy"**
2. ⏳ Aguarde 2-4 minutos
3. 🎉 Seu app estará online!

---

## PARTE 3: Primeiro Acesso e Configuração 🎯

### Passo 3.1: Acessar o App

1. Quando o deploy terminar, você verá uma mensagem de sucesso
2. Clique em **"Visit"** ou copie a URL (será algo como: `https://stoke-xyz123.vercel.app`)

### Passo 3.2: Verificar se Funcionou

1. Acesse a URL do seu app
2. Se aparecer a tela inicial do Stoke = ✅ SUCESSO!
3. Se der erro 500, veja a seção de "Troubleshooting" abaixo

---

## 🐛 TROUBLESHOOTING (Resolvendo Problemas)

### Erro: "Application error"

**Causa**: Provavelmente a DATABASE_URL está errada

**Solução:**
1. No Vercel, vá em seu projeto
2. Clique em **Settings** > **Environment Variables**
3. Verifique a DATABASE_URL:
   - Tem o formato: `postgresql://postgres...`?
   - Você substituiu `[YOUR-PASSWORD]` pela senha real?
   - Não tem espaços no início/fim?

### Erro: "Bad Gateway"

**Causa**: O servidor está subindo, aguarde 1-2 minutos

### Erro: "CSRF verification failed"

**Causa**: ALLOWED_HOSTS não está configurado

**Solução:**
1. Vá em Settings > Environment Variables
2. Edite ALLOWED_HOSTS
3. Adicione seu domínio Vercel: `.vercel.app,stoke-xyz123.vercel.app`
4. Clique em "Save" e faça novo deploy

---

## 📱 BONUS: Instalar o App (PWA)

### No Celular (Android/iOS):
1. Abra seu app no Chrome/Safari
2. Menu (⋮) > **"Adicionar à tela inicial"**
3. Confirme
4. 🎉 Ícone aparecerá na tela inicial!

### No Desktop (Chrome/Edge):
1. Abra seu app
2. Procure o ícone ⊕ na barra de endereço
3. Clique em **"Instalar"**
4. 🎉 App abre em janela própria!

---

## 💡 Dicas Importantes

### Domínio Personalizado (Opcional)
1. No Vercel, vá em Settings > Domains
2. Adicione seu domínio (ex: `estoque.meusite.com`)
3. Configure DNS conforme instruções

### Monitoramento
- **Logs**: Vercel Dashboard > Seu Projeto > Logs
- **Banco**: Supabase Dashboard > Table Editor

### Atualizações
- Cada `git push` no branch `main` faz deploy automático! 🚀

---

## 📊 Custos Mensais

### Plano Gratuito (Recomendado para começar):
- **Supabase**: R$ 0,00 (500 MB banco + 1 GB storage)
- **Vercel**: R$ 0,00 (100 GB bandwidth)
- **TOTAL**: R$ 0,00/mês ✅

### Quando precisar pagar?
- Supabase: Se passar de 500 MB no banco (improvável)
- Vercel: Se passar de 100 GB de tráfego (muito improvável)

Para pequenas empresas, o plano gratuito é suficiente! 🎉

---

## ✅ Checklist Final

- [ ] Projeto criado no Supabase
- [ ] String de conexão anotada
- [ ] Projeto importado no Vercel
- [ ] Todas as 7 variáveis configuradas
- [ ] Deploy concluído com sucesso
- [ ] App acessível pela URL
- [ ] PWA instalável no celular

---

## 🆘 Precisa de Ajuda?

Se algo der errado:
1. Verifique os logs no Vercel (Functions > Logs)
2. Verifique se todas as variáveis estão corretas
3. Refaça o deploy (Deployments > ⋮ > Redeploy)

**Lembre-se**: O primeiro deploy pode demorar até 5 minutos! ⏳

