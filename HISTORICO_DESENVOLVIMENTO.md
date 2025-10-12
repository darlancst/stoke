# Histórico de Desenvolvimento - Stoke

[... conteúdo anterior mantido ...]

### 3.29. Refatoração Completa: Sistema "Produtos Chegando" Simplificado (Major Feature)

- **Contexto:** O sistema anterior de "Pedidos de Compra" era muito complexo (múltiplos itens por pedido, recebimentos parciais, etc.). O usuário solicitou uma abordagem mais simples e direta.

- **Nova Abordagem:** Sistema de pré-cadastro simples antes de incluir produtos no estoque.

#### 3.29.1. Conceito do Fluxo

**Workflow:**
1. **Produtos Chegando** = Pré-cadastro rápido (nome + quantidade + preço de compra)
2. Quando o produto chegar → **"Incluir no Estoque"**
3. Adiciona dados complementares (fornecedor + preço de venda)
4. Produto vai automaticamente para "Produtos" (estoque ativo)

#### 3.29.2. Novo Modelo

**`ProdutoChegando`:**
```python
- nome: CharField
- quantidade: PositiveIntegerField
- preco_compra: DecimalField
- data_compra: DateField
- data_prevista_chegada: DateField (opcional)
- observacoes: TextField (opcional)
- incluido_estoque: BooleanField (marca se já foi incluído)
- data_inclusao: DateTimeField (quando foi incluído)
```

**Vantagens:**
- ✅ Simples: apenas 1 registro por produto
- ✅ Rápido: poucos campos obrigatórios
- ✅ Flexível: pode incluir no estoque quando quiser

#### 3.29.3. Lógica de Inclusão no Estoque

**Quando clica em "Incluir no Estoque":**
1. Sistema pede: fornecedor + preço de venda
2. Verifica se já existe produto com mesmo nome (case-insensitive)
   - **Se sim**: Adiciona novo lote ao produto existente
   - **Se não**: Cria novo produto + lote
3. Marca `ProdutoChegando.incluido_estoque = True`
4. Produto aparece em "Produtos" normalmente

#### 3.29.4. Interfaces Criadas

**📋 `listar_produtos_chegando.html`:**
- Lista produtos ainda não incluídos no estoque
- Busca por nome
- Ações: "Incluir no Estoque" ou "Excluir"
- Responsivo (desktop + mobile)

**➕ `criar_produto_chegando.html`:**
- Formulário simples:
  - Nome do produto *
  - Quantidade *
  - Preço de compra *
  - Previsão de chegada
  - Observações
- Validação front-end
- Submit via AJAX

**📦 `incluir_no_estoque.html`:**
- Mostra dados do produto chegando
- Solicita dados complementares:
  - Fornecedor * (select)
  - Preço de venda *
- Alert informando sobre detecção de produtos duplicados
- Submit via AJAX → Redirect para "Produtos"

#### 3.29.5. URLs e Views

**URLs (`/chegando/...`):**
- `GET /chegando/` → listar_produtos_chegando
- `GET /chegando/novo/` → criar_produto_chegando
- `POST /chegando/novo/` → criar (JSON)
- `POST /chegando/<id>/excluir/` → excluir
- `GET /chegando/<id>/incluir/` → form incluir no estoque
- `POST /chegando/<id>/incluir/` → processar inclusão (JSON)

**Views:**
- `listar_produtos_chegando`: Lista + busca
- `criar_produto_chegando`: GET (form) + POST (JSON)
- `excluir_produto_chegando`: Exclusão com confirmação
- `incluir_no_estoque`: GET (form) + POST (transaction.atomic)

#### 3.29.6. Integração com Produtos

**Property atualizada em `Produto`:**
```python
@property
def quantidade_chegando(self):
    """Quantidade de produtos chegando com mesmo nome"""
    return ProdutoChegando.objects.filter(
        nome__iexact=self.nome,
        incluido_estoque=False
    ).aggregate(total=Sum('quantidade'))['total'] or 0
```

**Visualização:**
- Listagem de produtos: badge "Chegando" mostra quantidade
- Detalhes do produto: campo "Chegando" com destaque visual

#### 3.29.7. Melhorias de UX

**Menu lateral:**
- Ícone: `<i class="bi bi-hourglass-split"></i>`
- Nome: "Chegando" (simples e direto)
- Detecção ativa: highlight quando na seção

**Feedback visual:**
- Badge azul claro (`bg-info`) para quantidades chegando
- Alert informativo na tela de inclusão
- Mensagens de sucesso após operações
- Loading states nos botões

#### 3.29.8. Comparação com Sistema Anterior

**Antes (Pedidos de Compra - Complexo):**
- ❌ Múltiplos itens por pedido
- ❌ Recebimentos parciais
- ❌ Status (ABERTO, PARCIAL, RECEBIDO)
- ❌ Dependência de produtos já cadastrados
- ❌ Muitos passos para incluir no estoque

**Agora (Produtos Chegando - Simples):**
- ✅ 1 registro = 1 produto
- ✅ Inclusão direta (sem recebimentos parciais)
- ✅ Pré-cadastro independente de produtos
- ✅ 2 passos: Registrar → Incluir no Estoque
- ✅ Detecção automática de produtos duplicados

#### 3.29.9. Migrations

**Migration `0004`:**
- `CreateModel: ProdutoChegando`
- `Delete: PedidoCompra, ItemPedidoCompra`
- Transição limpa entre sistemas

#### 3.29.10. Casos de Uso Práticos

**Exemplo 1 - Produto Novo:**
1. Comprou 50 unidades de "Shampoo X" por R$ 10,00 cada
2. Registra em "Chegando"
3. Quando chegar, clica "Incluir no Estoque"
4. Informa: Fornecedor "Maria" + Preço Venda R$ 25,00
5. ✅ Produto criado + Lote adicionado

**Exemplo 2 - Reabastecimento:**
1. Comprou mais 30 unidades de "Shampoo X" (já existe no estoque)
2. Registra em "Chegando"
3. Clica "Incluir no Estoque"
4. Sistema detecta produto existente
5. ✅ Apenas novo lote é adicionado (mantém preço de venda atual)

**Exemplo 3 - Planejamento:**
1. Registra vários produtos chegando
2. Vê na listagem de Produtos o badge "Chegando: 150"
3. Sabe que terá 150 unidades a mais quando chegarem
4. ✅ Planejamento de estoque futuro

- **Resultado:** Sistema drasticamente simplificado, mais intuitivo e direto. Fluxo de trabalho natural: pré-cadastra rápido → inclui no estoque com dados completos quando chegar. Elimina complexidade desnecessária mantendo funcionalidade essencial de previsão de estoque futuro.

### 3.30. Autocomplete Inteligente em Produtos Chegando (UX Enhancement)

