# 🗄️ Como Rodar Migrations no Supabase

## Problema

O erro `relation "inventario_lote" does not exist` significa que o banco está vazio (sem tabelas).

Precisamos rodar `python manage.py migrate` no banco do Supabase.

---

## ✅ **SOLUÇÃO RÁPIDA (Windows PowerShell)**

### Passo 1: Abra o PowerShell no projeto

```powershell
cd C:\Users\darkl\Desktop\Stoke
```

### Passo 2: Defina a DATABASE_URL temporariamente

**Substitua pela sua string completa do Supabase:**

```powershell
$env:DATABASE_URL="postgresql://postgres.felqdmzuenchvdpibgyc:SUA_SENHA@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"
```

⚠️ **IMPORTANTE**: 
- Substitua `SUA_SENHA` pela senha real
- Use aspas duplas `"..."`
- Cole a linha completa de uma vez

### Passo 3: Navegue para a pasta do Django

```powershell
cd estoque_project
```

### Passo 4: Rode as migrations

```powershell
python manage.py migrate
```

### Passo 5: Aguarde

Você verá algo como:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying inventario.0001_initial... OK
  ...
```

---

## ✅ **Depois que rodar com sucesso:**

1. **Vercel** → Seu Projeto → **Deployments**
2. ⋮ (três pontinhos) → **Redeploy**
3. Aguarde 2 minutos
4. **Acesse a URL** → ✅ **Vai funcionar!**

---

## 🐛 **Se der erro:**

### Erro: "psycopg2 not found"

```powershell
pip install psycopg2-binary
```

Depois rode o Passo 4 novamente.

### Erro: "No module named 'dj_database_url'"

```powershell
pip install dj-database-url
```

Depois rode o Passo 4 novamente.

### Erro: "connection refused"

Verifique se a DATABASE_URL está correta:
- ✅ Porta `6543` (não 5432)
- ✅ Tem `pooler` no domínio
- ✅ Senha está correta

---

## 📝 **Comandos Completos (Copie e Cole)**

**Substitua `SUA_SENHA` antes de executar!**

```powershell
# 1. Ir para o projeto
cd C:\Users\darkl\Desktop\Stoke

# 2. Setar DATABASE_URL (SUBSTITUA SUA_SENHA!)
$env:DATABASE_URL="postgresql://postgres.felqdmzuenchvdpibgyc:SUA_SENHA@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"

# 3. Entrar na pasta Django
cd estoque_project

# 4. Rodar migrations
python manage.py migrate

# 5. (Opcional) Criar superusuário
python manage.py createsuperuser
```

---

## 🎯 **Resultado Esperado:**

Quando funcionar, você verá:

```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  ...
  Applying inventario.0013_itemvendalote... OK
  Applying sessions.0001_initial... OK
```

✅ **Pronto! Tabelas criadas no Supabase!**

---

## 💡 **Próxima vez:**

Sempre que fizer mudanças nos models, rode:

```powershell
$env:DATABASE_URL="sua_string_aqui"
cd estoque_project
python manage.py makemigrations
python manage.py migrate
```

E faça commit + push para atualizar no Vercel!











