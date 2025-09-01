from django.db import models
from django.db.models import Sum, F
from decimal import Decimal
from django.utils import timezone

class Fornecedor(models.Model):
    nome = models.CharField('Nome do Fornecedor', max_length=200, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

class Produto(models.Model):
    nome = models.CharField('Nome do Produto', max_length=200, unique=True)
    descricao = models.TextField('Descrição', blank=True, null=True)
    preco_venda = models.DecimalField('Preço de Venda', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    ativo = models.BooleanField('Ativo', default=True)
    imagem = models.ImageField('Imagem', upload_to='produtos/', blank=True, null=True)

    @property
    def quantidade_total(self):
        return self.lotes.aggregate(total=Sum('quantidade_atual'))['total'] or 0

    @property
    def custo_medio_ponderado(self):
        lotes_com_estoque = self.lotes.filter(quantidade_atual__gt=0)
        custo_total = lotes_com_estoque.aggregate(
            total=Sum(F('quantidade_atual') * F('preco_compra'))
        )['total'] or 0
        quantidade_total = lotes_com_estoque.aggregate(
            total=Sum('quantidade_atual')
        )['total'] or 0
        
        if quantidade_total > 0:
            return custo_total / quantidade_total
        return Decimal('0.00')

    @property
    def margem_lucro(self):
        custo = self.custo_medio_ponderado
        if self.preco_venda and custo and self.preco_venda > 0 and custo > 0:
            return ((self.preco_venda - custo) / custo) * 100
        return None

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

class Lote(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='lotes')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade_inicial = models.PositiveIntegerField('Quantidade Inicial')
    quantidade_atual = models.PositiveIntegerField('Quantidade Atual')
    preco_compra = models.DecimalField('Preço de Compra', max_digits=10, decimal_places=2)
    data_entrada = models.DateTimeField('Data de Entrada', default=timezone.now)

    def __str__(self):
        return f'Lote de {self.produto.nome} - {self.quantidade_atual} un.'

    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['data_entrada']

class Venda(models.Model):
    TIPO_VENDA_CHOICES = [
        ('LOJA', 'Venda na Loja'),
        ('EXTERNA', 'Venda Externa'),
    ]
    STATUS_CHOICES = [
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    ]
    cliente_nome = models.CharField('Nome do Cliente', max_length=200, default='Cliente Anônimo')
    data = models.DateTimeField('Data da Venda', default=timezone.now)
    tipo_venda = models.CharField(max_length=10, choices=TIPO_VENDA_CHOICES, default='LOJA')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='FINALIZADA')
    desconto = models.DecimalField('Desconto', max_digits=10, decimal_places=2, default=Decimal('0.00'))

    @property
    def teve_devolucao(self):
        return self.devolucoes.exists()

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
    def lucro_bruto(self):
        return self.valor_total - self.custo_total
    
    @property
    def meu_lucro(self):
        if self.tipo_venda == 'EXTERNA':
            return self.lucro_bruto * Decimal('0.5')
        return self.lucro_bruto

    def __str__(self):
        return f'Venda #{self.id} para {self.cliente_nome} em {self.data.strftime("%d/%m/%Y")}'

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data']

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT) # Impede exclusão de produto com vendas
    quantidade = models.PositiveIntegerField('Quantidade')
    preco_venda_unitario = models.DecimalField('Preço de Venda (no ato)', max_digits=10, decimal_places=2)
    custo_compra_total_registrado = models.DecimalField('Custo Total de Compra (FIFO)', max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantidade * self.preco_venda_unitario

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} na Venda #{self.venda.id}'

    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'


class Devolucao(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='devolucoes', verbose_name="Venda Original")
    data_devolucao = models.DateTimeField("Data da Devolução", default=timezone.now)
    motivo = models.TextField("Motivo", blank=True)

    @property
    def valor_total_restituido(self):
        total = self.itens_devolvidos.aggregate(
            total=Sum(F('quantidade') * F('item_venda_original__preco_venda_unitario'))
        )['total']
        return total if total is not None else Decimal('0.00')

    def __str__(self):
        return f"Devolução para Venda #{self.venda.id} em {self.data_devolucao.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Devolução"
        verbose_name_plural = "Devoluções"
        ordering = ['-data_devolucao']


class ItemDevolucao(models.Model):
    devolucao = models.ForeignKey(Devolucao, on_delete=models.CASCADE, related_name='itens_devolvidos')
    item_venda_original = models.ForeignKey(ItemVenda, on_delete=models.CASCADE, related_name='devolucoes_deste_item')
    quantidade = models.PositiveIntegerField("Quantidade Devolvida")

    @property
    def produto(self):
        return self.item_venda_original.produto

    @property
    def valor_restituido_item(self):
        return self.quantidade * self.item_venda_original.preco_venda_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Devolvido)"

    class Meta:
        verbose_name = "Item Devolvido"
        verbose_name_plural = "Itens Devolvidos"


class Configuracao(models.Model):
    nome_empresa = models.CharField(max_length=255, default="Meu Estoque")
    limite_estoque_baixo = models.PositiveIntegerField(default=10)
    margem_lucro_ideal = models.DecimalField('Margem de Lucro Ideal (%)', max_digits=5, decimal_places=2, default=Decimal('30.00'))
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return self.nome_empresa

    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Configurações"
