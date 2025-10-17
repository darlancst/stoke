"""
WSGI config para Vercel deployment.
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'estoque_project.settings')

application = get_wsgi_application()
app = application