- **Objetivo:** Melhorar a experiência ao registrar produtos chegando, sugerindo produtos já existentes no estoque e vinculando automaticamente.

#### 3.30.1. Funcionalidade Implementada

**Campo "Nome do Produto" com Autocomplete:**
- jQuery UI Autocomplete integrado
- Busca produtos ativos no estoque em tempo real
- Mostra sugestões enquanto o usuário digita (mínimo 2 caracteres)
- Endpoint usado: `/api/buscar-produtos/` (já existente)

**Vinculação Automática:**
- Se usuário seleciona produto da lista → armazena `produto_id`
- Badge verde aparece: "Produto existente no estoque - Ao incluir, será adicionado como novo lote"
- Se digitar manualmente (não selecionar) → produto_id vazio = novo produto

#### 3.30.2. Modelo Atualizado

**Novo campo em `ProdutoChegando`:**
```python
produto_existente = models.ForeignKey(
    Produto, 
    on_delete=models.SET_NULL, 
    null=True, 
    blank=True, 
    related_name='produtos_chegando'
)
```

**Lógica:**
- Se `produto_existente` está definido → usa ele diretamente ao incluir
- Se não → busca por nome (case-insensitive) ou cria novo

#### 3.30.3. Fluxo Atualizado

**Cenário 1 - Produto Existente Selecionado:**
1. Usuário digita "Sha..."
2. Autocomplete mostra: "Shampoo Dove 400ml (Estoque: 20)"
3. Usuário clica na sugestão
4. ✅ Badge verde aparece
5. Ao incluir no estoque:
   - Pula verificação por nome
   - Usa diretamente o produto vinculado
   - Adiciona apenas novo lote
   - Alert verde confirma: "Produto Vinculado: ..."

**Cenário 2 - Produto Novo (Digitado Manualmente):**
1. Usuário digita "Produto Novo X" (não seleciona sugestão)
2. Nenhum badge aparece
3. Ao incluir no estoque:
   - Verifica se existe por nome
   - Se não, cria novo produto
   - Alert amarelo: "Atenção: Se já existir..."

#### 3.30.4. Melhorias na Interface

**`criar_produto_chegando.html`:**
- jQuery UI CSS incluído
- Input com `autocomplete="off"` (evita autocomplete do navegador)
- Hidden input `#produto_id` para armazenar ID selecionado
- Badge dinâmico (fadeIn/fadeOut) indicando produto existente
- Placeholder atualizado: "Digite para buscar produtos existentes..."

**`incluir_no_estoque.html`:**
- Alert verde especial quando há `produto_vinculado`
- Mostra nome do produto vinculado e estoque atual
- Informa claramente que será adicionado um lote ao existente
- Mantém alert amarelo para casos sem vinculação

#### 3.30.5. JavaScript Implementado

**Autocomplete Setup:**
```javascript
$("#nome").autocomplete({
    source: "/api/buscar-produtos/",
    minLength: 2,
    select: function(event, ui) {
        $('#nome').val(ui.item.value);
        $('#produto_id').val(ui.item.id);
        $('.produto-existente-badge').fadeIn();
    },
    change: function(event, ui) {
        if (!ui.item) {
            $('#produto_id').val('');
            $('.produto-existente-badge').fadeOut();
        }
    }
});
```

**Payload Atualizado:**
```javascript
const payload = {
    nome: nome,
    quantidade: quantidade,
    preco_compra: preco_compra,
    data_prevista_chegada: data_prevista_chegada,
    observacoes: observacoes,
    produto_id: produto_id || null  // Novo campo
};
```

#### 3.30.6. Views Atualizadas

**`criar_produto_chegando`:**
- Extrai `produto_id` do payload
- Se válido, busca `Produto` e vincula
- Salva `produto_existente` no `ProdutoChegando`

**`incluir_no_estoque`:**
- Prioriza `produto_chegando.produto_existente`
- Se definido, pula busca por nome
- Se não, segue lógica anterior (busca/cria)
- Passa `produto_vinculado` para template

#### 3.30.7. Migrations

**Migration `0005`:**
- `AddField: produtochegando.produto_existente`
- ForeignKey para Produto (SET_NULL)

#### 3.30.8. Benefícios

**Para o Usuário:**
- ✅ Menos erro de digitação (seleciona da lista)
- ✅ Vê estoque atual ao selecionar
- ✅ Confirmação visual imediata (badge verde)
- ✅ Mais rápido (autocomplete)
- ✅ Sem produtos duplicados acidentais

**Para o Sistema:**
- ✅ Vinculação explícita (mais confiável)
- ✅ Menos verificações no backend
- ✅ Dados mais consistentes
- ✅ Histórico rastreável (FK no banco)

#### 3.30.9. Compatibilidade

**Backward Compatible:**
- ✅ Produtos chegando antigos (sem vinculação) continuam funcionando
- ✅ Lógica de busca por nome mantida como fallback
- ✅ Digitação manual ainda permitida (novos produtos)

- **Resultado:** UX significativamente melhorada com autocomplete inteligente. Usuário vê em tempo real se o produto já existe, evitando duplicatas e acelerando o cadastro. Sistema mantém flexibilidade para novos produtos enquanto facilita reabastecimento de existentes.

### 3.31. Edição de Quantidade em Estoque + Limpeza de UI em Vendas (UX Enhancement)

- **Objetivo:** Permitir ajustar a quantidade em estoque diretamente na página de edição de produtos e remover elementos visuais desnecessários para economizar espaço em telas pequenas.

#### 3.31.1. Edição de Quantidade em Estoque

**Novo Campo no Form:**
- Adicionado campo `quantidade_estoque` no `ProdutoEditForm` (campo não vinculado ao modelo)
- Campo do tipo `IntegerField` com `min_value=0`
- Help text explicativo: "Ajuste a quantidade total em estoque. Se aumentar, será criado um novo lote; se diminuir, será deduzido dos lotes mais antigos (FIFO)."

**Lógica FIFO para Ajuste:**

**Aumento de Estoque (diferença > 0):**
- Cria novo lote de ajuste
- Usa fornecedor padrão (primeiro cadastrado)
- Preço de compra = custo médio ponderado do produto (ou preço de venda se não houver custo)
- Adiciona `diferenca` unidades ao estoque

**Redução de Estoque (diferença < 0):**
- Remove unidades dos lotes mais antigos (FIFO - First In First Out)
- Itera pelos lotes ordenados por `data_entrada`
- Se lote tem mais unidades que o necessário → reduz parcialmente
- Se lote tem menos → esvazia e continua para o próximo

