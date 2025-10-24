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
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='produtos', null=True, blank=True)
    preco_venda = models.DecimalField('Preço de Venda', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Campos para previsão de estoque
    lead_time_dias = models.PositiveIntegerField(
        'Lead Time (dias)', 
        default=7,
        help_text='Tempo de entrega do fornecedor em dias'
    )
    dias_cobertura_minima = models.PositiveIntegerField(
        'Dias de Cobertura Mínima',
        default=15,
        help_text='Quantidade mínima de dias que o estoque deve cobrir'
    )
    
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
    TIPO_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
    ]
    cliente_nome = models.CharField('Nome do Cliente', max_length=255, blank=True, null=True)
    data = models.DateTimeField(default=timezone.now)
    tipo_venda = models.CharField(max_length=10, choices=TIPO_VENDA_CHOICES, default='LOJA')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONCLUIDA')
    desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Campos de pagamento
    tipo_pagamento = models.CharField('Tipo de Pagamento', max_length=10, choices=TIPO_PAGAMENTO_CHOICES, default='DINHEIRO')
    parcelas = models.PositiveIntegerField('Número de Parcelas', default=1)
    taxa_aplicada = models.DecimalField('Taxa Aplicada (%)', max_digits=5, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        from django.utils import timezone as tz
        data_local = tz.localtime(self.data)
        return f"Venda #{self.pk} - {data_local.strftime('%d/%m/%Y')}"

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
    def valor_taxa_reais(self):
        """Retorna o valor da taxa em reais (calculada sobre o valor total da venda)"""
        if self.taxa_aplicada > 0:
            return (self.valor_total * self.taxa_aplicada) / 100
        return Decimal('0.00')
    
    @property
    def meu_lucro(self):
        lucro_bruto_venda = self.lucro_bruto
        
        lucro_revertido_devolucoes = self.devolucoes.aggregate(
            total=Sum(F('itens_devolvidos__quantidade') * (F('itens_devolvidos__item_venda_original__preco_venda_unitario') - (F('itens_devolvidos__item_venda_original__custo_compra_total_registrado') / F('itens_devolvidos__item_venda_original__quantidade'))))
        )['total'] or Decimal('0')

        lucro_liquido = lucro_bruto_venda - lucro_revertido_devolucoes

        # Desconta as taxas de pagamento do lucro ANTES de dividir por tipo de venda
        # Taxa é aplicada sobre o valor total da venda
        if self.taxa_aplicada > 0:
            valor_taxa = (self.valor_total * self.taxa_aplicada) / 100
            lucro_liquido = lucro_liquido - valor_taxa
        
        # Aplica divisão por tipo de venda APÓS descontar a taxa
        # (na loja, tanto o lucro quanto as taxas são divididos com o sócio)
        if self.tipo_venda == 'LOJA':
            lucro_liquido = lucro_liquido / 2
        
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

class ItemVendaLote(models.Model):
    """Rastreamento de quais lotes foram utilizados em cada item de venda (FIFO)"""
    item_venda = models.ForeignKey(ItemVenda, related_name='lotes_utilizados', on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    quantidade_retirada = models.PositiveIntegerField()
    preco_compra_lote = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Lote Utilizado em Venda'
        verbose_name_plural = 'Lotes Utilizados em Vendas'
    
    def __str__(self):
        return f"Lote #{self.lote.id} - {self.quantidade_retirada} un. - {self.item_venda}"

class Configuracao(models.Model):
    nome_empresa = models.CharField('Nome da Empresa', max_length=255, default='Minha Empresa')
    logo = models.ImageField('Logo da Empresa', upload_to='empresa/', blank=True, null=True)
    limite_estoque_baixo = models.PositiveIntegerField('Limite de Estoque Baixo', default=10)
    margem_lucro_ideal = models.DecimalField('Margem de Lucro Ideal (%)', max_digits=5, decimal_places=2, default=Decimal('30.00'))
    dias_produto_parado = models.PositiveIntegerField('Dias sem vender para considerar parado', default=60, help_text='Produtos sem vendas neste período serão listados como parados')
    dias_analise_tendencias = models.PositiveIntegerField('Período de Análise de Tendências (dias)', default=90, help_text='Quantidade de dias de histórico usado para análise de tendências e previsão de estoque')
    
    # Taxas de pagamento
    taxa_debito = models.DecimalField('Taxa de Débito (%)', max_digits=5, decimal_places=2, default=Decimal('2.00'), help_text='Taxa cobrada em pagamentos no débito')
    taxa_credito_avista = models.DecimalField('Taxa de Crédito à Vista (%)', max_digits=5, decimal_places=2, default=Decimal('3.00'), help_text='Taxa cobrada em pagamentos no crédito em 1x')
    
    # Juros de parcelamento (crédito)
    juros_2x = models.DecimalField('Juros 2x (%)', max_digits=5, decimal_places=2, default=Decimal('3.50'))
    juros_3x = models.DecimalField('Juros 3x (%)', max_digits=5, decimal_places=2, default=Decimal('4.00'))
    juros_4x = models.DecimalField('Juros 4x (%)', max_digits=5, decimal_places=2, default=Decimal('4.50'))
    juros_5x = models.DecimalField('Juros 5x (%)', max_digits=5, decimal_places=2, default=Decimal('5.00'))
    juros_6x = models.DecimalField('Juros 6x (%)', max_digits=5, decimal_places=2, default=Decimal('5.50'))
    juros_7x = models.DecimalField('Juros 7x (%)', max_digits=5, decimal_places=2, default=Decimal('6.00'))
    juros_8x = models.DecimalField('Juros 8x (%)', max_digits=5, decimal_places=2, default=Decimal('6.50'))
    juros_9x = models.DecimalField('Juros 9x (%)', max_digits=5, decimal_places=2, default=Decimal('7.00'))
    juros_10x = models.DecimalField('Juros 10x (%)', max_digits=5, decimal_places=2, default=Decimal('7.50'))
    juros_11x = models.DecimalField('Juros 11x (%)', max_digits=5, decimal_places=2, default=Decimal('8.00'))
    juros_12x = models.DecimalField('Juros 12x (%)', max_digits=5, decimal_places=2, default=Decimal('8.50'))

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def __str__(self):
        return f"Configurações de {self.nome_empresa}"
    
    def get_taxa_pagamento(self, tipo_pagamento, parcelas=1):
        """Retorna a taxa aplicável com base no tipo de pagamento e número de parcelas"""
        if tipo_pagamento == 'DINHEIRO' or tipo_pagamento == 'PIX':
            return Decimal('0.00')
        elif tipo_pagamento == 'DEBITO':
            return self.taxa_debito
        elif tipo_pagamento == 'CREDITO':
            if parcelas == 1:
                return self.taxa_credito_avista
            elif parcelas == 2:
                return self.juros_2x
            elif parcelas == 3:
                return self.juros_3x
            elif parcelas == 4:
                return self.juros_4x
            elif parcelas == 5:
                return self.juros_5x
            elif parcelas == 6:
                return self.juros_6x
            elif parcelas == 7:
                return self.juros_7x
            elif parcelas == 8:
                return self.juros_8x
            elif parcelas == 9:
                return self.juros_9x
            elif parcelas == 10:
                return self.juros_10x
            elif parcelas == 11:
                return self.juros_11x
            elif parcelas == 12:
                return self.juros_12x
        return Decimal('0.00')

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
    devolvido_ao_estoque = models.BooleanField('Devolvido ao estoque', default=False)
    data_retorno_estoque = models.DateTimeField('Data de retorno ao estoque', null=True, blank=True)

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
