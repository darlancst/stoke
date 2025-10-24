from django import forms
from .models import Produto, Fornecedor, Lote, Configuracao

def capitalizar_nome(nome):
    """Capitaliza a primeira letra de cada palavra em um nome"""
    if not nome:
        return nome
    return ' '.join(palavra.capitalize() for palavra in nome.strip().split())

class ProdutoForm(forms.ModelForm):
    # Campos do Lote
    fornecedor = forms.ModelChoiceField(queryset=Fornecedor.objects.all(), required=True, label="Fornecedor", widget=forms.Select(attrs={'class': 'form-select'}))
    quantidade_inicial = forms.IntegerField(label="Quantidade Inicial", min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    preco_compra = forms.DecimalField(label="Preço de Compra (Unitário)", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0,00'}))

    class Meta:
        model = Produto
        fields = ['nome', 'preco_venda', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0,00'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        return capitalizar_nome(nome)

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
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0,00'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        return capitalizar_nome(nome)

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['quantidade_inicial', 'preco_compra']
        widgets = {
            'quantidade_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'preco_compra': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0,00'}),
        }

class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = [
            'nome_empresa', 'limite_estoque_baixo', 'margem_lucro_ideal', 
            'dias_produto_parado', 'dias_analise_tendencias',
            'taxa_debito', 'taxa_credito_avista',
            'juros_2x', 'juros_3x', 'juros_4x', 'juros_5x', 'juros_6x',
            'juros_7x', 'juros_8x', 'juros_9x', 'juros_10x', 'juros_11x', 'juros_12x'
        ]
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'limite_estoque_baixo': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'margem_lucro_ideal': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
            'dias_produto_parado': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '1'}),
            'dias_analise_tendencias': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '7', 'max': '365'}),
            'taxa_debito': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'taxa_credito_avista': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_2x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_3x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_4x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_5x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_6x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_7x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_8x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_9x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_10x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_11x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'juros_12x': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
        }
        help_texts = {
            'nome_empresa': 'O nome que aparecerá no sistema.',
            'limite_estoque_baixo': 'Receba alertas quando o estoque atingir este número.',
            'margem_lucro_ideal': 'A margem de lucro que você considera ideal para seus produtos (em %).',
            'dias_produto_parado': 'Produtos sem vendas neste período serão listados como parados no dashboard.',
            'dias_analise_tendencias': 'Quantidade de dias de histórico usado para análise de tendências (mínimo: 7, máximo: 365).',
            'taxa_debito': 'Taxa cobrada sobre o valor da venda em pagamentos no débito.',
            'taxa_credito_avista': 'Taxa cobrada sobre o valor da venda em pagamentos no crédito à vista (1x).',
        }

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nome do fornecedor'}),
        }
    
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        return capitalizar_nome(nome) 