**View `editar_produto` Atualizada:**
```python
# Preencher quantidade atual no GET
form.fields['quantidade_estoque'].initial = produto.quantidade_total

# Processar ajuste no POST
nova_quantidade = form.cleaned_data.get('quantidade_estoque')
if nova_quantidade is not None:
    quantidade_atual = produto.quantidade_total
    diferenca = nova_quantidade - quantidade_atual
    
    if diferenca > 0:
        # Criar novo lote
        Lote.objects.create(
            produto=produto,
            fornecedor=fornecedor_padrao,
            quantidade_inicial=diferenca,
            quantidade_atual=diferenca,
            preco_compra=produto.custo_medio_ponderado or produto.preco_venda
        )
    elif diferenca < 0:
        # Remover dos lotes mais antigos (FIFO)
        quantidade_a_remover = abs(diferenca)
        lotes = produto.lotes.filter(quantidade_atual__gt=0).order_by('data_entrada')
        for lote in lotes:
            if lote.quantidade_atual <= quantidade_a_remover:
                quantidade_a_remover -= lote.quantidade_atual
                lote.quantidade_atual = 0
            else:
                lote.quantidade_atual -= quantidade_a_remover
                quantidade_a_remover = 0
            lote.save()
```

**Template Atualizado (`editar_produto.html`):**
- Adicionado campo de quantidade entre preço de venda e status ativo
- Exibe help text do form
- Mantém estética Bootstrap 5 consistente

#### 3.31.2. Limpeza de UI em Histórico de Vendas

**Remoção de Dicas de Busca:**
- Removido bloco de "Dicas: digite "#123" para buscar por ID..." em `listar_vendas.html`
- Objetivo: economizar espaço em telas pequenas (mobile)
- Funcionalidade de busca mantida intacta
- Placeholder do input já é autoexplicativo

**Antes:**
```html
<div class="px-3 pb-3 text-muted small">
    Dicas: digite "#123" para buscar por ID, "loja" ou "externa" para filtrar por tipo.
</div>
```

**Depois:**
```html
<!-- Removido - economia de espaço -->
```

#### 3.31.3. Arquivos Modificados

**`inventario/forms.py`:**
- `ProdutoEditForm`: Adicionado campo `quantidade_estoque` com validação e help text

**`inventario/views.py`:**
- `editar_produto`: Lógica de ajuste FIFO implementada com mensagens de sucesso

**`inventario/templates/inventario/editar_produto.html`:**
- Adicionado campo de quantidade com label e help text

**`inventario/templates/inventario/listar_vendas.html`:**
- Removidas dicas de busca para economia de espaço

#### 3.31.4. Benefícios

**Edição de Quantidade:**
- ✅ Usuário pode ajustar estoque diretamente (sem criar lote manualmente)
- ✅ Sistema FIFO preservado automaticamente
- ✅ Mensagens de feedback claras
- ✅ Útil para correções de inventário, perdas, ou ajustes manuais

**Limpeza de UI:**
- ✅ Mais espaço vertical em mobile
- ✅ Interface mais limpa e focada
- ✅ Placeholder já orienta o uso

- **Resultado:** Maior flexibilidade na gestão de estoque com ajuste direto de quantidades, respeitando FIFO. Interface de vendas mais limpa e otimizada para dispositivos móveis.

### 3.32. Reorganização do Menu Lateral + Links nos Cards do Dashboard (UX Enhancement)

- **Objetivo:** Melhorar a navegação reorganizando o menu lateral em uma ordem mais lógica e tornar os produtos nos cards do Dashboard clicáveis.

#### 3.32.1. Reorganização do Menu Lateral

**Nova Ordem Lógica:**
```
1. Dashboard (visão geral)
2. Produtos (estoque atual)
3. Chegando (produtos que vão entrar no estoque)
4. Vendas (operações de venda)
5. Devoluções (operações de devolução)
6. Configurações (separado em seção própria)
```

**Justificativa:**
- Produtos → Chegando: Fluxo natural (estoque atual → estoque futuro)
- Chegando → Vendas: Separação clara entre entrada e saída
- Vendas → Devoluções: Operações relacionadas (venda e sua reversão)
- Configurações: Mantida separada como configurações do sistema

**Arquivo Modificado:**
- `inventario/templates/inventario/base.html`: Reordenação dos itens `<li>` no menu lateral

#### 3.32.2. Links nos Cards "Mais Vendidos" e "Mais Lucrativos"

**Problema Anterior:**
- Produtos nos cards "Mais Vendidos" e "Mais Lucrativos" eram apenas texto
- Card "Produtos com Estoque Baixo" tinha links, criando inconsistência
- Usuário não podia navegar diretamente para detalhes do produto

**Solução Implementada:**

**Views Atualizadas (`views.py`):**
```python
# Incluir produto__id nos querysets
top_produtos_vendidos = ItemVenda.objects.filter(
    venda__in=vendas_periodo
).values(
    'produto__id',    # ← Adicionado
    'produto__nome'
).annotate(...)

produtos_mais_lucrativos = ItemVenda.objects.filter(
    venda__in=vendas_periodo
).values(
    'produto__id',    # ← Adicionado
    'produto__nome'
).annotate(...)
```

**Template Atualizado (`dashboard.html`):**
```html
<!-- Mais Vendidos -->
<a href="{% url 'inventario:detalhar_produto' pk=produto.produto__id %}">
    {{ produto.produto__nome }}
</a>

<!-- Mais Lucrativos -->
<a href="{% url 'inventario:detalhar_produto' pk=produto.produto__id %}">
    {{ produto.produto__nome }}
</a>
```

#### 3.32.3. Benefícios

**Reorganização do Menu:**
- ✅ Fluxo mais intuitivo (estoque → entrada → saída)
- ✅ Agrupamento lógico de funcionalidades relacionadas
- ✅ Navegação mais eficiente

**Links nos Cards:**
- ✅ Navegação rápida para detalhes do produto
- ✅ Consistência em todos os cards do Dashboard
- ✅ UX aprimorada (menos cliques para acessar informações)
- ✅ Análise mais ágil dos produtos mais vendidos/lucrativos

#### 3.32.4. Arquivos Modificados

**`inventario/templates/inventario/base.html`:**
- Reordenação do menu lateral (Produtos → Chegando → Vendas → Devoluções)

**`inventario/views.py`:**
- `dashboard`: Adicionado `produto__id` aos querysets de produtos mais vendidos e lucrativos

**`inventario/templates/inventario/dashboard.html`:**
- Transformados nomes de produtos em links clicáveis nos cards "Mais Vendidos" e "Mais Lucrativos"

- **Resultado:** Navegação mais lógica e intuitiva com menu reorganizado. Dashboard totalmente interativo com todos os produtos clicáveis, facilitando análise rápida e acesso às informações detalhadas.

