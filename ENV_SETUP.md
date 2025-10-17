# Configuração de Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Django Settings
SECRET_KEY=sua-chave-secreta-aqui-use-python-manage-py-shell-e-from-django-core-management-utils-import-get-random-secret-key-print-get-random-secret-key
DEBUG=False
ALLOWED_HOSTS=.vercel.app,seu-dominio.com

# Database - Supabase PostgreSQL
# Obtenha no Supabase: Settings > Database > Connection String (Transaction Mode)
DATABASE_URL=postgresql://usuario:senha@host:porta/banco

# Security (Produção)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Para Desenvolvimento Local

```env
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

## Gerando SECRET_KEY

Execute no terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

