from django import forms
from .models import Produto, Fornecedor, Lote, Configuracao

class ProdutoForm(forms.ModelForm):
    # Campos do Lote
    fornecedor = forms.ModelChoiceField(queryset=Fornecedor.objects.all(), required=True, label="Fornecedor", widget=forms.Select(attrs={'class': 'form-select'}))
    quantidade_inicial = forms.IntegerField(label="Quantidade Inicial", min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    preco_compra = forms.DecimalField(label="Preço de Compra (Unitário)", widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Produto
        fields = ['nome', 'preco_venda', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProdutoEditForm(forms.ModelForm):
    quantidade_estoque = forms.IntegerField(
        label="Quantidade em Estoque",
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Ajuste a quantidade total em estoque. Se aumentar, será criado um novo lote; se diminuir, será deduzido dos lotes mais antigos (FIFO).'
    )
    
    class Meta:
        model = Produto
        fields = ['nome', 'preco_venda', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['quantidade_inicial', 'preco_compra']
        widgets = {
            'quantidade_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'preco_compra': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = ['nome_empresa', 'limite_estoque_baixo', 'margem_lucro_ideal', 'dias_produto_parado']
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'limite_estoque_baixo': forms.NumberInput(attrs={'class': 'form-control'}),
            'margem_lucro_ideal': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_produto_parado': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        help_texts = {
            'nome_empresa': 'O nome que aparecerá no sistema.',
            'limite_estoque_baixo': 'Receba alertas quando o estoque atingir este número.',
            'margem_lucro_ideal': 'A margem de lucro que você considera ideal para seus produtos (em %).',
            'dias_produto_parado': 'Produtos sem vendas neste período serão listados como parados no dashboard.',
        } 