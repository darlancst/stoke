from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Fornecedor, Lote, Venda, ItemVenda, Configuracao, Devolucao, ItemDevolucao, ProdutoChegando
from .forms import ProdutoForm, ProdutoEditForm, LoteForm, ConfiguracaoForm, FornecedorForm
from django.http import JsonResponse
import json
from django.db import transaction
from decimal import Decimal
from django.db.models import Sum, F, OuterRef, Subquery, ExpressionWrapper, fields, Case, When, Value, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.urls import reverse
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

# Create your views here.

def capitalizar_nome(nome):
    """Capitaliza a primeira letra de cada palavra em um nome"""
    if not nome:
        return nome
    return ' '.join(palavra.capitalize() for palavra in nome.strip().split())

def dashboard(request):
    """
    Exibe a página principal do dashboard com estatísticas e informações rápidas,
    permitindo a filtragem por período.
    """
    # --- 1. Lógica de Filtro de Data ---
    periodo = request.GET.get('periodo', '30d') # Padrão: Últimos 30 dias
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')

    hoje = timezone.localtime(timezone.now()).date()
    
    if periodo == '7d':
        data_inicio = hoje - timedelta(days=6)
        data_fim = hoje
    elif periodo == 'anual':
        data_inicio = hoje - timedelta(days=364)
        data_fim = hoje
    elif periodo == 'custom' and data_inicio_str and data_fim_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            periodo = '30d' # Volta ao padrão se as datas forem inválidas
            data_inicio = hoje - timedelta(days=29)
            data_fim = hoje
    else: # Padrão '30d'
        periodo = '30d'
        data_inicio = hoje - timedelta(days=29)
        data_fim = hoje
    
    # Garante que a data fim inclua o dia inteiro
    data_fim_query = datetime.combine(data_fim, datetime.max.time())

    # --- 2. Recalcular Estatísticas com Base no Filtro ---
    vendas_periodo = Venda.objects.filter(data__range=[data_inicio, data_fim_query])
    
    # Cards
    valor_total_estoque = Lote.objects.filter(produto__ativo=True).aggregate(
        total=Sum(F('quantidade_atual') * F('preco_compra'))
    )['total'] or Decimal('0')
    
    numero_vendas = vendas_periodo.count()
    meu_lucro_total = sum(venda.meu_lucro for venda in vendas_periodo)
    receita_total = sum(venda.valor_total for venda in vendas_periodo) # Nova métrica

    # --- NOVO: Top 5 Produtos Mais Vendidos no Período ---
    top_produtos_vendidos = ItemVenda.objects.filter(
        venda__in=vendas_periodo
    ).values(
        'produto__id',
        'produto__nome'
    ).annotate(
        quantidade_total_vendida=Sum('quantidade')
    ).order_by('-quantidade_total_vendida')[:5]

    # --- NOVO: Top 5 Produtos Mais Lucrativos no Período ---
    produtos_mais_lucrativos = ItemVenda.objects.filter(
        venda__in=vendas_periodo
    ).values(
        'produto__id',
        'produto__nome'
    ).annotate(
        receita_total=Sum(F('quantidade') * F('preco_venda_unitario')),
        custo_total=Sum('custo_compra_total_registrado'),
        lucro_total=F('receita_total') - F('custo_total'),
        margem_lucro=Case(
            When(receita_total__gt=0, then=ExpressionWrapper(
                F('lucro_total') * 100 / F('receita_total'),
                output_field=fields.DecimalField(max_digits=5, decimal_places=2)
            )),
            default=Value(0),
            output_field=fields.DecimalField(max_digits=5, decimal_places=2)
        )
    ).order_by('-lucro_total')[:5]

    # Tabela de estoque baixo (não depende do período)
    config, _ = Configuracao.objects.get_or_create()

    # Produtos com estoque baixo
    produtos_estoque_baixo = Produto.objects.annotate(
        qtd_total=Sum('lotes__quantidade_atual')
    ).filter(qtd_total__lt=config.limite_estoque_baixo, ativo=True)
    
    # Produtos parados (há mais de X dias no estoque sem vender, conforme configuração)
    produtos_com_estoque = Produto.objects.annotate(
        qtd_total=Sum('lotes__quantidade_atual')
    ).filter(qtd_total__gt=0, ativo=True)
    
    produtos_parados = []
    for produto in produtos_com_estoque:
        # Busca a última venda deste produto
        ultima_venda_item = ItemVenda.objects.filter(
            produto=produto
        ).order_by('-venda__data').first()
        
        # Calcula há quantos dias está parado
        if ultima_venda_item:
            # Produto já foi vendido - calcula dias desde a última venda
            # Converter para timezone local antes de extrair a data
            data_ultima_venda = timezone.localtime(ultima_venda_item.venda.data).date()
            dias_parado = (hoje - data_ultima_venda).days
        else:
            # Produto nunca foi vendido - calcula dias desde o lote mais antigo
            lote_mais_antigo = produto.lotes.filter(quantidade_atual__gt=0).order_by('data_entrada').first()
            if lote_mais_antigo:
                # data_entrada também precisa de conversão se for DateTimeField
                data_entrada = timezone.localtime(lote_mais_antigo.data_entrada).date()
                dias_parado = (hoje - data_entrada).days
            else:
                continue  # Pula se não houver lote
        
        # Só adiciona se o produto está parado há X dias ou mais (conforme configuração)
        if dias_parado >= config.dias_produto_parado:
            produtos_parados.append({
                'produto': produto,
                'dias_parado': dias_parado,
                'quantidade': produto.quantidade_total
            })
    
    # Ordena por dias parado (maior tempo primeiro) e limita a 5
    produtos_parados = sorted(produtos_parados, key=lambda x: x['dias_parado'], reverse=True)[:5]

    # --- 3. Dados do Gráfico de Linhas ---
    vendas_por_unidade = {}
    if (data_fim - data_inicio).days <= 90: # Agrupar por dia para períodos curtos
        delta = data_fim - data_inicio
        for i in range(delta.days + 1):
            dia = data_inicio + timedelta(days=i)
            vendas_por_unidade[dia.strftime('%d/%m')] = {'receita': Decimal('0'), 'meu_lucro': Decimal('0')}
        
        for venda in vendas_periodo:
            # Converter para timezone local antes de formatar
            data_local = timezone.localtime(venda.data)
            dia_str = data_local.strftime('%d/%m')
            if dia_str in vendas_por_unidade:
                vendas_por_unidade[dia_str]['receita'] += venda.valor_total
                vendas_por_unidade[dia_str]['meu_lucro'] += venda.meu_lucro
    else: # Agrupar por mês para períodos longos
        # Criar dicionário de meses primeiro (baseado no período)
        meses = set()
        for venda in vendas_periodo:
            data_local = timezone.localtime(venda.data)
            mes_str = data_local.strftime('%b/%y')
            meses.add(mes_str)
        
        for mes_str in sorted(meses):
            vendas_por_unidade[mes_str] = {'receita': Decimal('0'), 'meu_lucro': Decimal('0')}

        for venda in vendas_periodo:
            # Converter para timezone local antes de formatar
            data_local = timezone.localtime(venda.data)
            mes_str = data_local.strftime('%b/%y')
            if mes_str in vendas_por_unidade:
                vendas_por_unidade[mes_str]['receita'] += venda.valor_total
                vendas_por_unidade[mes_str]['meu_lucro'] += venda.meu_lucro
    
    labels_grafico = list(vendas_por_unidade.keys())
    receita_grafico = [v['receita'] for v in vendas_por_unidade.values()]
    meu_lucro_grafico = [v['meu_lucro'] for v in vendas_por_unidade.values()]

    # --- 4. Dados do Gráfico Heatmap (últimos 365 dias) ---
    heatmap_inicio = hoje - timedelta(days=364)
    vendas_heatmap = Venda.objects.filter(
        data__range=[heatmap_inicio, data_fim_query],
        status='CONCLUIDA'  # Apenas vendas concluídas
    ).prefetch_related('itens', 'devolucoes__itens_devolvidos')
    
    lucro_por_dia = {}
    for venda in vendas_heatmap:
        # Converter para timezone local antes de extrair a data
        data_local = timezone.localtime(venda.data)
        dia = data_local.date()
        lucro_por_dia.setdefault(dia, Decimal('0'))
        lucro_venda = venda.meu_lucro
        lucro_por_dia[dia] += lucro_venda

    heatmap_data = []
    max_lucro = max(lucro_por_dia.values()) if lucro_por_dia else 0
    for i in range(365):
        dia = heatmap_inicio + timedelta(days=i)
        lucro = lucro_por_dia.get(dia, 0)
        
        # Nivelar o lucro em 5 categorias para as cores
        nivel = 0
        if max_lucro > 0:
            if lucro > max_lucro * Decimal('0.75'): nivel = 4
            elif lucro > max_lucro * Decimal('0.50'): nivel = 3
            elif lucro > max_lucro * Decimal('0.25'): nivel = 2
            elif lucro > 0: nivel = 1
        
        heatmap_data.append({
            'data': dia.isoformat(),
            'lucro': float(lucro),
            'nivel': nivel
        })
    
    # --- 5. Contexto Final ---
    context = {
        'valor_total_estoque': valor_total_estoque,
        'numero_vendas': numero_vendas,
        'meu_lucro_total': meu_lucro_total,
        'receita_total': receita_total,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'produtos_parados': produtos_parados,
        'dias_limite_parado': config.dias_produto_parado,  # Quantidade de dias conforme configuração
        'top_produtos_vendidos': top_produtos_vendidos,
        'produtos_mais_lucrativos': produtos_mais_lucrativos,
        'config': config,  # Adiciona config ao contexto para uso no template
        
        # Dados para o formulário de filtro
        'periodo_selecionado': periodo,
        'data_inicio_selecionada': data_inicio.strftime('%Y-%m-%d') if data_inicio else '',
        'data_fim_selecionada': data_fim.strftime('%Y-%m-%d') if data_fim else '',
        'hoje_str': hoje.strftime('%Y-%m-%d'),
        'labels_grafico': json.dumps(labels_grafico),
        'receita_grafico': json.dumps(receita_grafico, cls=DjangoJSONEncoder),
        'meu_lucro_grafico': json.dumps(meu_lucro_grafico, cls=DjangoJSONEncoder),
        'heatmap_data': json.dumps(heatmap_data),
    }
    return render(request, 'inventario/dashboard.html', context)

