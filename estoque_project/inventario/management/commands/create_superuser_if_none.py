"""
Management command para criar superusuário automaticamente se não existir nenhum.
Uso: python manage.py create_superuser_if_none
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Cria um superusuário se não existir nenhum'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Verifica se já existe algum superusuário
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Superusuário já existe. Nenhuma ação necessária.')
            )
            return
        
        # Pega credenciais das variáveis de ambiente ou usa padrões
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@stoke.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        
        # Cria o superusuário
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Superusuário "{username}" criado com sucesso!')
        )
        self.stdout.write(
            self.style.WARNING('⚠️ IMPORTANTE: Altere a senha após o primeiro login!')
        )

