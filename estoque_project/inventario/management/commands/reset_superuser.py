"""
Management command para resetar e recriar o superusuário.
Uso: python manage.py reset_superuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Deleta todos os usuários e recria o superusuário das variáveis de ambiente'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Pega credenciais das variáveis de ambiente
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@stoke.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        
        # Deletar TODOS os usuários
        count = User.objects.all().count()
        User.objects.all().delete()
        
        self.stdout.write(
            self.style.WARNING(f'Deletados {count} usuário(s) existente(s).')
        )
        
        # Criar novo superusuário
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Superusuário "{username}" criado com sucesso!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📧 Email: {email}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'🔑 Senha: {password}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'\n🚀 Agora você pode fazer login em: https://stoke-mb54.onrender.com/login/')
        )