# --- CRUD Produto ---

def listar_produtos(request):
    status = request.GET.get('status', 'ativos')
    query = request.GET.get('q', '') # Adiciona a busca
    config = Configuracao.objects.first()

    if status == 'pausados':
        # Otimização: carrega fornecedor junto
        produtos_list = Produto.objects.select_related('fornecedor').filter(ativo=False)
        titulo = "Produtos Pausados"
        status_atual = 'pausados'
    else:
        # Otimização: carrega fornecedor junto
        produtos_list = Produto.objects.select_related('fornecedor').filter(ativo=True)
        titulo = "Produtos em Estoque"
        status_atual = 'ativos'

    if query:
        produtos_list = produtos_list.filter(nome__icontains=query)

    produtos = produtos_list.annotate(
        quantidade_total_agg=Sum('lotes__quantidade_atual'),
        custo_total=Sum(F('lotes__quantidade_atual') * F('lotes__preco_compra'))
    ).annotate(
        custo_medio_ponderado_agg=Case(
            When(quantidade_total_agg__gt=0, then=F('custo_total') / F('quantidade_total_agg')),
            default=Value(0),
            output_field=fields.DecimalField(max_digits=10, decimal_places=2)
        )
    ).annotate(
        margem_lucro_agg=Case(
            When(custo_medio_ponderado_agg__gt=0, then=ExpressionWrapper(
                (F('preco_venda') - F('custo_medio_ponderado_agg')) * 100 / F('custo_medio_ponderado_agg'),
                output_field=fields.DecimalField(max_digits=5, decimal_places=2)
            )),
            default=Value(None),
            output_field=fields.DecimalField(max_digits=5, decimal_places=2, null=True)
        )
    ).order_by('nome')
    
    # Calcular estatísticas gerais (antes da paginação)
    total_produtos_diferentes = produtos.count()
    quantidade_total_geral = produtos.aggregate(
        total=Sum('quantidade_total_agg')
    )['total'] or 0
    
    # Paginação (30 produtos por página)
    paginator = Paginator(produtos, 30)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    context = {
        'page_obj': page_obj,
        'produtos': page_obj,  # Mantém compatibilidade com template
        'titulo': titulo,
        'config': config,
        'status_atual': status_atual,
        'query_atual': query,
        'total_produtos_diferentes': total_produtos_diferentes,
        'quantidade_total_geral': quantidade_total_geral,
    }
    return render(request, 'inventario/listar_produtos.html', context)