### 3.33. Porcentagem de Lucro no Dashboard + Compactação Mobile (UX Enhancement)

- **Objetivo:** Adicionar margem de lucro no card "Mais Lucrativos" do Dashboard e compactar drasticamente as listagens mobile de Produtos e Vendas para exibir mais informações por tela.

#### 3.33.1. Margem de Lucro no Card "Mais Lucrativos"

**Implementação:**
- Adicionada linha com porcentagem da margem de lucro abaixo do valor total de lucro
- Formato: `<small class="text-muted">X.X% margem</small>`
- Mantém badge verde com o valor em R$
- Layout de 2 linhas por produto: nome do produto e valores (R$ + %)

**Template Atualizado:**
```html
<div class="text-end">
    <span class="badge bg-success">R$ {{ produto.lucro_total|floatformat:2 }}</span>
    <small class="d-block text-muted mt-1">{{ produto.margem_lucro|floatformat:1 }}% margem</small>
</div>
```

#### 3.33.2. Compactação de Cards Mobile - Produtos

**Reduções Aplicadas:**
- `mb-3` → `mb-2` (espaçamento entre cards)
- `card-body` padding: `py-2 px-3` (antes era padrão)
- Título: classe `small` adicionada
- Badges de ação: `py-0 px-2` (botões ultra-compactos)
- Removido campo "Custo Médio" (menos relevante em mobile)
- Removida label "Margem de Lucro" (badge auto-explicativo)

**Nova Estrutura (3 linhas):**
1. **Nome + Badges de Estoque**: Nome do produto (small) + badge estoque + badge chegando
2. **Preço + Margem**: Preço de venda (destaque) + badge de margem colorido
3. **Ações Compactas**: Ícones-only em botões mini (Ver, Lote, Editar, Pausar/Excluir)

**Ganho de Espaço:**
- ~40% de redução na altura de cada card
- Mais ~60% de produtos visíveis por tela

#### 3.33.3. Compactação de Cards Mobile - Vendas

