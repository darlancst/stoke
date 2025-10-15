from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, F

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    
    class Meta:
        verbose_name_plural = 'Fornecedores'
    
    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    ativo = models.BooleanField(default=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='produtos')
    preco_venda = models.DecimalField('Preço de Venda', max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return self.nome
    
    @property
    def quantidade_total(self):
        return self.lotes.aggregate(total=Sum('quantidade_atual'))['total'] or 0
    
    @property
    def custo_medio_ponderado(self):
        lotes = self.lotes.filter(quantidade_atual__gt=0)
        if not lotes.exists():
            return Decimal('0.00')
        
        custo_total = sum(lote.quantidade_atual * lote.preco_compra for lote in lotes)
        quantidade_total = sum(lote.quantidade_atual for lote in lotes)
        
        if quantidade_total == 0:
            return Decimal('0.00')
        
        return custo_total / quantidade_total
    
    @property
    def margem_lucro(self):
        if not self.preco_venda or self.custo_medio_ponderado == 0:
            return Decimal('0.00')
        
        return ((self.preco_venda - self.custo_medio_ponderado) / self.preco_venda) * 100
    
    @property
    def quantidade_chegando(self):
        """Quantidade de produtos chegando (pré-cadastro) com mesmo nome"""
        # Import local para evitar circular import
        from django.db.models import Sum as SumAgg
        ProdutoCh = self.__class__.__module__.split('.')[0]
        try:
            return ProdutoChegando.objects.filter(
                nome__iexact=self.nome,
                incluido_estoque=False
            ).aggregate(total=SumAgg('quantidade'))['total'] or 0
        except:
            return 0

class Lote(models.Model):
    produto = models.ForeignKey(Produto, related_name='lotes', on_delete=models.CASCADE)
    quantidade_inicial = models.PositiveIntegerField()
    quantidade_atual = models.PositiveIntegerField()
    preco_compra = models.DecimalField(max_digits=10, decimal_places=2)
    data_entrada = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Lote de {self.produto.nome} - {self.quantidade_atual}/{self.quantidade_inicial}"

class Venda(models.Model):
    TIPO_VENDA_CHOICES = [
        ('LOJA', 'Loja'),
        ('EXTERNA', 'Externa'),
    ]
    STATUS_CHOICES = [
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]
    cliente_nome = models.CharField('Nome do Cliente', max_length=255, blank=True, null=True)
    data = models.DateTimeField(default=timezone.now)
    tipo_venda = models.CharField(max_length=10, choices=TIPO_VENDA_CHOICES, default='LOJA')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONCLUIDA')
    desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Venda #{self.pk} - {self.data.strftime('%d/%m/%Y')}"

    @property
    def teve_devolucao(self):
        return self.devolucoes.exists()
    
    @property
    def quantidade_total_vendida(self):
        return self.itens.aggregate(total=Sum('quantidade'))['total'] or 0
    
    @property
    def quantidade_total_devolvida(self):
        total_devolvido = 0
        for devolucao in self.devolucoes.all():
            total_devolvido += devolucao.itens_devolvidos.aggregate(total=Sum('quantidade'))['total'] or 0
        return total_devolvido
    
    @property
    def tipo_devolucao(self):
        """Retorna o tipo de devolução: 'total', 'parcial' ou None"""
        if not self.teve_devolucao:
            return None
        
        quantidade_vendida = self.quantidade_total_vendida
        quantidade_devolvida = self.quantidade_total_devolvida
        
        if quantidade_devolvida >= quantidade_vendida:
            return 'total'
        else:
            return 'parcial'

    @property
    def valor_bruto(self):
        return self.itens.aggregate(total=Sum(F('quantidade') * F('preco_venda_unitario')))['total'] or Decimal('0.00')

    @property
    def valor_total(self):
        return self.valor_bruto - self.desconto

    @property
    def custo_total(self):
        return sum(item.custo_compra_total_registrado for item in self.itens.all())
    
    @property
    def valor_brindes_dados(self):
        """Valor dos produtos dados como brinde (custo dos brindes)"""
        brindes = self.itens.filter(eh_brinde=True)
        return sum(item.custo_compra_total_registrado for item in brindes)
    
    @property
    def quantidade_brindes_dados(self):
        """Quantidade total de itens dados como brinde"""
        return self.itens.filter(eh_brinde=True).aggregate(total=Sum('quantidade'))['total'] or 0
    
    @property
    def tem_brindes(self):
        """Verifica se a venda tem brindes"""
        return self.itens.filter(eh_brinde=True).exists()

    @property
    def lucro_bruto(self):
        return self.valor_total - self.custo_total
    
    @property
    def meu_lucro(self):
        lucro_bruto_venda = self.lucro_bruto
        
        lucro_revertido_devolucoes = self.devolucoes.aggregate(
            total=Sum(F('itens_devolvidos__quantidade') * (F('itens_devolvidos__item_venda_original__preco_venda_unitario') - (F('itens_devolvidos__item_venda_original__custo_compra_total_registrado') / F('itens_devolvidos__item_venda_original__quantidade'))))
        )['total'] or Decimal('0')

        lucro_liquido = lucro_bruto_venda - lucro_revertido_devolucoes

        if self.tipo_venda == 'LOJA':
            return lucro_liquido / 2
        return lucro_liquido

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_venda_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    custo_compra_total_registrado = models.DecimalField(max_digits=10, decimal_places=2)
    eh_brinde = models.BooleanField('É Brinde', default=False)

    @property
    def subtotal(self):
        """Calcula o subtotal do item (quantidade * preço unitário)"""
        if self.eh_brinde:
            return Decimal('0.00')
        return self.quantidade * self.preco_venda_unitario

    def __str__(self):
        if self.eh_brinde:
            return f"{self.quantidade}x {self.produto.nome} (BRINDE)"
        return f"{self.quantidade}x {self.produto.nome}"

class Configuracao(models.Model):
    nome_empresa = models.CharField('Nome da Empresa', max_length=255, default='Minha Empresa')
    logo = models.ImageField('Logo da Empresa', upload_to='empresa/', blank=True, null=True)
    limite_estoque_baixo = models.PositiveIntegerField('Limite de Estoque Baixo', default=10)
    margem_lucro_ideal = models.DecimalField('Margem de Lucro Ideal (%)', max_digits=5, decimal_places=2, default=Decimal('30.00'))
    dias_produto_parado = models.PositiveIntegerField('Dias sem vender para considerar parado', default=60, help_text='Produtos sem vendas neste período serão listados como parados')

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def __str__(self):
        return f"Configurações de {self.nome_empresa}"

class Devolucao(models.Model):
    venda_original = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='devolucoes')
    data = models.DateTimeField(default=timezone.now)
    motivo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Devolução da Venda #{self.venda_original.pk}"

    @property
    def valor_total_restituido(self):
        total = self.itens_devolvidos.aggregate(
            total=Sum(F('quantidade') * F('item_venda_original__preco_venda_unitario'))
        )['total']
        return total or Decimal('0.00')