@transaction.atomic
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                produto = Produto.objects.create(
                    nome=form.cleaned_data['nome'],
                    preco_venda=form.cleaned_data['preco_venda'],
                    fornecedor=form.cleaned_data['fornecedor']
                )

                Lote.objects.create(
                    produto=produto,
                    quantidade_inicial=form.cleaned_data['quantidade_inicial'],
                    quantidade_atual=form.cleaned_data['quantidade_inicial'],
                    preco_compra=form.cleaned_data['preco_compra']
                )
            return redirect('inventario:listar_produtos')
    else:
        form = ProdutoForm()
    
    context = {'form': form, 'titulo': 'Adicionar Novo Produto e Lote Inicial'}
    return render(request, 'inventario/produto_form.html', context)

def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoEditForm(request.POST, instance=produto)
        if form.is_valid():
            # Salvar o produto (nome, preço, ativo)
            form.save()
            
            # Processar ajuste de quantidade se fornecido
            nova_quantidade = form.cleaned_data.get('quantidade_estoque')
            if nova_quantidade is not None:
                quantidade_atual = produto.quantidade_total
                diferenca = nova_quantidade - quantidade_atual
                
                if diferenca > 0:
                    # Aumentar estoque: criar novo lote de ajuste
                    fornecedor_padrao = Fornecedor.objects.first()
                    if fornecedor_padrao:
                        Lote.objects.create(
                            produto=produto,
                            fornecedor=fornecedor_padrao,
                            quantidade_inicial=diferenca,
                            quantidade_atual=diferenca,
                            preco_compra=produto.custo_medio_ponderado or produto.preco_venda
                        )
                        messages.success(request, f'Estoque aumentado em {diferenca} unidades.')
                elif diferenca < 0:
                    # Diminuir estoque: remover dos lotes mais antigos (FIFO)
                    quantidade_a_remover = abs(diferenca)
                    lotes_disponiveis = produto.lotes.filter(quantidade_atual__gt=0).order_by('data_entrada')
                    
                    for lote in lotes_disponiveis:
                        if quantidade_a_remover <= 0:
                            break
                        
                        if lote.quantidade_atual <= quantidade_a_remover:
                            # Remover todo o lote
                            quantidade_a_remover -= lote.quantidade_atual
                            lote.quantidade_atual = 0
                            lote.save()
                        else:
                            # Remover parcialmente
                            lote.quantidade_atual -= quantidade_a_remover
                            lote.save()
                            quantidade_a_remover = 0
                    
                    messages.success(request, f'Estoque reduzido em {abs(diferenca)} unidades.')
            
            return redirect('inventario:detalhar_produto', pk=produto.pk)
    else:
        form = ProdutoEditForm(instance=produto)
        # Preencher o campo de quantidade com o valor atual
        form.fields['quantidade_estoque'].initial = produto.quantidade_total
    
    context = {'form': form, 'titulo': f'Editar Produto: {produto.nome}', 'produto': produto}
    return render(request, 'inventario/editar_produto.html', context)

def detalhar_produto(request, pk):
    config = Configuracao.objects.first()
    produto = get_object_or_404(Produto, pk=pk)
    
    # Pega o lote FIFO (mais antigo disponível)
    lote_fifo = produto.lotes.filter(quantidade_atual__gt=0).order_by('data_entrada').first()
    
    # Calcula o lucro unitário baseado no lote FIFO
    lucro_unitario_fifo = None
    if lote_fifo and produto.preco_venda:
        lucro_unitario_fifo = produto.preco_venda - lote_fifo.preco_compra
    
    context = {
        'produto': produto,
        'config': config,
        'lote_fifo': lote_fifo,
        'lucro_unitario_fifo': lucro_unitario_fifo
    }
    return render(request, 'inventario/detalhar_produto.html', context)

@require_POST
def reativar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    produto.ativo = True
    produto.save()
    messages.success(request, f"Produto '{produto.nome}' reativado com sucesso!")
    return redirect('inventario:listar_produtos')

@require_POST
def pausar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    produto.ativo = False
    produto.save()
    messages.success(request, f"Produto '{produto.nome}' pausado com sucesso!")
    return redirect('inventario:listar_produtos')

@require_POST
def excluir_produto_permanente(request, pk):
    produto = get_object_or_404(Produto, pk=pk)

    if ItemVenda.objects.filter(produto=produto).exists():
        messages.error(request, f"Não é possível excluir '{produto.nome}', pois ele possui histórico de vendas. Você pode mantê-lo pausado.")
        return redirect(reverse('inventario:listar_produtos') + '?status=pausados')

    nome_produto = produto.nome
    produto.delete()
    messages.success(request, f"Produto '{nome_produto}' foi excluído permanentemente.")
    return redirect(reverse('inventario:listar_produtos') + '?status=pausados')


# --- Estoque ---

def adicionar_estoque(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.produto = produto
            lote.quantidade_atual = lote.quantidade_inicial
            lote.save()
            return redirect('inventario:detalhar_produto', pk=produto.pk)
    else:
        form = LoteForm()
    
    context = {
        'form': form,
        'produto': produto,
        'titulo': f'Adicionar Lote para {produto.nome}'
    }
    return render(request, 'inventario/adicionar_estoque.html', context)

@require_POST
def criar_fornecedor_rapido_json(request):
    try:
        dados = json.loads(request.body)
        nome_fornecedor = dados.get('nome')
        if not nome_fornecedor:
            return JsonResponse({'sucesso': False, 'erro': 'O nome do fornecedor é obrigatório.'}, status=400)

        fornecedor, created = Fornecedor.objects.get_or_create(nome=nome_fornecedor)
        
        return JsonResponse({
            'sucesso': True,
            'id': fornecedor.id,
            'nome': fornecedor.nome
        })
    except Exception as e:
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)


# --- Vendas ---

@ratelimit(key='ip', rate='60/m', method='GET')
def buscar_produtos_json(request):
    """API de busca de produtos com limite de 60 requisições por minuto por IP"""
    termo = request.GET.get('term', '')
    produtos = Produto.objects.annotate(
        quantidade_total_agg=Sum('lotes__quantidade_atual')
    ).filter(
        nome__icontains=termo,
        ativo=True
    ).exclude(
        preco_venda__isnull=True
    )

    resultado = []
    for produto in produtos:
        estoque_atual = produto.quantidade_total_agg if produto.quantidade_total_agg else 0
        
        # Pega o custo FIFO (primeiro lote disponível, mais antigo)
        lote_fifo = produto.lotes.filter(quantidade_atual__gt=0).order_by('data_entrada').first()
        custo_fifo = lote_fifo.preco_compra if lote_fifo else Decimal('0')
        
        # Adiciona indicador visual se sem estoque
        if estoque_atual == 0:
            label = f"{produto.nome} (SEM ESTOQUE)"
        else:
            label = f"{produto.nome} (Estoque: {estoque_atual})"
        
        resultado.append({
            'id': produto.id,
            'label': label,
            'value': produto.nome,
            'preco': str(produto.preco_venda),
            'custo': str(custo_fifo),
            'estoque': estoque_atual,
            'sem_estoque': estoque_atual == 0
        })
    
    return JsonResponse(resultado, safe=False)

