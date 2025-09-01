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
        fields = ['fornecedor', 'quantidade_inicial', 'preco_compra']
        widgets = {
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_inicial': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'preco_compra': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = ['nome_empresa', 'limite_estoque_baixo', 'margem_lucro_ideal', 'logo']
        widgets = {
            'nome_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'limite_estoque_baixo': forms.NumberInput(attrs={'class': 'form-control'}),
            'margem_lucro_ideal': forms.NumberInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'margem_lucro_ideal': 'Insira o valor percentual (ex: 30 para 30%).',
        } 