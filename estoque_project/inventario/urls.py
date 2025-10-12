from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # PWA
    path('offline/', views.offline, name='offline'),
    path('sw.js', views.service_worker, name='service_worker'),
    # URLs Produto
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produtos/novo/', views.criar_produto, name='criar_produto'),
    path('produtos/<int:pk>/', views.detalhar_produto, name='detalhar_produto'),
    path('produtos/<int:pk>/editar/', views.editar_produto, name='editar_produto'),
    path('produtos/<int:pk>/pausar/', views.pausar_produto, name='pausar_produto'),
    path('produtos/<int:pk>/reativar/', views.reativar_produto, name='reativar_produto'),
    path('produtos/<int:pk>/excluir-permanente/', views.excluir_produto_permanente, name='excluir_produto_permanente'),
    path('produtos/<int:pk>/adicionar-estoque/', views.adicionar_estoque, name='adicionar_estoque'),

    # URLs Vendas
    path('vendas/', views.listar_vendas, name='listar_vendas'),
    path('vendas/nova/', views.criar_venda, name='criar_venda'),
    path('vendas/<int:pk>/', views.detalhar_venda, name='detalhar_venda'),
    
    # URLs Devoluções
    path('devolucoes/', views.listar_devolucoes, name='listar_devolucoes'),
    path('devolucoes/<int:pk>/', views.detalhar_devolucao, name='detalhar_devolucao'),
    path('vendas/<int:venda_pk>/registrar-devolucao/', views.registrar_devolucao, name='registrar_devolucao'),

    # URLs Produtos Chegando
    path('chegando/', views.listar_produtos_chegando, name='listar_produtos_chegando'),
    path('chegando/novo/', views.criar_produto_chegando, name='criar_produto_chegando'),
    path('chegando/<int:pk>/excluir/', views.excluir_produto_chegando, name='excluir_produto_chegando'),
    path('chegando/<int:pk>/incluir/', views.incluir_no_estoque, name='incluir_no_estoque'),

    # URLs API
    path('api/buscar-produtos/', views.buscar_produtos_json, name='buscar_produtos_json'),
    path('api/buscar-produtos-listagem/', views.buscar_produtos_listagem_json, name='buscar_produtos_listagem_json'),
    path('api/buscar-vendas-listagem/', views.buscar_vendas_listagem_json, name='buscar_vendas_listagem_json'),
    path('api/criar-fornecedor/', views.criar_fornecedor_rapido_json, name='criar_fornecedor_rapido'),

    # URLs Configurações
    path('configuracoes/', views.configuracoes, name='configuracoes'),
] 