@ratelimit(key='ip', rate='60/m', method='GET')
def buscar_produtos_listagem_json(request):
    """API para busca em tempo real na listagem de produtos - Limite: 60 req/min"""
    query = request.GET.get('q', '')
    status = request.GET.get('status', 'ativos')
    
    if status == 'pausados':
        produtos_list = Produto.objects.filter(ativo=False)
    else:
        produtos_list = Produto.objects.filter(ativo=True)
    
    if query:
        produtos_list = produtos_list.filter(nome__icontains=query)
    
    config = Configuracao.objects.first()
    
    produtos = produtos_list.annotate(
        quantidade_total_agg=Sum('lotes__quantidade_atual'),
        custo_total=Sum(F('lotes__quantidade_atual') * F('lotes__preco_compra'))
    ).annotate(
        custo_medio_ponderado_agg=Case(
            When(quantidade_total_agg__gt=0, then=F('custo_total') / F('quantidade_total_agg')),
            default=Value(0),
            output_field=fields.DecimalField(max_digits=10, decimal_places=2)
        )
    ).annotate(
        margem_lucro_agg=Case(
            When(custo_medio_ponderado_agg__gt=0, then=ExpressionWrapper(
                (F('preco_venda') - F('custo_medio_ponderado_agg')) * 100 / F('custo_medio_ponderado_agg'),
                output_field=fields.DecimalField(max_digits=5, decimal_places=2)
            )),
            default=Value(None),
            output_field=fields.DecimalField(max_digits=5, decimal_places=2, null=True)
        )
    ).order_by('nome')
    
    produtos_data = []
    for produto in produtos:
        margem_cor = 'success' if config and produto.margem_lucro_agg and produto.margem_lucro_agg >= config.margem_lucro_ideal else 'danger'
        
        produtos_data.append({
            'id': produto.pk,
            'nome': produto.nome,
            'quantidade_total_agg': produto.quantidade_total_agg or 0,
            'preco_venda': float(produto.preco_venda),
            'custo_medio_ponderado_agg': float(produto.custo_medio_ponderado_agg or 0),
            'margem_lucro_agg': float(produto.margem_lucro_agg) if produto.margem_lucro_agg else None,
            'margem_cor': margem_cor,
            'ativo': produto.ativo,
            'quantidade_chegando': int(produto.quantidade_chegando or 0)
        })
    
    return JsonResponse({
        'produtos': produtos_data,
        'total': len(produtos_data)
    })

@transaction.atomic
def criar_venda(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            cliente_nome = dados.get('cliente_nome', '').strip()
            cliente_nome = capitalizar_nome(cliente_nome) if cliente_nome else None
            tipo_venda = dados.get('tipo_venda', 'LOJA')
            desconto = Decimal(dados.get('desconto', '0.00'))
            itens_venda = dados.get('itens', [])

            if not itens_venda:
                return JsonResponse({'sucesso': False, 'erro': 'A venda deve ter pelo menos um item.'}, status=400)
            
            # Valida desconto antes de criar a venda
            valor_bruto_temp = 0
            for item_data in itens_venda:
                produto = Produto.objects.get(id=item_data['id'])
                valor_bruto_temp += produto.preco_venda * int(item_data['quantidade'])
            
            if desconto > valor_bruto_temp:
                return JsonResponse({'sucesso': False, 'erro': 'O desconto não pode ser maior que o valor total da venda.'}, status=400)


            with transaction.atomic():
                venda = Venda.objects.create(
                    cliente_nome=cliente_nome,
                    tipo_venda=tipo_venda,
                    desconto=desconto
                )

                for item_data in itens_venda:
                    produto_id = item_data['id']
                    quantidade_vendida = int(item_data['quantidade'])
                    eh_brinde = item_data.get('eh_brinde', False)
                    produto = Produto.objects.get(id=produto_id)

                    if produto.quantidade_total < quantidade_vendida:
                        raise ValueError(f'Estoque insuficiente para o produto: {produto.nome}')
                    
                    preco_no_ato_da_venda = Decimal('0.00') if eh_brinde else produto.preco_venda
                    if not eh_brinde and preco_no_ato_da_venda is None:
                        raise ValueError(f'O produto {produto.nome} está sem preço de venda definido.')

                    quantidade_a_baixar = quantidade_vendida
                    custo_total_item = Decimal('0')
                    lotes_disponiveis = produto.lotes.filter(quantidade_atual__gt=0).order_by('data_entrada')

                    for lote in lotes_disponiveis:
                        if quantidade_a_baixar == 0:
                            break
                        quantidade_retirada_lote = min(lote.quantidade_atual, quantidade_a_baixar)
                        custo_total_item += quantidade_retirada_lote * lote.preco_compra
                        lote.quantidade_atual -= quantidade_retirada_lote
                        lote.save()
                        quantidade_a_baixar -= quantidade_retirada_lote
                    
                    ItemVenda.objects.create(
                        venda=venda,
                        produto=produto,
                        quantidade=quantidade_vendida,
                        preco_venda_unitario=preco_no_ato_da_venda,
                        custo_compra_total_registrado=custo_total_item,
                        eh_brinde=eh_brinde
                    )

            return JsonResponse({'sucesso': True, 'venda_id': venda.id})
        except Exception as e:
            return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)
    return render(request, 'inventario/nova_venda.html')

