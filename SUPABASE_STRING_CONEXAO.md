# 🔍 Como Encontrar a String de Conexão no Supabase

## Passo a Passo Atualizado (2025)

### 1️⃣ Acesse seu Projeto no Supabase

Depois de criar o projeto, aguarde ele ficar **"Active"** (bolinha verde)

---

### 2️⃣ Encontre a String de Conexão

Há **2 formas** de encontrar:

## 📍 **FORMA 1: Via Settings (Recomendada)**

1. Na barra lateral esquerda, clique em **⚙️ Settings** (ícone de engrenagem)
2. No menu que abre, clique em **Database**
3. Role a página até encontrar a seção **"Connection string"**
4. Você verá **3 opções de tabs/abas:**
   - **URI** (NÃO use esta)
   - **PSQL**
   - **Transaction** ← **USE ESTA!**

5. **Clique na aba "Transaction"** (ou "Pooler" em algumas versões)

6. Você verá algo assim:
```
postgresql://postgres.xxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

7. **Copie essa string toda**

8. **IMPORTANTE**: Substitua `[YOUR-PASSWORD]` pela senha que você criou no Passo 1.2

---

## 📍 **FORMA 2: Via Connect (Alternativa)**

1. Na barra lateral esquerda, clique em **🔌 Database**
2. No topo, procure o botão **"Connect"** e clique
3. Uma modal/popup vai abrir
4. Escolha **"Connection pooling"** ou **"Transaction mode"**
5. Selecione **"Connection string"**
6. Copie a string mostrada

---

## ✅ **String Correta - Formato:**

```
postgresql://postgres.[PROJETO_ID]:[SUA_SENHA]@aws-0-[REGIAO].pooler.supabase.com:6543/postgres
```

### **Exemplo Real (com senha fictícia):**

```
postgresql://postgres.abcdefghij:minhaSenha123!@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

---

## ❌ **NÃO use estas (URI Mode):**

```
postgresql://postgres:[SENHA]@db.xxxxx.supabase.co:5432/postgres
```
☝️ Esta é a string "URI" - **NÃO funciona no Vercel!** (porta 5432)

---

## 🔐 **Onde está minha senha?**

A senha você criou quando criou o projeto! Se esqueceu:

1. Settings → Database
2. Role até **"Database password"**
3. Clique em **"Reset database password"**
4. Crie nova senha e anote!

---

## 🧪 **Como testar se a string está correta?**

A string correta tem estas características:

✅ Começa com `postgresql://`
✅ Tem `pooler.supabase.com` no meio
✅ Termina com porta `:6543/postgres` (não 5432)
✅ Tem `.pooler.` no domínio
✅ Região `aws-0-sa-east-1` (se escolheu São Paulo)

---

## 🎯 **Checklist Final:**

- [ ] String começa com `postgresql://`
- [ ] Contém `pooler.supabase.com`
- [ ] Porta é `:6543` (não 5432)
- [ ] Substituí `[YOUR-PASSWORD]` pela minha senha real
- [ ] Não tem espaços no início ou fim
- [ ] Copiei a string completa (toda uma linha)

---

## 📸 **Localização Visual:**

```
Supabase Dashboard
└── Settings (⚙️)
    └── Database
        └── Connection string
            └── [Transaction] ← CLIQUE AQUI
                └── Copie a string que aparece
```

---

## 🆘 **Ainda não encontrou?**

### **Tente este caminho alternativo:**

1. **Home do Supabase** → Seu projeto
2. **Sidebar** → **Database** (ícone de banco de dados)
3. No topo direito, botão **"Connect"** (verde)
4. **Pooler/Transaction Mode**
5. **Connection String**
6. Copie!

---

## 💡 **Dica Extra:**

Se a interface do Supabase mudou novamente, procure por:
- **"Connection string"**
- **"Pooler"**
- **"Transaction mode"**
- **"Connection pooling"**
- Porta **6543** (não 5432)

A string que você precisa SEMPRE terá `.pooler.` no domínio e porta `6543`!

---

## ❓ **Tem Print/Screenshot da sua tela?**

Se ainda não encontrou, me diga o que você está vendo na tela do Supabase que eu te ajudo a localizar!

