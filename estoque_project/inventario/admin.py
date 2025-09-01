from django.contrib import admin
from .models import Produto, Fornecedor, Lote, Venda, ItemVenda, Configuracao

# Register your models here.

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1 # Quantos formulários em branco exibir

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nome', 'data', 'status', 'valor_total')
    list_filter = ('status', 'data')
    search_fields = ('cliente_nome',)
    inlines = [ItemVendaInline]

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_total', 'preco_venda', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('produto', 'fornecedor', 'quantidade_atual', 'preco_compra', 'data_entrada')
    list_filter = ('produto', 'fornecedor', 'data_entrada')
    search_fields = ('produto__nome', 'fornecedor__nome')

admin.site.register(Configuracao)