def listar_vendas(request):
    query = request.GET.get('q', '').strip()
    # Otimização: usa prefetch_related para evitar N+1 queries
    vendas = Venda.objects.prefetch_related(
        'itens',
        'itens__produto',
        'devolucoes',
        'devolucoes__itens_devolvidos'
    )
    if query:
        filtros = Q(cliente_nome__icontains=query)
        if query.isdigit():
            filtros |= Q(id=int(query))
        # Busca por tipo de venda
        termo = query.lower()
        if 'loja' in termo:
            filtros |= Q(tipo_venda='LOJA')
        if 'extern' in termo or 'externa' in termo or 'externo' in termo:
            filtros |= Q(tipo_venda='EXTERNA')
        vendas = vendas.filter(filtros)
    vendas = vendas.order_by('-data')
    
    # Paginação (20 vendas por página)
    paginator = Paginator(vendas, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    return render(request, 'inventario/listar_vendas.html', {
        'page_obj': page_obj,
        'vendas': page_obj,  # Mantém compatibilidade com template
        'query_atual': query,
    })

@ratelimit(key='ip', rate='60/m', method='GET')
def buscar_vendas_listagem_json(request):
    """API para busca em tempo real na listagem de vendas - Limite: 60 req/min"""
    query = request.GET.get('q', '').strip()
    # Otimização: usa prefetch_related para evitar N+1 queries
    vendas_qs = Venda.objects.prefetch_related(
        'itens',
        'itens__produto',
        'devolucoes',
        'devolucoes__itens_devolvidos'
    )
    if query:
        filtros = Q(cliente_nome__icontains=query)
        if query.isdigit():
            filtros |= Q(id=int(query))
        termo = query.lower()
        if 'loja' in termo:
            filtros |= Q(tipo_venda='LOJA')
        if 'extern' in termo or 'externa' in termo or 'externo' in termo:
            filtros |= Q(tipo_venda='EXTERNA')
        vendas_qs = vendas_qs.filter(filtros)
    vendas_qs = vendas_qs.order_by('-data')

    vendas_data = []
    for venda in vendas_qs:
        vendas_data.append({
            'id': venda.id,
            'cliente_nome': venda.cliente_nome or 'Cliente não informado',
            'data': timezone.localtime(venda.data).strftime('%d/%m/%Y %H:%M') if venda.data else '',
            'tipo_venda': venda.tipo_venda,
            'tipo_venda_label': venda.get_tipo_venda_display(),
            'valor_total': float(venda.valor_total),
            'meu_lucro': float(venda.meu_lucro),
            'tipo_devolucao': venda.tipo_devolucao,
            'quantidade_total_vendida': venda.quantidade_total_vendida,
            'quantidade_total_devolvida': venda.quantidade_total_devolvida,
            'tem_brindes': venda.tem_brindes if hasattr(venda, 'tem_brindes') else any(getattr(item, 'eh_brinde', False) for item in venda.itens.all()),
            'quantidade_brindes_dados': getattr(venda, 'quantidade_brindes_dados', 0),
            'valor_brindes_dados': float(getattr(venda, 'valor_brindes_dados', 0) or 0),
            'url_detalhes': reverse('inventario:detalhar_venda', kwargs={'pk': venda.pk}),
        })

    return JsonResponse({
        'vendas': vendas_data,
        'total': len(vendas_data)
    })

def detalhar_venda(request, pk):
    venda = get_object_or_404(Venda, pk=pk)
    return render(request, 'inventario/detalhar_venda.html', {'venda': venda})

# --- Devoluções ---

def listar_devolucoes(request):
    venda_id = request.GET.get('venda_id')
    # Otimização: carrega venda e itens devolvidos de uma vez
    if venda_id:
        devolucoes = Devolucao.objects.filter(
            venda_original_id=venda_id
        ).select_related('venda_original').prefetch_related(
            'itens_devolvidos',
            'itens_devolvidos__item_venda_original',
            'itens_devolvidos__item_venda_original__produto'
        ).order_by('-data')
        mensagem_filtro = f"Exibindo devoluções para a Venda #{venda_id}"
    else:
        devolucoes = Devolucao.objects.select_related(
            'venda_original'
        ).prefetch_related(
            'itens_devolvidos',
            'itens_devolvidos__item_venda_original',
            'itens_devolvidos__item_venda_original__produto'
        ).all().order_by('-data')
        mensagem_filtro = None
    
    # Paginação (15 devoluções por página)
    paginator = Paginator(devolucoes, 15)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'devolucoes': page_obj,  # Mantém compatibilidade com template
        'venda_id_filtrada': venda_id,
        'mensagem_filtro': mensagem_filtro
    }
    return render(request, 'inventario/listar_devolucoes.html', context)

def detalhar_devolucao(request, pk):
    devolucao = get_object_or_404(Devolucao.objects.select_related('venda_original'), pk=pk)
    context = {
        'devolucao': devolucao
    }
    return render(request, 'inventario/detalhar_devolucao.html', context)

@transaction.atomic
def registrar_devolucao(request, venda_pk):
    venda = get_object_or_404(Venda, pk=venda_pk)

    if request.method == 'POST':
        devolucao = Devolucao.objects.create(
            venda_original=venda,
            motivo=request.POST.get('motivo', '')
        )
        
        itens_devolvidos_dados = []
        houve_devolucao = False

        for item_venda in venda.itens.all():
            input_name = f'item_{item_venda.id}'
            quantidade_a_devolver = int(request.POST.get(input_name, 0))

            if quantidade_a_devolver > 0:
                houve_devolucao = True
                
                # Validação
                total_ja_devolvido = ItemDevolucao.objects.filter(item_venda_original=item_venda).aggregate(Sum('quantidade'))['quantidade__sum'] or 0
                if quantidade_a_devolver > (item_venda.quantidade - total_ja_devolvido):
                    messages.error(request, f"Quantidade a devolver para '{item_venda.produto.nome}' é maior que a permitida.")
                    return redirect('inventario:registrar_devolucao', venda_pk=venda.pk)

                itens_devolvidos_dados.append({
                    'item_venda_original': item_venda,
                    'quantidade': quantidade_a_devolver
                })
        
        if not houve_devolucao:
            messages.warning(request, "Nenhum item foi selecionado para devolução.")
            devolucao.delete() # Remove a devolução vazia
            return redirect('inventario:registrar_devolucao', venda_pk=venda.pk)

        # Processar a devolução
        for dados in itens_devolvidos_dados:
            ItemDevolucao.objects.create(devolucao=devolucao, **dados)
            
            # Restaurar estoque no lote mais recente
            produto = dados['item_venda_original'].produto
            lote_mais_recente = produto.lotes.order_by('-data_entrada').first()
            if lote_mais_recente:
                lote_mais_recente.quantidade_atual += dados['quantidade']
                lote_mais_recente.save()
        
        messages.success(request, "Devolução registrada com sucesso e estoque atualizado.")
        return redirect('inventario:listar_devolucoes')

    # Lógica para o GET (exibição inicial)
    itens_venda_com_max_devolucao = []
    for item in venda.itens.all():
        total_ja_devolvido = ItemDevolucao.objects.filter(item_venda_original=item).aggregate(Sum('quantidade'))['quantidade__sum'] or 0
        max_para_devolver = item.quantidade - total_ja_devolvido
        itens_venda_com_max_devolucao.append({
            'item': item,
            'max_para_devolver': max_para_devolver
        })

    context = {
        'venda': venda,
        'itens_venda_com_max_devolucao': itens_venda_com_max_devolucao
    }
    return render(request, 'inventario/registrar_devolucao.html', context)

# --- Produtos Chegando ---

