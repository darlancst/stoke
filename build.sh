#!/bin/bash

# Instalar dependências
pip install -r requirements.txt

# Navegar para o diretório do projeto Django
cd estoque_project

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Executar migrações
python manage.py migrate --no-input

