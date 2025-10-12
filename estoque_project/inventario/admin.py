from django.contrib import admin
from .models import Produto, Fornecedor, Lote, Venda, ItemVenda, Configuracao

# Register your models here.

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1 # Quantos formulários em branco exibir

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'tipo_venda', 'status')
    list_filter = ('status', 'data', 'tipo_venda')
    search_fields = ('id',)
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
    list_display = ('produto', 'quantidade_atual', 'preco_compra', 'data_entrada')
    list_filter = ('produto', 'data_entrada')
    search_fields = ('produto__nome',)

admin.site.register(Configuracao)