def listar_produtos_chegando(request):
    query = request.GET.get('q', '').strip()
    produtos_chegando = ProdutoChegando.objects.filter(incluido_estoque=False)
    if query:
        produtos_chegando = produtos_chegando.filter(nome__icontains=query)
    produtos_chegando = produtos_chegando.order_by('-data_compra')
    
    # Paginação (20 produtos por página)
    paginator = Paginator(produtos_chegando, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    
    return render(request, 'inventario/listar_produtos_chegando.html', {
        'page_obj': page_obj,
        'produtos_chegando': page_obj,  # Mantém compatibilidade com template
        'query_atual': query,
    })

def criar_produto_chegando(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            nome = capitalizar_nome(dados.get('nome'))
            quantidade = int(dados.get('quantidade'))
            preco_compra = Decimal(str(dados.get('preco_compra')))
            fornecedor_id = dados.get('fornecedor_id')
            data_prevista_chegada = dados.get('data_prevista_chegada')
            observacoes = dados.get('observacoes', '')
            produto_id = dados.get('produto_id')  # ID do produto existente (se selecionado)

            # Verifica fornecedor
            fornecedor = None
            if fornecedor_id:
                try:
                    fornecedor = Fornecedor.objects.get(pk=fornecedor_id)
                except Fornecedor.DoesNotExist:
                    pass

            # Verifica se foi selecionado um produto existente
            produto_existente = None
            if produto_id:
                try:
                    produto_existente = Produto.objects.get(pk=produto_id, ativo=True)
                except Produto.DoesNotExist:
                    pass

            produto_chegando = ProdutoChegando.objects.create(
                nome=nome,
                quantidade=quantidade,
                preco_compra=preco_compra,
                fornecedor=fornecedor,
                data_prevista_chegada=data_prevista_chegada or None,
                observacoes=observacoes,
                produto_existente=produto_existente
            )

            return JsonResponse({'sucesso': True, 'id': produto_chegando.id})
        except Exception as e:
            return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)

    fornecedores = Fornecedor.objects.all()
    return render(request, 'inventario/criar_produto_chegando.html', {'fornecedores': fornecedores})

def excluir_produto_chegando(request, pk):
    produto_chegando = get_object_or_404(ProdutoChegando, pk=pk)
    if request.method == 'POST':
        produto_chegando.delete()
        messages.success(request, 'Produto excluído da lista de chegando.')
        return redirect('inventario:listar_produtos_chegando')
    return render(request, 'inventario/confirmar_exclusao_chegando.html', {'produto_chegando': produto_chegando})

@transaction.atomic
def incluir_no_estoque(request, pk):
    produto_chegando = get_object_or_404(ProdutoChegando, pk=pk, incluido_estoque=False)
    
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            preco_venda = Decimal(str(dados.get('preco_venda')))
            
            # Define o fornecedor (usa do produto_chegando ou do produto existente)
            fornecedor = produto_chegando.fornecedor
            
            # Se tem produto_existente vinculado, usa ele diretamente
            if produto_chegando.produto_existente:
                produto = produto_chegando.produto_existente
                # Usa fornecedor do produto existente se não tiver no produto_chegando
                if not fornecedor:
                    fornecedor = produto.fornecedor
            else:
                # Verifica se já existe produto com esse nome
                produto_existente = Produto.objects.filter(nome__iexact=produto_chegando.nome, ativo=True).first()
                
                if produto_existente:
                    # Adiciona lote ao produto existente
                    produto = produto_existente
                    # Usa fornecedor do produto existente se não tiver no produto_chegando
                    if not fornecedor:
                        fornecedor = produto.fornecedor
                else:
                    # Cria novo produto (pode ser sem fornecedor)
                    produto = Produto.objects.create(
                        nome=produto_chegando.nome,
                        fornecedor=fornecedor,
                        preco_venda=preco_venda,
                        ativo=True
                    )
            
            # Cria lote
            Lote.objects.create(
                produto=produto,
                quantidade_inicial=produto_chegando.quantidade,
                quantidade_atual=produto_chegando.quantidade,
                preco_compra=produto_chegando.preco_compra
            )
            
            # Marca como incluído
            produto_chegando.incluido_estoque = True
            produto_chegando.data_inclusao = timezone.now()
            produto_chegando.save()
            
            return JsonResponse({'sucesso': True, 'produto_id': produto.id})
        except Exception as e:
            return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)
    
    # GET: exibe form
    fornecedores = Fornecedor.objects.all().order_by('nome')
    
    # Se tem produto existente vinculado, pré-preenche dados
    produto_vinculado = None
    if produto_chegando.produto_existente:
        produto_vinculado = produto_chegando.produto_existente
    
    return render(request, 'inventario/incluir_no_estoque.html', {
        'produto_chegando': produto_chegando,
        'fornecedores': fornecedores,
        'produto_vinculado': produto_vinculado
    })


# --- Configurações ---

def configuracoes(request):
    config, created = Configuracao.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('inventario:configuracoes')
    else:
        form = ConfiguracaoForm(instance=config)
    
    # Buscar todos os fornecedores
    fornecedores = Fornecedor.objects.all().order_by('nome')
    fornecedor_form = FornecedorForm()
    
    return render(request, 'inventario/configuracoes.html', {
        'form': form,
        'fornecedores': fornecedores,
        'fornecedor_form': fornecedor_form,
    })


@require_http_methods(["POST"])
def adicionar_fornecedor(request):
    """Adiciona um novo fornecedor"""
    form = FornecedorForm(request.POST)
    if form.is_valid():
        fornecedor = form.save()
        messages.success(request, f'Fornecedor "{fornecedor.nome}" adicionado com sucesso!')
    else:
        messages.error(request, 'Erro ao adicionar fornecedor. Verifique os dados.')
    return redirect('inventario:configuracoes')


@require_http_methods(["POST"])
def excluir_fornecedor(request, pk):
    """Exclui um fornecedor se não estiver sendo usado"""
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    
    # Verifica se o fornecedor está sendo usado em produtos ou produtos chegando
    produtos_usando = fornecedor.produtos.count()
    produtos_chegando_usando = fornecedor.produtos_chegando.count()
    
    if produtos_usando > 0 or produtos_chegando_usando > 0:
        messages.error(
            request, 
            f'Não é possível excluir o fornecedor "{fornecedor.nome}" pois está sendo usado em {produtos_usando} produto(s) e {produtos_chegando_usando} produto(s) chegando.'
        )
    else:
        nome_fornecedor = fornecedor.nome
        fornecedor.delete()
        messages.success(request, f'Fornecedor "{nome_fornecedor}" excluído com sucesso!')
    
    return redirect('inventario:configuracoes')


# --- Retornar Item de Devolução ao Estoque ---

