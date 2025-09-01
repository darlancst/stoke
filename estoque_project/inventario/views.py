from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Fornecedor, Lote, Venda, ItemVenda, Configuracao, Devolucao, ItemDevolucao
from .forms import ProdutoForm, ProdutoEditForm, LoteForm, ConfiguracaoForm
from django.http import JsonResponse
import json
from django.db import transaction
from decimal import Decimal
from django.db.models import Sum, F, OuterRef, Subquery, ExpressionWrapper, fields, Case, When, Value
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse

# Create your views here.

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
        'produto__nome'
    ).annotate(
        quantidade_total_vendida=Sum('quantidade')
    ).order_by('-quantidade_total_vendida')[:5]

    # --- NOVO: Top 5 Produtos Mais Lucrativos no Período ---
    produtos_mais_lucrativos = ItemVenda.objects.filter(
        venda__in=vendas_periodo
    ).values(
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
    config, _ = Configuracao.objects.get_or_create(pk=1)
    produtos_estoque_baixo = Produto.objects.annotate(
        qtd_total=Sum('lotes__quantidade_atual')
    ).filter(qtd_total__lt=config.limite_estoque_baixo, ativo=True)

    # --- 3. Dados do Gráfico de Linhas ---
    vendas_por_unidade = {}
    if (data_fim - data_inicio).days <= 90: # Agrupar por dia para períodos curtos
        delta = data_fim - data_inicio
        for i in range(delta.days + 1):
            dia = data_inicio + timedelta(days=i)
            vendas_por_unidade[dia.strftime('%d/%m')] = {'receita': Decimal('0'), 'meu_lucro': Decimal('0')}
        
        for venda in vendas_periodo:
            dia_str = venda.data.strftime('%d/%m')
            if dia_str in vendas_por_unidade:
                vendas_por_unidade[dia_str]['receita'] += venda.valor_total
                vendas_por_unidade[dia_str]['meu_lucro'] += venda.meu_lucro
    else: # Agrupar por mês para períodos longos
        vendas_periodo_meses = vendas_periodo.dates('data', 'month')
        for mes_inicio in vendas_periodo_meses:
            vendas_por_unidade[mes_inicio.strftime('%b/%y')] = {'receita': Decimal('0'), 'meu_lucro': Decimal('0')}

        for venda in vendas_periodo:
            mes_str = venda.data.strftime('%b/%y')
            if mes_str in vendas_por_unidade:
                vendas_por_unidade[mes_str]['receita'] += venda.valor_total
                vendas_por_unidade[mes_str]['meu_lucro'] += venda.meu_lucro
    
    labels_grafico = list(vendas_por_unidade.keys())
    receita_grafico = [v['receita'] for v in vendas_por_unidade.values()]
    meu_lucro_grafico = [v['meu_lucro'] for v in vendas_por_unidade.values()]

    # --- 4. Dados do Gráfico Heatmap (últimos 365 dias) ---
    heatmap_inicio = hoje - timedelta(days=364)
    vendas_heatmap = Venda.objects.filter(data__range=[heatmap_inicio, data_fim_query])
    
    lucro_por_dia = {}
    for venda in vendas_heatmap:
        dia = venda.data.date()
        lucro_por_dia.setdefault(dia, Decimal('0'))
        lucro_por_dia[dia] += venda.meu_lucro

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
        'top_produtos_vendidos': top_produtos_vendidos, # Adicionar ao contexto
        'produtos_mais_lucrativos': produtos_mais_lucrativos, # Adicionar ao contexto
        
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
        produtos_list = Produto.objects.filter(ativo=False)
        titulo = "Produtos Pausados"
        status_atual = 'pausados'
    else:
        produtos_list = Produto.objects.filter(ativo=True)
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
    
    context = {
        'produtos': produtos,
        'titulo': titulo,
        'config': config,
        'status_atual': status_atual,
        'query_atual': query, # Passa a query para o template
    }
    return render(request, 'inventario/listar_produtos.html', context)

@transaction.atomic
def criar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            # Cria o produto usando os campos do formulário que pertencem ao modelo Produto
            produto = Produto.objects.create(
                nome=form.cleaned_data['nome'],
                preco_venda=form.cleaned_data['preco_venda'],
                ativo=form.cleaned_data['ativo'],
                descricao='' # Campo não está mais no form, mas o modelo ainda pode tê-lo
            )

            # Cria o lote inicial com os campos restantes
            Lote.objects.create(
                produto=produto,
                fornecedor=form.cleaned_data.get('fornecedor'),
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
            form.save()
            return redirect('inventario:detalhar_produto', pk=produto.pk)
    else:
        form = ProdutoEditForm(instance=produto)
    
    context = {'form': form, 'titulo': f'Editar Produto: {produto.nome}', 'produto': produto}
    return render(request, 'inventario/editar_produto.html', context)

def detalhar_produto(request, pk):
    config = Configuracao.objects.first()
    produto = get_object_or_404(Produto, pk=pk)
    context = {'produto': produto, 'config': config}
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

def buscar_produtos_json(request):
    termo = request.GET.get('term', '')
    produtos = Produto.objects.annotate(
        quantidade_total_agg=Sum('lotes__quantidade_atual')
    ).filter(
        nome__icontains=termo,
        ativo=True,
        quantidade_total_agg__gt=0
    ).exclude(
        preco_venda__isnull=True
    )

    resultado = [
        {
            'id': produto.id,
            'label': f"{produto.nome} (Estoque: {produto.quantidade_total_agg})",
            'value': produto.nome,
            'preco': str(produto.preco_venda),
            'estoque': produto.quantidade_total_agg
        }
        for produto in produtos
    ]
    return JsonResponse(resultado, safe=False)

def buscar_produtos_listagem_json(request):
    """API para busca em tempo real na listagem de produtos"""
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
            'ativo': produto.ativo
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
            cliente_nome = dados.get('cliente_nome', 'Cliente Anônimo')
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


            venda = Venda.objects.create(
                cliente_nome=cliente_nome,
                tipo_venda=tipo_venda,
                desconto=desconto
            )

            for item_data in itens_venda:
                produto_id = item_data['id']
                quantidade_vendida = int(item_data['quantidade'])
                produto = Produto.objects.get(id=produto_id)

                if produto.quantidade_total < quantidade_vendida:
                    raise ValueError(f'Estoque insuficiente para o produto: {produto.nome}')
                
                preco_no_ato_da_venda = produto.preco_venda
                if preco_no_ato_da_venda is None:
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
                    custo_compra_total_registrado=custo_total_item
                )

            return JsonResponse({'sucesso': True, 'venda_id': venda.id})
        except Exception as e:
            return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)
    return render(request, 'inventario/nova_venda.html')

