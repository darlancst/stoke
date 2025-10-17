#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar variáveis de ambiente necessárias para deploy
"""

print("=" * 70)
print("GERADOR DE VARIAVEIS PARA DEPLOY - STOKE")
print("=" * 70)
print()

# Gerar SECRET_KEY
print("Gerando SECRET_KEY...")
try:
    from django.core.management.utils import get_random_secret_key
    secret_key = get_random_secret_key()
    print("Gerada com sucesso!")
    print()
except ImportError:
    secret_key = "ERRO: Django nao instalado"
    print("Erro ao gerar. Use: pip install django")
    print()

# Exibir todas as variáveis formatadas
print("=" * 70)
print("COPIE E COLE NO VERCEL (Environment Variables)")
print("=" * 70)
print()

variaveis = [
    ("SECRET_KEY", secret_key),
    ("DEBUG", "False"),
    ("ALLOWED_HOSTS", ".vercel.app"),
    ("DATABASE_URL", "postgresql://postgres.xxxxx:SUA_SENHA@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"),
    ("SECURE_SSL_REDIRECT", "True"),
    ("SESSION_COOKIE_SECURE", "True"),
    ("CSRF_COOKIE_SECURE", "True"),
]

for i, (key, value) in enumerate(variaveis, 1):
    print(f"Variável {i}:")
    print(f"  Key:   {key}")
    print(f"  Value: {value}")
    if key == "DATABASE_URL":
        print("  ATENCAO: Substitua pela string REAL do Supabase!")
    print()

print("=" * 70)
print("PROXIMOS PASSOS:")
print("=" * 70)
print()
print("1. Abra o arquivo 'GUIA_DEPLOY_PASSO_A_PASSO.md'")
print("2. Siga o passo a passo")
print("3. Use as variaveis geradas acima no Vercel")
print("4. Aguarde o deploy (2-4 minutos)")
print("5. Acesse seu app online!")
print()
print("=" * 70)

