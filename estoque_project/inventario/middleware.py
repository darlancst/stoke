from django.http import JsonResponse
from django_ratelimit.exceptions import Ratelimited

class RatelimitMiddleware:
    """
    Middleware para interceptar exceções de rate limiting e retornar
    respostas amigáveis em JSON para APIs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            # Se for uma requisição AJAX/API, retorna JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or \
               request.path.endswith('.json') or \
               'json' in request.path:
                return JsonResponse({
                    'erro': 'Limite de requisições excedido. Por favor, aguarde um momento.',
                    'limite_atingido': True
                }, status=429)
            # Caso contrário, retorna uma página HTML
            from django.shortcuts import render
            return render(request, 'inventario/rate_limit.html', status=429)
        return None