def listar_vendas(request):
    vendas = Venda.objects.all().order_by('-data')
    return render(request, 'inventario/listar_vendas.html', {'vendas': vendas})

def detalhar_venda(request, pk):
    venda = get_object_or_404(Venda, pk=pk)
    return render(request, 'inventario/detalhar_venda.html', {'venda': venda})

# --- Devoluções ---

def listar_devolucoes(request):
    devolucoes = Devolucao.objects.select_related('venda').all().order_by('-data_devolucao')
    
    venda_id_filtrada = request.GET.get('venda_id')
    if venda_id_filtrada:
        devolucoes = devolucoes.filter(venda__id=venda_id_filtrada)

    context = {
        'devolucoes': devolucoes,
        'venda_id_filtrada': venda_id_filtrada
    }
    return render(request, 'inventario/listar_devolucoes.html', context)

def detalhar_devolucao(request, pk):
    devolucao = get_object_or_404(Devolucao.objects.select_related('venda'), pk=pk)
    context = {
        'devolucao': devolucao
    }
    return render(request, 'inventario/detalhar_devolucao.html', context)

@transaction.atomic
def registrar_devolucao(request, venda_pk):
    venda = get_object_or_404(Venda, pk=venda_pk)

    if request.method == 'POST':
        devolucao = Devolucao.objects.create(
            venda=venda,
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


# --- Configurações ---

def configuracoes(request):
    config, created = Configuracao.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            return redirect('inventario:configuracoes')
    else:
        form = ConfiguracaoForm(instance=config)
    
    return render(request, 'inventario/configuracoes.html', {'form': form})
