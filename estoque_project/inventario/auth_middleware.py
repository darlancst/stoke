"""
Middleware de autenticação para proteger todas as views do sistema.
Redireciona usuários não autenticados para a página de login.
"""
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Middleware que exige login para acessar qualquer página,
    exceto login, logout e arquivos estáticos.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que não precisam de autenticação
        self.exempt_urls = [
            reverse('login'),
            '/logout/',
            '/admin/login/',  # Permitir login do admin
            '/static/',
            '/media/',
            '/favicon.ico',
            '/manifest.webmanifest',
            '/sw.js',
            '/offline/',
        ]
    
    def __call__(self, request):
        # Se o usuário já está autenticado, permite acesso
        if request.user.is_authenticated:
            response = self.get_response(request)
            return response
        
        # Verifica se a URL atual está na lista de exceções
        path = request.path_info
        
        # Permite acesso a URLs isentas
        for exempt_url in self.exempt_urls:
            if path.startswith(exempt_url):
                response = self.get_response(request)
                return response
        
        # Se não está autenticado e não é uma URL isenta, redireciona para login
        login_url = settings.LOGIN_URL
        return redirect(f'{login_url}?next={path}')