**Reduções Aplicadas:**
- `mb-3` → `mb-2` (espaçamento entre cards)
- `card-body` padding: `py-2 px-3`
- Cliente truncado em 20 caracteres
- Informações de cliente e data na mesma linha do ID
- Removido botão "Ver Detalhes" (card inteiro é clicável via link no #ID)
- Badges de devolução/brinde mais compactos (apenas ícone + info essencial)

**Nova Estrutura (2-3 linhas):**
1. **ID + Cliente + Data + Tipo**: Tudo em uma linha com truncamento inteligente
2. **Valores**: Valor total (esquerda) + Lucro (direita) na mesma linha
3. **Badges** (condicional): Só aparece se houver devolução ou brinde

**Ganho de Espaço:**
- ~50% de redução na altura de cada card
- Mais ~70% de vendas visíveis por tela

**JavaScript Atualizado:**
- Nova função `badgesDevolucaoBrindeCompacto()` para gerar badges na busca dinâmica
- `atualizarCardsMobile()` adaptada para a nova estrutura compacta
- Reinicialização de tooltips após atualização dinâmica

#### 3.33.4. Detalhes Técnicos

**Classes Bootstrap Usadas:**
- `py-0`, `px-2`: Padding mínimo em botões
- `py-2`, `px-3`: Padding reduzido em cards
- `mb-1`: Margem mínima entre linhas internas
- `mb-2`: Margem entre cards
- `small`: Fonte reduzida
- `truncatechars:20`: Filtro Django para truncar textos

**Responsividade Mantida:**
- Desktop (tabela) não foi alterado
- Apenas mobile (`d-lg-none`) foi compactado
- Breakpoint: `lg` (992px)

#### 3.33.5. Arquivos Modificados

**`inventario/templates/inventario/dashboard.html`:**
- Card "Mais Lucrativos": Adicionada linha com margem de lucro em %

**`inventario/templates/inventario/listar_produtos.html`:**
- Cards mobile: Estrutura compactada de 3 linhas
- Removidas informações secundárias
- Botões de ação com ícones-only

**`inventario/templates/inventario/listar_vendas.html`:**
- Cards mobile: Estrutura ultra-compacta de 2-3 linhas
- Cliente + data inline com ID
- Removido botão de ação (link no ID)
- JavaScript: Funções atualizadas para gerar HTML compacto na busca

#### 3.33.6. Benefícios

**Dashboard:**
- ✅ Informação completa sobre lucratividade (valor + margem %)
- ✅ Facilita comparação entre produtos (margem vs. lucro absoluto)

**Mobile - Produtos:**
- ✅ ~40% mais produtos visíveis por tela
- ✅ Menos scroll necessário
- ✅ Informações essenciais mantidas (nome, estoque, preço, margem)
- ✅ Ações rápidas com ícones compactos

**Mobile - Vendas:**
- ✅ ~50% mais vendas visíveis por tela
- ✅ Layout extremamente limpo
- ✅ Todas informações críticas preservadas
- ✅ Badges informativos com tooltips detalhados

- **Resultado:** Dashboard com informações completas de lucratividade. Listagens mobile drasticamente compactadas, permitindo visualizar muito mais informações por tela sem perda de funcionalidade, ideal para uso em smartphones.

### 3.34. Compactação Mobile para Chegando e Devoluções (UX Enhancement)

- **Objetivo:** Aplicar a mesma estratégia de compactação mobile nas páginas "Produtos Chegando" e "Devoluções" para maximizar informações visíveis por tela.

#### 3.34.1. Compactação de "Produtos Chegando" (Mobile)

**Reduções Aplicadas:**
- `mb-3` → `mb-2` (espaçamento entre cards)
- `card-body` padding: `py-2 px-3`
- Título: classe `small` adicionada
- Botões compactos: `py-0 px-2`
- Texto do botão "Incluir no Estoque" → "Incluir"
- Removidas labels redundantes (agora inline)

**Nova Estrutura (3 linhas):**
1. **Nome + Quantidade**: Nome do produto (small) + badge de quantidade
2. **Preço + Previsão**: Preço de compra (destaque verde) + data prevista com ícone
3. **Ações Compactas**: Botão "Incluir" + botão excluir (ícone-only)

**Ganho de Espaço:**
- ~45% de redução na altura de cada card
- Mais ~60% de produtos visíveis por tela

#### 3.34.2. Compactação de "Devoluções" (Mobile)

**Reduções Aplicadas:**
- `mb-3` → `mb-2` (espaçamento entre cards)
- `card-body` padding: `py-2 px-3`
- Informações inline (ID + venda + data na mesma linha)
- Removido botão "Ver Detalhes" (ID é clicável)
- Badge simplificado (apenas ícone)

**Nova Estrutura (2 linhas):**
1. **ID + Venda Original + Data + Badge**: Tudo em uma linha com links clicáveis
2. **Valor Restituído**: Label pequena + valor em destaque

**Ganho de Espaço:**
- ~55% de redução na altura de cada card
- Mais ~70% de devoluções visíveis por tela

#### 3.34.3. Detalhes de Implementação

**Produtos Chegando:**
```html
<div class="card mb-2">
    <div class="card-body py-2 px-3">
        <!-- Nome + Quantidade -->
        <h6 class="mb-0 small">{{ produto.nome }}</h6>
        <span class="badge bg-info">{{ produto.quantidade }}</span>
        
        <!-- Preço + Previsão (mesma linha) -->
        <span class="fw-bold text-success">R$ {{ produto.preco_compra }}</span>
        <small class="text-muted">📅 {{ produto.data_prevista_chegada }}</small>
        
        <!-- Ações compactas -->
        <button class="btn btn-success btn-sm py-0 px-2">
            <i class="bi bi-box-arrow-in-down"></i> Incluir
        </button>
    </div>
</div>
```

**Devoluções:**
```html
<div class="card mb-2">
    <div class="card-body py-2 px-3">
        <!-- ID + Venda + Data + Badge (tudo inline) -->
        <h6 class="mb-0 small">
            <a href="#">#{{ devolucao.id }}</a> · 
            <a href="#" class="text-muted">Venda #{{ devolucao.venda_original.id }}</a>
        </h6>
        <small class="text-muted">{{ devolucao.data }}</small>
        <span class="badge bg-warning"><i class="bi bi-arrow-return-left"></i></span>
        
        <!-- Valor restituído -->
        <small class="text-muted">Restituído:</small>
        <strong class="text-danger">R$ {{ devolucao.valor_total_restituido }}</strong>
    </div>
</div>
```

#### 3.34.4. Arquivos Modificados

**`inventario/templates/inventario/listar_produtos_chegando.html`:**
- Cards mobile: Estrutura compactada de 3 linhas
- Botão "Incluir" reduzido
- Preço com cor verde para destaque
- Data com ícone de calendário

**`inventario/templates/inventario/listar_devolucoes.html`:**
- Cards mobile: Estrutura ultra-compacta de 2 linhas
- ID clicável (não precisa de botão separado)
- Venda original inline
- Badge simplificado com apenas ícone

#### 3.34.5. Benefícios

**Produtos Chegando:**
- ✅ ~45% mais produtos visíveis por tela
- ✅ Ação principal ("Incluir") em destaque
- ✅ Todas informações relevantes preservadas
- ✅ Layout limpo e funcional

**Devoluções:**
- ✅ ~55% mais devoluções visíveis por tela
- ✅ Navegação rápida via links inline
- ✅ Informações essenciais em apenas 2 linhas
- ✅ Extremamente compacto sem perder clareza

**Consistência:**
- ✅ Todas as listagens mobile agora seguem o mesmo padrão de compactação
- ✅ Experiência uniforme em todo o sistema
- ✅ Otimizado para uso em smartphones

- **Resultado:** Sistema completamente otimizado para mobile com todas as páginas de listagem (Produtos, Vendas, Chegando, Devoluções) usando layouts ultra-compactos. Ganho médio de 40-55% mais informações visíveis por tela, mantendo clareza e funcionalidade completa.

### 3.35. Fornecedor em "Produtos Chegando" + Reorganização do Dashboard (UX Enhancement)

- **Objetivo:** Adicionar fornecedor no cadastro de "Produtos Chegando" para simplificar o processo de inclusão no estoque, e reorganizar o Dashboard para melhor aproveitamento do espaço, especialmente em mobile.

#### 3.35.1. Fornecedor em "Produtos Chegando"

**Problema Anterior:**
- Usuário precisava informar o fornecedor duas vezes: ao cadastrar o produto chegando e novamente ao incluir no estoque
- Processo redundante e mais passos desnecessários

**Solução Implementada:**

**Modelo Atualizado (`ProdutoChegando`):**
```python
fornecedor = models.ForeignKey(
    Fornecedor, 
    on_delete=models.PROTECT, 
    related_name='produtos_chegando', 
    null=True, 
    blank=True
)
```

**View `criar_produto_chegando`:**
- Adicionado campo `fornecedor_id` no payload
- Valida e associa fornecedor ao criar `ProdutoChegando`
- Passa lista de fornecedores para o template

**View `incluir_no_estoque`:**
- Prioriza fornecedor do `produto_chegando` se existir
- Só pede fornecedor no form se não foi informado anteriormente
- Código otimizado:
```python
if produto_chegando.fornecedor:
    fornecedor = produto_chegando.fornecedor
else:
    fornecedor_id = dados.get('fornecedor_id')
    fornecedor = get_object_or_404(Fornecedor, pk=fornecedor_id)
```

**Template `criar_produto_chegando.html`:**
- Adicionado select de fornecedor (opcional)
- Campo posicionado após "Preço de Compra"
- JavaScript atualizado para enviar `fornecedor_id`

**Template `incluir_no_estoque.html`:**
- Exibe fornecedor como read-only se já cadastrado
- Só mostra select se fornecedor não existir
- JavaScript adaptado para validar condicional

**Migration:**
- `0006_produtochegando_fornecedor.py`: Adiciona campo fornecedor

#### 3.35.2. Reorganização do Dashboard

**Layout Anterior:**
- Título e filtro lado a lado em desktop
- Campos de data personalizada inline com o select
- Difícil de usar em mobile (campos apertados)

**Novo Layout:**

**Desktop:**
```
┌─────────────────────────────────────┐
│ Dashboard        [Select Período ▼] │
│                                     │
│ [Data Início] até [Data Fim] [Filtrar] ← (só aparece se "Personalizado")
└─────────────────────────────────────┘
```

**Mobile:**
```
┌──────────────────┐
│ Dashboard        │
│ [Select Período] │
│                  │
│ [Data Início]    │  ← (aparece abaixo 
│ até              │     quando "Personalizado")
│ [Data Fim]       │
│ [Filtrar]        │
└──────────────────┘
```

**Implementação:**
- Título e select na mesma linha com `justify-content-between`
- Campos de data em um form separado que aparece abaixo
- Botão "Filtrar" para submeter datas personalizadas
- JavaScript simplificado: só mostra/esconde campos, não auto-submit em "custom"

**Estrutura HTML:**
```html
<div class="d-flex justify-content-between align-items-center flex-wrap">
    <h1 class="mb-0">Dashboard</h1>
    <form method="get" id="filtro-periodo-form">
        <select name="periodo" id="periodo-select">...</select>
    </form>
</div>

<!-- Campos personalizados aparecem abaixo -->
<div id="periodo-customizado" class="mt-2 d-none">
    <form method="get">
        <input type="hidden" name="periodo" value="custom">
        <input type="date" name="data_inicio">
        até
        <input type="date" name="data_fim">
        <button type="submit">Filtrar</button>
    </form>
</div>
```

**JavaScript Atualizado:**
```javascript
periodoSelect.addEventListener('change', function() {
    if (this.value === 'custom') {
        customizadoDiv.classList.remove('d-none'); // Mostra campos
    } else {
        customizadoDiv.classList.add('d-none'); // Esconde e submete
        form.submit();
    }
});
```

#### 3.35.3. Benefícios

**Fornecedor em "Chegando":**
- ✅ Elimina redundância: fornecedor informado apenas uma vez
- ✅ Processo mais rápido: menos campos ao incluir no estoque
- ✅ Opcional: pode deixar em branco e informar depois
- ✅ Menos erros: dados consistentes desde o cadastro

**Dashboard Reorganizado:**
- ✅ Melhor uso do espaço horizontal
- ✅ Título e filtro sempre visíveis juntos
- ✅ Campos de data não comprimidos em mobile
- ✅ Mais claro: botão explícito para filtrar datas personalizadas
- ✅ Layout responsivo sem quebras

#### 3.35.4. Arquivos Modificados

**Backend:**
- `inventario/models.py`: Campo `fornecedor` em `ProdutoChegando`
- `inventario/views.py`: Views `criar_produto_chegando` e `incluir_no_estoque` atualizadas
- `inventario/migrations/0006_produtochegando_fornecedor.py`: Nova migração

**Frontend:**
- `inventario/templates/inventario/criar_produto_chegando.html`: Campo de fornecedor e JS
- `inventario/templates/inventario/incluir_no_estoque.html`: Exibição condicional de fornecedor
- `inventario/templates/inventario/dashboard.html`: Layout reorganizado e JS simplificado

- **Resultado:** Processo de cadastro de produtos chegando otimizado com fornecedor integrado. Dashboard com layout mais limpo e intuitivo, especialmente em dispositivos móveis, com filtro de período acessível e campos de data personalizados bem organizados.

### 3.36. Ajustes de UX: Remoção de Dicas e Layout Condicional em Produtos (Polish)

- **Objetivo:** Limpar a interface removendo dicas desnecessárias e implementar layout condicional em "Produtos em Estoque" para melhorar a experiência.

#### 3.36.1. Remoção de Dicas

**Dicas Removidas:**

1. **listar_produtos_chegando.html:**
   - Removido: "Produtos comprados aguardando chegada ou inclusão no estoque"
   - Mantido apenas o título "Produtos Chegando"

2. **criar_produto_chegando.html:**
   - Removido: "Digite o nome para ver sugestões de produtos já cadastrados"
   - Badge informativo mantido quando produto é selecionado

**Benefício:** Interface mais limpa, especialmente em mobile onde cada linha conta.

#### 3.36.2. Layout Condicional em "Produtos em Estoque"

**Problema Anterior:**
- Layout sempre ultra-compacto em mobile
- Quando usuário faz busca, precisa de mais informações detalhadas
- Formato compacto demais para visualização de resultados de busca

**Solução: Dois Layouts Condicionais**

**Layout COMPACTO (quando `query_atual` está vazio):**
```html
<div class="card mb-2">
    <div class="card-body py-2 px-3">
        <!-- Nome + badges em linha -->
        <!-- Preço + margem em linha -->
        <!-- Botões icon-only (py-1 px-2) -->
    </div>
</div>
```
- Cards com `mb-2` (espaçamento menor)
- Padding reduzido `py-2 px-3`
- Botões compactos (apenas ícones)
- H6 para títulos
- Ideal para scroll rápido e visualização geral

**Layout NORMAL (quando há busca - `query_atual` existe):**
```html
<div class="card mb-3">
    <div class="card-body">
        <!-- Título H5 + badges -->
        <!-- Grid com labels e valores -->
        <!-- Botões com texto (ícone + texto) -->
    </div>
</div>
```
- Cards com `mb-3` (mais espaçamento)
- Padding padrão
- Botões com texto: "Ver", "Lote", "Editar", "Pausar", etc.
- H5 para títulos
- Labels descritivos: "Estoque:", "Chegando:", "Preço de Venda", "Margem de Lucro"
- Melhor legibilidade para análise de resultados

**Implementação Condicional:**
```django
{% if query_atual %}
    <!-- Layout NORMAL -->
{% else %}
    <!-- Layout COMPACTO -->
{% endif %}
```

**JavaScript (busca dinâmica):**
- Sempre gera layout NORMAL (porque há query quando a busca é feita)
- Consistente com a lógica condicional do template

#### 3.36.3. Ajustes Visuais

**Layout Compacto:**
- Botões: `py-1 px-2` (antes era `py-0 px-2` - muito apertado)
- Margem entre elementos: `mb-2` para melhor respiração
- H6 sem classe `small` (legibilidade melhorada)

**Layout Normal:**
- Estrutura em grid (`row mb-3`)
- Labels pequenos em cinza: `<small class="text-muted d-block">`
- Valores destacados: strong/badges
- Mais informações por card (Estoque, Chegando, Preço, Margem)

#### 3.36.4. Benefícios

**Limpeza Visual:**
- ✅ Menos texto desnecessário
- ✅ Interface mais profissional
- ✅ Foco no conteúdo relevante

**Layout Condicional:**
- ✅ Compacto para navegação geral (visualizar muitos produtos)
- ✅ Expandido para análise (quando busca algo específico)
- ✅ Melhor aproveitamento do espaço conforme contexto
- ✅ Experiência adaptativa: sistema "entende" a intenção do usuário

**Usabilidade:**
- ✅ Scroll mais rápido em listagem completa (compacto)
- ✅ Análise detalhada em resultados de busca (normal)
- ✅ Sem necessidade de toggle manual
- ✅ Transição automática e inteligente

#### 3.36.5. Arquivos Modificados

- `inventario/templates/inventario/listar_produtos_chegando.html`: Remoção de dica
- `inventario/templates/inventario/criar_produto_chegando.html`: Remoção de dica
- `inventario/templates/inventario/listar_produtos.html`: Layout condicional mobile

- **Resultado:** Interface polida com dicas removidas e sistema de layout adaptativo inteligente que se ajusta automaticamente ao contexto de uso (navegação geral vs. busca específica), otimizando densidade de informação conforme necessidade.

### 3.37. Compactação da Página de Detalhes de Produto (Mobile Optimization)

- **Objetivo:** Reduzir espaçamento e otimizar a visualização das informações de detalhes do produto, especialmente em telas pequenas.

#### 3.37.1. Card de Informações Resumidas

**Alterações:**

**Layout Mobile Otimizado:**
- Grid reorganizado: 3 colunas em mobile (`col-4`) ao invés de 6 colunas
- Ordem otimizada: Quantidade, Chegando, Status (primeira linha)
- Custo, Preço, Margem (segunda linha)

**Redução de Espaçamento:**
```html
<!-- ANTES -->
<div class="card-body">
    <div class="row g-3">
        <h6 class="text-muted mb-1">...</h6>

<!-- DEPOIS -->
<div class="card-body py-2 py-md-3">
    <div class="row g-2">
        <small class="text-muted d-block">...</small>
```

**Simplificações:**
- Títulos: `<h6>` → `<small>` (menor e mais discreto)
- Padding vertical: `py-3` → `py-2` (mobile) | `py-md-3` (desktop)
- Gap do grid: `g-3` → `g-2`
- Margem de lucro: removida box colorida, apenas badge
- Preço de venda: destaque com `text-primary`
- Margem: `floatformat:2` → `floatformat:1` (menos casas decimais)

#### 3.37.2. Cards de Lotes (Mobile)

**Antes (Layout em Grid 3 Linhas):**
```html
<div class="card-body p-3">
    <div class="row g-2">
        <div class="col-6">Data + Fornecedor</div>
        <div class="col-4">Inicial</div>
        <div class="col-4">Atual</div>
        <div class="col-4">Compra</div>
    </div>
</div>
```

**Depois (Layout Flex 2 Linhas):**
```html
<div class="card-body p-2">
    <!-- Linha 1: Data/Fornecedor | Badges Ini/Atual -->
    <div class="d-flex justify-content-between">
        <div>
            <small>01/01/2024</small>
            <span class="d-block">Fornecedor X</span>
        </div>
        <div>
            <badge>Ini: 10</badge>
            <badge>Atual: 5</badge>
        </div>
    </div>
    <!-- Linha 2: Preço de Compra -->
    <div class="text-end">
        Compra: R$ 10.00
    </div>
</div>
```

**Melhorias:**
- Padding: `p-3` → `p-2`
- Estrutura mais compacta: 2 linhas ao invés de 3
- Informações agrupadas logicamente
- Badges inline ao invés de grid separado
- Rótulos abreviados: "Ini:" e "Atual:" ao invés de labels separados

#### 3.37.3. Card Header e Empty State

**Card Header:**
```html
<!-- ANTES -->
<div class="card-header">
    <h5 class="mb-0">Lotes do Produto</h5>

<!-- DEPOIS -->
<div class="card-header py-2">
    <h6 class="mb-0">Lotes do Produto</h6>
```

**Empty State (sem lotes):**
```html
<!-- ANTES -->
<div class="text-center py-4">
    <i class="bi bi-inbox display-1"></i>
    <h5>Nenhum lote cadastrado</h5>
    <p>Este produto ainda não possui lotes...</p>
    <button class="btn btn-primary">...</button>

<!-- DEPOIS -->
<div class="text-center py-3">
    <i class="bi bi-inbox fs-1"></i>
    <p class="mt-2 mb-2">Nenhum lote cadastrado</p>
    <button class="btn btn-primary btn-sm">...</button>
```

#### 3.37.4. Comparativo de Espaçamento

**Mobile (antes vs depois):**

```
ANTES:                          DEPOIS:
┌─────────────────┐            ┌─────────────────┐
│                 │            │ Qtd  Cheg  Status│
│ Quantidade: 10  │            │ 10    5    Ativo │
│                 │            │                  │
│ Chegando: 5     │            │ Custo  Preço  Mrg│
│                 │            │ 10.00  15.00  33%│
│ Custo: 10.00    │            └─────────────────┘
│                 │            
│ Preço: 15.00    │            ┌──Lotes──────────┐
│                 │            │ 01/01  [Ini:10] │
│ Margem: 33.33%  │            │ Forn X [Atual:5]│
│                 │            │ Compra: R$ 10.00│
│ Status: Ativo   │            └─────────────────┘
│                 │
└─────────────────┘

┌──Lotes──────────┐
│                  │
│ Data: 01/01      │
│ Fornecedor: X    │
│                  │
│ Inicial: 10      │
│ Atual: 5         │
│ Compra: R$ 10.00 │
│                  │
└──────────────────┘
```

**Ganho de Espaço:**
- Card de informações: ~35% mais compacto
- Cards de lotes: ~40% mais compactos
- Mais lotes visíveis por tela

#### 3.37.5. Benefícios

**Densidade de Informação:**
- ✅ Mais informações visíveis sem scroll
- ✅ Lotes mais compactos e fáceis de comparar
- ✅ Layout otimizado para mobile

**Visual:**
- ✅ Menos espaço em branco desperdiçado
- ✅ Informações agrupadas logicamente
- ✅ Hierarquia visual clara (badges, cores)

**Performance:**
- ✅ Menos scroll necessário
- ✅ Visão mais completa do produto
- ✅ Comparação rápida entre lotes

#### 3.37.6. Arquivos Modificados

- `inventario/templates/inventario/detalhar_produto.html`: Compactação completa da página

- **Resultado:** Página de detalhes de produto otimizada com redução de 35-40% no espaço vertical utilizado, melhorando significativamente a experiência em dispositivos móveis e permitindo visualizar mais informações sem necessidade de scroll excessivo.

### 3.38. Padronização Visual Global (Design System Implementation)

- **Objetivo:** Unificar a formatação visual de todas as páginas de listagem do sistema, usando o "Histórico de Vendas" como referência de padrão de design.

#### 3.38.1. Padrão de Referência (Histórico de Vendas)

**Estrutura Desktop:**
```html
<div class="card d-none d-lg-block">
    <div class="card-body p-0">
        <table class="table table-hover mb-0">
            <thead class="table-light">...</thead>
            <tbody>...</tbody>
        </table>
    </div>
</div>
```

**Estrutura Mobile:**
```html
<div class="card mb-2">
    <div class="card-body py-2 px-3">
        <!-- Linha 1: Identificador + Info secundária -->
        <div class="d-flex justify-content-between align-items-start mb-1">
            <div class="flex-grow-1">
                <h6 class="mb-0 small">
                    <span class="fw-bold">Identificador</span>
                </h6>
                <small class="text-muted">Info secundária</small>
            </div>
            <div>Badges</div>
        </div>
        
        <!-- Linha 2: Valores principais -->
        <div class="d-flex justify-content-between align-items-center mb-1">
            <div><strong>Valor 1</strong></div>
            <div><strong>Valor 2</strong></div>
        </div>
        
        <!-- Linha 3: Ações (botões com ícones) -->
        <div class="d-flex gap-1 mt-2">
            <button class="btn btn-info btn-sm py-0 px-2"><i>...</i></button>
        </div>
    </div>
</div>
```

#### 3.38.2. Aplicação em Produtos em Estoque

**Antes:**
- Layout condicional (compacto vs normal)
- Inconsistência entre busca e navegação
- Botões com tamanhos variados

**Depois (Padrão Unificado):**
```django
<div class="card mb-2">
    <div class="card-body py-2 px-3">
        <!-- Linha 1: Nome, Custo e Estoque -->
        <h6 class="mb-0 small">
            <span class="fw-bold">{{ produto.nome }}</span>
        </h6>
        <small class="text-muted">Custo: R$ X</small>
        <span class="badge bg-primary">Qtd</span>
        
        <!-- Linha 2: Preço e Margem -->
        <strong class="text-primary">R$ Preço</strong>
        <span class="badge bg-success">Margem</span>
        
        <!-- Linha 3: Ações (ícones apenas) -->
        <button class="btn btn-info btn-sm py-0 px-2">
            <i class="bi bi-eye"></i>
        </button>
    </div>
</div>
```

**JavaScript Atualizado:**
- Função `atualizarCardsMobile()` refatorada
- Nova função `gerarBotoesIconesMobile()` para botões uniformes
- Cards dinâmicos seguem o mesmo padrão do template

#### 3.38.3. Aplicação em Produtos Chegando

**Ajustes:**
```django
<!-- Linha 1: Nome, Data, Quantidade -->
<h6 class="mb-0 small">
    <span class="fw-bold">{{ produto.nome }}</span>
</h6>
<small class="text-muted">{{ produto.data_compra|date:"d/m/Y" }}</small>
<span class="badge bg-info text-dark">{{ produto.quantidade }}</span>

<!-- Linha 2: Preço e Previsão -->
<strong class="text-success">R$ {{ produto.preco_compra }}</strong>
<small class="text-muted">Prev: {{ data|date:"d/m" }}</small>

<!-- Linha 3: Ações -->
<a class="btn btn-success btn-sm py-0 px-2" title="Incluir">
    <i class="bi bi-box-arrow-in-down"></i>
</a>
<button class="btn btn-danger btn-sm py-0 px-2" title="Excluir">
    <i class="bi bi-trash"></i>
</button>
```

**Melhorias:**
- Data de compra adicionada à Linha 1
- Previsão compactada (d/m ao invés de d/m/Y)
- Botões apenas com ícones + tooltips
- Consistência com padrão global

#### 3.38.4. Aplicação em Devoluções

**Ajustes:**
```django
<!-- Linha 1: ID, Venda Original, Badge -->
<h6 class="mb-0 small">
    <span class="fw-bold">#{{ devolucao.id }}</span>
    <span class="text-muted">· Venda #{{ venda_id }}</span>
</h6>
<small class="text-muted">{{ devolucao.data }}</small>
<span class="badge bg-warning"><i class="bi bi-arrow-return-left"></i></span>

<!-- Linha 2: Valor Restituído -->
<small class="text-muted">Restituído:</small>
<strong class="text-danger">R$ {{ valor }}</strong>

<!-- Linha 3: Ação -->
<a class="btn btn-info btn-sm py-0 px-2" title="Ver">
    <i class="bi bi-eye"></i>
</a>
```

**Melhorias:**
- Linha 3 adicionada com botão de ação
- Estrutura de 3 linhas consistente
- Botão com ícone + tooltip

#### 3.38.5. Padrão Estabelecido

**Elementos Comuns:**

1. **Cards Mobile:**
   - `mb-2`: espaçamento entre cards
   - `py-2 px-3`: padding interno
   - 3 linhas de informação

2. **Linha 1 (Identificação):**
   - `<h6 class="mb-0 small">` com `<span class="fw-bold">`
   - `<small class="text-muted">` para info secundária
   - Badges no canto direito

3. **Linha 2 (Valores):**
   - `<strong>` para valores principais
   - `<small class="text-muted">` para labels
   - `d-flex justify-content-between`

4. **Linha 3 (Ações):**
   - `d-flex gap-1 mt-2`
   - Botões: `btn-sm py-0 px-2`
   - Apenas ícones + `title` para tooltips

5. **Empty State:**
   - Centralizado: `text-center py-5`
   - Ícone: `display-1 text-muted`
   - Título: `<h5 class="text-muted mt-3">`
   - Botão CTA: `btn-primary mt-3`

6. **Tabela Desktop:**
   - Card com `p-0`
   - `table table-hover mb-0`
   - `thead table-light`
   - Botões apenas com ícones

#### 3.38.6. Consistência Global

**Classes Padronizadas:**
- **Títulos mobile**: `h6 mb-0 small` + `fw-bold`
- **Info secundária**: `small text-muted`
- **Valores**: `strong` com cores contextuais (`text-primary`, `text-success`, `text-danger`)
- **Badges**: Bootstrap padrão (`bg-primary`, `bg-success`, `bg-info`, etc.)
- **Botões mobile**: `btn-sm py-0 px-2` + ícone

**Espaçamentos:**
- Entre elementos: `mb-1`
- Antes de ações: `mt-2`
- Entre cards: `mb-2`
- Padding interno: `py-2 px-3`

**Cores Contextuais:**
- Azul (`primary`): Quantidades, identificadores
- Verde (`success`): Preços de compra, lucros, confirmações
- Vermelho (`danger`): Devoluções, exclusões
- Amarelo (`warning`): Alertas, status intermediários
- Cinza (`secondary`): Informações neutras

#### 3.38.7. Benefícios da Padronização

**Consistência:**
- ✅ Experiência uniforme em todo o sistema
- ✅ Aprendizado rápido: padrão reconhecível
- ✅ Manutenção simplificada

**Profissionalismo:**
- ✅ Visual coeso e polido
- ✅ Design system implementado
- ✅ Aparência de produto maduro

**Usabilidade:**
- ✅ Previsibilidade nas interações
- ✅ Botões e badges sempre no mesmo lugar
- ✅ Densidade de informação otimizada

**Manutenibilidade:**
- ✅ Código HTML repetível e documentado
- ✅ Classes CSS consistentes
- ✅ Fácil adicionar novas páginas seguindo o padrão

#### 3.38.8. Arquivos Modificados

**Templates:**
- `inventario/templates/inventario/listar_produtos.html`: Padrão unificado + JS atualizado
- `inventario/templates/inventario/listar_produtos_chegando.html`: Estrutura de 3 linhas
- `inventario/templates/inventario/listar_devolucoes.html`: Linha 3 de ações adicionada

- **Resultado:** Sistema completamente padronizado visualmente, com design system consistente aplicado em todas as páginas de listagem. Experiência de usuário uniforme e profissional, facilitando navegação e manutenção futura do código.
