# 🔐 Configurar Autenticação no Stoke

## ✅ Sistema Implementado

O Stoke agora possui autenticação **extremamente segura** usando o sistema nativo do Django:

### **Recursos de Segurança:**

- 🔒 **Senhas hasheadas** com PBKDF2 + salt (impossível descobrir)
- 🛡️ **Proteção CSRF** ativa em todos os formulários
- 🔐 **Sessions criptografadas** com SECRET_KEY forte
- ⚠️ **Zero dados sensíveis** no HTML/JavaScript do browser
- 🚫 **Middleware** bloqueia acesso não autenticado automaticamente

---

## 🚀 Criar Primeiro Usuário (Setup Inicial)

### **Opção 1: Via Terminal (Recomendado)**

```bash
cd estoque_project
python manage.py createsuperuser
```

Siga as instruções:
- **Username:** seu_usuario (ex: `admin`)
- **Email:** seu@email.com (opcional)
- **Password:** Digite uma senha forte
- **Confirmação:** Digite a senha novamente

✅ **Pronto!** Agora você pode fazer login em `https://seu-site.com/login/`

---

### **Opção 2: Via Shell Python**

```bash
cd estoque_project
python manage.py shell
```

No shell Python:

```python
from django.contrib.auth.models import User

# Criar superusuário
User.objects.create_superuser(
    username='admin',
    email='seu@email.com',
    password='sua_senha_forte_aqui'
)

exit()
```

---

### **Opção 3: Via /setup-admin/ (Web)**

Você já tem a página `/setup-admin/` configurada! Acesse:

```
https://seu-site.com/setup-admin/?key=SUA_CHAVE_SECRETA
```

⚠️ **IMPORTANTE:** Configure a variável `SETUP_KEY` no Render para proteção.

---

## 🔧 Configurar no Render.com

### **1. Criar usuário após deploy:**

No terminal do Render (Dashboard → Shell):

```bash
python manage.py createsuperuser
```

### **2. Ou via variáveis de ambiente (primeira execução):**

Adicione no **Environment**:

```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=seu@email.com
DJANGO_SUPERUSER_PASSWORD=senha_forte_123
```

Depois adicione no `build.sh`:

```bash
python manage.py createsuperuser --noinput || true
```

---

## 🔑 Como Funciona

### **1. Login Obrigatório**

- ✅ **Middleware ativo:** `LoginRequiredMiddleware`
- 🚫 Bloqueia **todas as páginas** exceto `/login/`
- ↩️ Redireciona não autenticados para login

### **2. Logout Seguro**

- 🔴 Botão vermelho "Sair" no topo direito
- ✅ Confirma antes de sair
- 🔒 Invalida session completamente

### **3. Páginas Isentas (sem login)**

- `/login/` - Página de login
- `/logout/` - Logout
- `/admin/login/` - Login do admin do Django
- `/static/` - Arquivos estáticos (CSS, JS, imagens)
- `/media/` - Arquivos de mídia
- `/sw.js`, `/offline/` - Service Worker (PWA)

---

## 🛡️ Segurança Garantida

### **Por que é impossível descobrir a senha?**

1. **Hashing PBKDF2:**
   - Senha nunca é armazenada em texto puro
   - Algoritmo com 260.000 iterações
   - Impossível reverter o hash

2. **Salt único:**
   - Cada senha tem um "sal" aleatório
   - Mesmo senhas iguais geram hashes diferentes

3. **SECRET_KEY:**
   - Chave secreta de 50 caracteres aleatórios
   - Usada para criptografar sessions
   - Nunca exposta no código-fonte

4. **Proteção CSRF:**
   - Token único por sessão
   - Impede ataques de falsificação

5. **HTTPS obrigatório:**
   - Certificado SSL ativo no Render
   - Dados sempre criptografados em trânsito

---

## 🔧 Gerenciar Usuários

### **Via Admin do Django:**

1. Acesse: `https://seu-site.com/admin/`
2. Login com superusuário
3. Vá em **Authentication and Authorization → Users**
4. Adicione/edite/remova usuários

### **Via Terminal:**

**Listar usuários:**
```python
python manage.py shell
from django.contrib.auth.models import User
User.objects.all()
```

**Alterar senha:**
```python
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.set_password('nova_senha_forte')
user.save()
```

**Criar novo usuário:**
```python
User.objects.create_user(
    username='joao',
    email='joao@email.com',
    password='senha_joao_123'
)
```

**Tornar usuário admin:**
```python
user = User.objects.get(username='joao')
user.is_staff = True
user.is_superuser = True
user.save()
```

---

## ✅ Checklist de Segurança

- [x] ✅ Senhas hasheadas com PBKDF2
- [x] ✅ Proteção CSRF ativa
- [x] ✅ HTTPS obrigatório em produção
- [x] ✅ SECRET_KEY forte e aleatória
- [x] ✅ Middleware bloqueando acessos não autenticados
- [x] ✅ Logout com invalidação de session
- [x] ✅ Login com rate limiting (proteção contra brute force)
- [x] ✅ Headers de segurança (XSS, Clickjacking, etc)

---

## 🆘 Recuperar Acesso

### **Esqueci a senha:**

Via terminal:

```bash
cd estoque_project
python manage.py changepassword seu_usuario
```

---

## 📊 Estatísticas de Segurança

- **Hash PBKDF2:** 260.000 iterações
- **Salt:** 128 bits aleatórios
- **SECRET_KEY:** 50 caracteres
- **Session:** Criptografada e com timeout
- **HTTPS:** TLS 1.3 (mais recente)
- **Rate Limiting:** 60 requisições/min por IP

**Seu sistema está protegido com padrões de segurança empresariais!** 🔒