@require_http_methods(["POST"])
def retornar_item_ao_estoque(request, item_id):
    """Retorna um item devolvido ao estoque com seu preço de compra original"""
    item_devolucao = get_object_or_404(ItemDevolucao, pk=item_id)
    
    # Verifica se já foi devolvido
    if item_devolucao.devolvido_ao_estoque:
        messages.warning(request, 'Este item já foi retornado ao estoque.')
        return redirect('inventario:detalhar_devolucao', pk=item_devolucao.devolucao.pk)
    
    try:
        with transaction.atomic():
            # Pega o produto e item de venda original
            produto = item_devolucao.item_venda_original.produto
            item_venda = item_devolucao.item_venda_original
            
            # Calcula o preço de compra unitário original
            if item_venda.custo_compra_total_registrado and item_venda.quantidade > 0:
                preco_compra_unitario = item_venda.custo_compra_total_registrado / item_venda.quantidade
            else:
                preco_compra_unitario = Decimal('0.00')
            
            # Cria um novo lote com a quantidade devolvida
            lote = Lote.objects.create(
                produto=produto,
                quantidade_inicial=item_devolucao.quantidade,
                quantidade_atual=item_devolucao.quantidade,
                preco_compra=preco_compra_unitario,
                data_entrada=timezone.now()
            )
            
            # Marca o item como devolvido ao estoque
            item_devolucao.devolvido_ao_estoque = True
            item_devolucao.data_retorno_estoque = timezone.now()
            item_devolucao.save()
            
            messages.success(
                request, 
                f'{item_devolucao.quantidade} unidade(s) de "{produto.nome}" retornada(s) ao estoque com sucesso!'
            )
    except Exception as e:
        messages.error(request, f'Erro ao retornar item ao estoque: {str(e)}')
    
    return redirect('inventario:detalhar_devolucao', pk=item_devolucao.devolucao.pk)


# --- API de Busca para Devoluções ---

@ratelimit(key='ip', rate='60/m', method='GET')
def buscar_devolucoes_listagem_json(request):
    """API para busca em tempo real na listagem de devoluções - Limite: 60 req/min"""
    query = request.GET.get('q', '').strip()
    
    devolucoes_list = Devolucao.objects.all().select_related('venda_original')
    
    if query:
        # Busca por cliente, ID da venda ou produto
        devolucoes_list = devolucoes_list.filter(
            Q(venda_original__cliente_nome__icontains=query) |
            Q(venda_original__id__icontains=query) |
            Q(itens_devolvidos__item_venda_original__produto__nome__icontains=query)
        ).distinct()
    
    devolucoes_list = devolucoes_list.order_by('-data')
    
    # Serializa os dados
    devolucoes_data = []
    for dev in devolucoes_list:
        devolucoes_data.append({
            'id': dev.id,
            'data': timezone.localtime(dev.data).strftime('%d/%m/%Y %H:%M'),
            'venda_id': dev.venda_original.id,
            'cliente': dev.venda_original.cliente_nome or 'Sem nome',
            'valor_total': float(dev.valor_total_restituido),
            'motivo': dev.motivo or '',
        })
    
    return JsonResponse({'devolucoes': devolucoes_data})


# --- PWA Support ---

def offline(request):
    """Página offline para PWA"""
    return render(request, 'inventario/offline.html')


def service_worker(request):
    """Service Worker para PWA"""
    return render(request, 'inventario/sw.js', content_type='application/javascript')


# --- Análise de Tendências e Previsão de Estoque ---