class ItemDevolucao(models.Model):
    devolucao = models.ForeignKey(Devolucao, on_delete=models.CASCADE, related_name='itens_devolvidos')
    item_venda_original = models.ForeignKey(ItemVenda, on_delete=models.CASCADE, related_name='itens_devolvidos')
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantidade}x {self.item_venda_original.produto.nome} devolvido"

    @property
    def valor_restituido(self):
        return self.quantidade * self.item_venda_original.preco_venda_unitario


# -------- Produtos Chegando (Pré-cadastro antes de incluir no estoque) --------

class ProdutoChegando(models.Model):
    """Produtos comprados que ainda não chegaram ou não foram incluídos no estoque"""
    nome = models.CharField('Nome do Produto', max_length=255)
    quantidade = models.PositiveIntegerField('Quantidade')
    preco_compra = models.DecimalField('Preço de Compra', max_digits=10, decimal_places=2)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='produtos_chegando', null=True, blank=True)
    data_compra = models.DateField('Data da Compra', default=timezone.now)
    data_prevista_chegada = models.DateField('Previsão de Chegada', blank=True, null=True)
    observacoes = models.TextField('Observações', blank=True, null=True)
    incluido_estoque = models.BooleanField('Já Incluído no Estoque', default=False)
    data_inclusao = models.DateTimeField('Data de Inclusão no Estoque', blank=True, null=True)
    produto_existente = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos_chegando')

    class Meta:
        verbose_name = 'Produto Chegando'
        verbose_name_plural = 'Produtos Chegando'
        ordering = ['-data_compra']

    def __str__(self):
        status = "✓ Incluído" if self.incluido_estoque else "⏳ Chegando"
        return f"{self.nome} ({self.quantidade} un.) - {status}"
