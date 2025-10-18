#!/usr/bin/env python3
"""
Script para preparar o projeto para deploy no Vercel com Supabase.
Execute este script antes de começar o deploy.
"""

import os
import shutil
import sys
from pathlib import Path

def limpar_cache():
    """Remove todos os arquivos __pycache__ e .pyc"""
    print("\n[1/5] Limpando cache do Python...")
    
    base_dir = Path(__file__).resolve().parent / "estoque_project"
    
    # Remover __pycache__
    for pycache_dir in base_dir.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            print(f"  [OK] Removido: {pycache_dir.relative_to(base_dir)}")
        except Exception as e:
            print(f"  [AVISO] Nao foi possivel remover {pycache_dir}: {e}")
    
    # Remover .pyc
    for pyc_file in base_dir.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            print(f"  [OK] Removido: {pyc_file.relative_to(base_dir)}")
        except Exception as e:
            print(f"  [AVISO] Nao foi possivel remover {pyc_file}: {e}")
    
    print("  [OK] Cache limpo!\n")

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    print("[2/5] Verificando arquivos necessarios...")
    
    arquivos_necessarios = [
        "requirements.txt",
        "vercel.json",
        "build.sh",
        "estoque_project/wsgi_vercel.py",
        "estoque_project/estoque_project/settings.py",
        "estoque_project/manage.py",
    ]
    
    todos_existem = True
    for arquivo in arquivos_necessarios:
        caminho = Path(arquivo)
        if caminho.exists():
            print(f"  [OK] {arquivo}")
        else:
            print(f"  [ERRO] {arquivo} NAO ENCONTRADO!")
            todos_existem = False
    
    if todos_existem:
        print("  [OK] Todos os arquivos necessarios existem!\n")
    else:
        print("  [ERRO] Alguns arquivos estao faltando!\n")
        sys.exit(1)

def verificar_dependencies():
    """Verifica se as dependências estão no requirements.txt"""
    print("[3/5] Verificando dependencias...")
    
    with open("requirements.txt", "r") as f:
        conteudo = f.read()
    
    deps_necessarias = [
        "psycopg2-binary",
        "dj-database-url",
        "gunicorn",
        "whitenoise",
        "Django"
    ]
    
    for dep in deps_necessarias:
        if dep in conteudo:
            print(f"  [OK] {dep}")
        else:
            print(f"  [ERRO] {dep} nao encontrado!")
    
    # Verificar se python-decouple foi removido
    if "python-decouple" in conteudo:
        print("  [AVISO] python-decouple ainda esta no requirements.txt!")
        print("          Isso pode causar problemas. Removendo...")
        conteudo = "\n".join([linha for linha in conteudo.split("\n") 
                              if "python-decouple" not in linha])
        with open("requirements.txt", "w") as f:
            f.write(conteudo)
        print("  [OK] python-decouple removido!")
    
    print("  [OK] Dependencias verificadas!\n")

def verificar_git():
    """Verifica se o repositório Git está limpo"""
    print("[4/5] Verificando repositorio Git...")
    
    if not Path(".git").exists():
        print("  [AVISO] Nao e um repositorio Git!")
        print("          Inicialize com: git init\n")
        return
    
    # Verificar se há mudanças não commitadas
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print("  [AVISO] Ha mudancas nao commitadas:")
            print(result.stdout)
            print("  Execute: git add . && git commit -m 'Preparado para deploy'\n")
        else:
            print("  [OK] Repositorio limpo!\n")
    except Exception as e:
        print(f"  [AVISO] Nao foi possivel verificar Git: {e}\n")

def mostrar_proximos_passos():
    """Mostra os próximos passos"""
    print("[5/5] Preparacao concluida!\n")
    print("=" * 70)
    print("PROXIMOS PASSOS:")
    print("=" * 70)
    print()
    print("1. Abra o arquivo: GUIA_RAILWAY_COMPLETO.md")
    print()
    print("2. Siga o guia passo a passo:")
    print("   - PARTE 1: Criar conta Railway")
    print("   - PARTE 2: Criar banco PostgreSQL")
    print("   - PARTE 3: Copiar string de conexao")
    print("   - PARTE 4: Testar localmente")
    print("   - ... ate PARTE 11")
    print()
    print("3. Comece pela criacao da conta no Railway:")
    print("   https://railway.app/")
    print()
    print("4. Quando pegar a string de conexao do Railway, rode:")
    print('   cd estoque_project')
    print('   $env:DATABASE_URL="sua-string-railway"')
    print('   python manage.py migrate')
    print()
    print("=" * 70)
    print()
    print("[OK] Tudo pronto! Boa sorte com o deploy! ")
    print()

def main():
    print("=" * 70)
    print("PREPARACAO PARA DEPLOY - RAILWAY + VERCEL")
    print("=" * 70)
    
    try:
        limpar_cache()
        verificar_arquivos()
        verificar_dependencies()
        verificar_git()
        mostrar_proximos_passos()
    except KeyboardInterrupt:
        print("\n\n[CANCELADO] Preparacao interrompida pelo usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