def analise_tendencias(request):
    """
    Análise de tendências de vendas e previsão de necessidade de reposição de estoque.
    Calcula médias móveis, detecta sazonalidade e sugere reposições baseadas em histórico.
    """
    from collections import defaultdict
    from statistics import mean, stdev
    
    hoje = timezone.localtime(timezone.now()).date()
    
    # Obter período de análise das configurações
    config, _ = Configuracao.objects.get_or_create()
    dias_analise = config.dias_analise_tendencias
    
    # Período de análise
    data_inicio_analise = hoje - timedelta(days=dias_analise - 1)
    
    # Buscar todos os produtos ativos
    produtos = Produto.objects.filter(ativo=True).prefetch_related('lotes')
    
    analises_produtos = []
    
    for produto in produtos:
        # Histórico de vendas diárias dos últimos 90 dias
        vendas_diarias = defaultdict(int)
        
        # Buscar todas as vendas do produto no período
        itens_vendidos = ItemVenda.objects.filter(
            produto=produto,
            venda__data__gte=data_inicio_analise,
            venda__status='CONCLUIDA',
            eh_brinde=False  # Não contar brindes
        ).select_related('venda')
        
        # Preencher vendas diárias
        for item in itens_vendidos:
            data_venda = timezone.localtime(item.venda.data).date()
            vendas_diarias[data_venda] += item.quantidade
        
        # Criar lista de vendas para todos os dias (incluindo dias sem vendas = 0)
        vendas_lista = []
        for i in range(dias_analise):
            data = data_inicio_analise + timedelta(days=i)
            vendas_lista.append(vendas_diarias.get(data, 0))
        
        # Se não houver vendas no período configurado, pular este produto
        total_vendido_periodo = sum(vendas_lista)
        if total_vendido_periodo == 0:
            continue
        
        # Calcular médias móveis
        media_movel_7_dias = mean(vendas_lista[-7:]) if len(vendas_lista) >= 7 else mean(vendas_lista)
        media_movel_14_dias = mean(vendas_lista[-14:]) if len(vendas_lista) >= 14 else mean(vendas_lista)
        media_movel_30_dias = mean(vendas_lista[-30:]) if len(vendas_lista) >= 30 else mean(vendas_lista)
        
        # Desvio padrão para entender volatilidade
        try:
            desvio_padrao = stdev(vendas_lista) if len(vendas_lista) > 1 else 0
        except:
            desvio_padrao = 0
        
        # Tendência: comparar segunda metade do período com primeira metade
        # Requer pelo menos 14 dias de dados (7 dias em cada metade)
        if len(vendas_lista) >= 14:
            metade = len(vendas_lista) // 2
            media_segunda_metade = mean(vendas_lista[metade:])
            media_primeira_metade = mean(vendas_lista[:metade])
            
            if media_primeira_metade > 0:
                variacao_percentual = ((media_segunda_metade - media_primeira_metade) / media_primeira_metade) * 100
            else:
                # Se não havia vendas na primeira metade mas há na segunda
                if media_segunda_metade > 0:
                    variacao_percentual = 100
                else:
                    variacao_percentual = 0
            
            if variacao_percentual > 15:
                tendencia = 'crescente'
                tendencia_icon = '📈'
                tendencia_class = 'success'
            elif variacao_percentual < -15:
                tendencia = 'decrescente'
                tendencia_icon = '📉'
                tendencia_class = 'danger'
            else:
                tendencia = 'estável'
                tendencia_icon = '➡️'
                tendencia_class = 'info'
        else:
            variacao_percentual = 0
            tendencia = 'dados insuficientes'
            tendencia_icon = '❓'
            tendencia_class = 'secondary'
        
        # Estoque atual
        estoque_atual = produto.quantidade_total
        
        # Projeção de demanda futura (baseada na média móvel de 30 dias)
        demanda_diaria_media = media_movel_30_dias
        
        # Dias de cobertura atual (quantos dias o estoque atual vai durar)
        if demanda_diaria_media > 0:
            dias_cobertura_atual = estoque_atual / demanda_diaria_media
        else:
            dias_cobertura_atual = float('inf')
        
        # Calcular ponto de reposição
        # Ponto de reposição = (Demanda diária * Lead Time) + Estoque de Segurança
        # Estoque de Segurança = Demanda diária * Dias de cobertura mínima
        lead_time = produto.lead_time_dias
        dias_cobertura_minima = produto.dias_cobertura_minima
        
        # Adicionar desvio padrão ao estoque de segurança para produtos com vendas voláteis
        estoque_seguranca = (demanda_diaria_media * dias_cobertura_minima) + (desvio_padrao * 1.5)
        ponto_reposicao = (demanda_diaria_media * lead_time) + estoque_seguranca
        
        # Quantidade sugerida para compra
        # Queremos manter estoque para: Lead Time + Cobertura Mínima + 50% extra
        estoque_ideal = demanda_diaria_media * (lead_time + dias_cobertura_minima) * 1.5
        
        # Considerar produtos chegando
        quantidade_chegando = produto.quantidade_chegando
        estoque_projetado = estoque_atual + quantidade_chegando
        
        if estoque_projetado < ponto_reposicao:
            precisa_repor = True
            quantidade_sugerida = max(0, estoque_ideal - estoque_projetado)
            urgencia = 'alta' if dias_cobertura_atual < lead_time else 'média'
            urgencia_class = 'danger' if urgencia == 'alta' else 'warning'
        else:
            precisa_repor = False
            quantidade_sugerida = 0
            urgencia = 'baixa'
            urgencia_class = 'success'
        
        # Detecção de sazonalidade simples (comparar semanas)
        # Agrupar por dia da semana
        vendas_por_dia_semana = defaultdict(list)
        for i, qtd in enumerate(vendas_lista):
            data = data_inicio_analise + timedelta(days=i)
            dia_semana = data.weekday()  # 0 = Segunda, 6 = Domingo
            vendas_por_dia_semana[dia_semana].append(qtd)
        
        # Calcular média por dia da semana
        medias_dia_semana = {}
        dias_nomes = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        for dia in range(7):
            if vendas_por_dia_semana[dia]:
                medias_dia_semana[dias_nomes[dia]] = mean(vendas_por_dia_semana[dia])
        
        # Dia da semana com mais vendas
        if medias_dia_semana:
            dia_mais_vendas = max(medias_dia_semana, key=medias_dia_semana.get)
            media_dia_mais_vendas = medias_dia_semana[dia_mais_vendas]
        else:
            dia_mais_vendas = 'N/A'
            media_dia_mais_vendas = 0
        
        # Custo estimado da reposição sugerida
        custo_medio = produto.custo_medio_ponderado
        
        # Se o custo médio ponderado for 0 (sem estoque), usar o último preço de compra conhecido
        if custo_medio == 0:
            ultimo_lote = produto.lotes.order_by('-data_entrada').first()
            if ultimo_lote:
                custo_medio = ultimo_lote.preco_compra
        
        custo_estimado_reposicao = Decimal(str(quantidade_sugerida)) * custo_medio if quantidade_sugerida > 0 else Decimal('0.00')
        
        analises_produtos.append({
            'produto': produto,
            'estoque_atual': estoque_atual,
            'quantidade_chegando': quantidade_chegando,
            'estoque_projetado': estoque_projetado,
            'total_vendido_periodo': total_vendido_periodo,
            'media_movel_7_dias': round(media_movel_7_dias, 2),
            'media_movel_14_dias': round(media_movel_14_dias, 2),
            'media_movel_30_dias': round(media_movel_30_dias, 2),
            'desvio_padrao': round(desvio_padrao, 2),
            'dias_cobertura_atual': round(dias_cobertura_atual, 1) if dias_cobertura_atual != float('inf') else 999,
            'ponto_reposicao': round(ponto_reposicao, 1),
            'precisa_repor': precisa_repor,
            'quantidade_sugerida': round(quantidade_sugerida),
            'urgencia': urgencia,
            'urgencia_class': urgencia_class,
            'tendencia': tendencia,
            'tendencia_icon': tendencia_icon,
            'tendencia_class': tendencia_class,
            'variacao_percentual': round(variacao_percentual, 1),
            'dia_mais_vendas': dia_mais_vendas,
            'media_dia_mais_vendas': round(media_dia_mais_vendas, 2),
            'custo_estimado_reposicao': custo_estimado_reposicao,
            'vendas_lista': vendas_lista[-30:],  # Últimos 30 dias para gráfico
        })
    
    # Ordenar por urgência (alta primeiro) e depois por quantidade sugerida
    def ordem_urgencia(item):
        if item['urgencia'] == 'alta':
            return (0, -item['quantidade_sugerida'])
        elif item['urgencia'] == 'média':
            return (1, -item['quantidade_sugerida'])
        else:
            return (2, -item['quantidade_sugerida'])
    
    analises_produtos.sort(key=ordem_urgencia)
    
    # Calcular totais e estatísticas gerais
    total_produtos_analisados = len(analises_produtos)
    produtos_precisam_reposicao = sum(1 for p in analises_produtos if p['precisa_repor'])
    produtos_urgencia_alta = sum(1 for p in analises_produtos if p['urgencia'] == 'alta')
    custo_total_reposicao = sum(p['custo_estimado_reposicao'] for p in analises_produtos)
    
    context = {
        'analises_produtos': analises_produtos,
        'total_produtos_analisados': total_produtos_analisados,
        'produtos_precisam_reposicao': produtos_precisam_reposicao,
        'produtos_urgencia_alta': produtos_urgencia_alta,
        'custo_total_reposicao': custo_total_reposicao,
        'data_inicio_analise': data_inicio_analise,
        'data_fim_analise': hoje,
        'dias_analise': dias_analise,
    }
    
    return render(request, 'inventario/analise_tendencias.html', context)
