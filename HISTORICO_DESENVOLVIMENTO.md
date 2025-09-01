# Histórico de Desenvolvimento - Sistema de Controle de Estoque

Este documento serve como um registro das principais decisões, funcionalidades implementadas, modificações e correções de bugs realizadas durante o desenvolvimento do projeto.

---

## 1. Setup Inicial e Estrutura

- **Projeto:** Django
- **Nome do Projeto Principal:** `estoque_project`
- **Nome do App Principal:** `inventario`
- **Ambiente:** Projeto configurado para rodar em um ambiente virtual Python (`venv`).
- **Dependências Iniciais:** `django`, `pillow`.

---

## 2. Funcionalidades Implementadas (Fluxo Inicial)

- **CRUD de Produtos:** Implementação completa das funcionalidades de Criar, Ler (Listar e Detalhar), Atualizar e Excluir produtos.
- **CRUD de Fornecedores:** Implementação completa do CRUD para fornecedores.
- **Entrada de Estoque:** Funcionalidade para adicionar `Lotes` a um produto existente a partir da página de detalhes do produto.
- **Sistema de Vendas (FIFO):**
    - Página de "Nova Venda" com busca de produtos e adição dinâmica de itens.
    - Lógica de backend para dar baixa no estoque seguindo o método "Primeiro que Entra, Primeiro que Sai" (FIFO).
    - Cálculo do custo da venda baseado nos preços de compra dos lotes.
    - Histórico e página de detalhes para vendas concluídas.
- **Dashboard Dinâmico:**
    - Exibição de métricas de negócio (Valor do Estoque, Vendas no período, Lucro).
    - Tabela de produtos com estoque baixo.
    - Gráfico de Receita vs. Custo (Chart.js) com dados dos últimos 30 dias.
- **Configurações:** Página para gerenciar configurações globais do sistema, como o nome da empresa e o limite de estoque baixo.

---

## 3. Modificações e Correções de Bugs

Esta seção detalha as alterações feitas com base no feedback e nos testes durante o desenvolvimento.

### 3.1. Otimização do Cadastro de Produtos (Solicitado pelo Usuário)

- **Problema:** O fluxo original exigia a criação de um produto e, posteriormente, a adição de um lote em uma tela separada, o que era pouco prático.
- **Solução:** Unificamos o processo. A página "Adicionar Novo Produto" foi transformada em "Adicionar Novo Produto e Lote Inicial".
    - O `ProdutoForm` foi modificado para incluir os campos do lote (`fornecedor`, `quantidade_inicial`, `preco_compra`, `preco_venda`).
    - A view `criar_produto` foi reescrita para, dentro de uma transação, criar o `Produto` e, em seguida, o seu primeiro `Lote` com os dados fornecidos.
    - O template `produto_form.html` foi ajustado para exibir os novos campos de forma organizada.

### 3.2. Correção da Página de "Nova Venda" em Branco

- **Problema:** Acessar a URL `/vendas/nova/` resultava em uma página completamente em branco.
- **Causa:** O arquivo de template `nova_venda.html` foi criado, mas seu conteúdo não foi salvo, resultando em um arquivo vazio.
- **Solução:** O conteúdo completo do template, incluindo o HTML e o JavaScript necessário para a funcionalidade da página, foi reescrito no arquivo `nova_venda.html`.

### 3.3. Correção da Busca de Produtos na Página de Vendas

- **Problema:** A busca de produtos na página de vendas não retornava nenhum item, mesmo havendo produtos com estoque.
- **Causa:** A consulta ao banco de dados na view `buscar_produtos_json` era ineficiente e falhava em alguns cenários.
- **Solução:** A query foi completamente reescrita usando `annotate` e `Subquery` do Django para ser mais robusta e eficiente, garantindo que todos os produtos com estoque (`quantidade_total > 0`) e preço de venda definido sejam retornados.

### 3.4. Correção do Erro ao Adicionar Item à Venda

- **Problema:** Após corrigir a busca, o produto era encontrado, mas ao selecioná-lo, ele não era adicionado à tabela de "Itens da Venda".
- **Causa:** O JavaScript na página `nova_venda.html` recebia o preço do produto como uma `string` e falhava silenciosamente ao tentar usá-lo em cálculos, o que impedia a criação da linha na tabela.
- **Solução:** O JavaScript foi ajustado para converter o preço recebido para um número (`parseFloat`) antes de realizar qualquer operação, garantindo a manipulação correta dos dados.

### 3.5. Correção do Erro `NOT NULL constraint failed` ao Finalizar a Venda

- **Problema:** Ao clicar em "Finalizar Venda", um erro de banco de dados (`NOT NULL constraint failed: inventario_itemvenda.custo_compra_total_registrado`) era gerado.
- **Causa:** A view `criar_venda` estava salvando o `ItemVenda` no banco de dados *antes* de calcular o custo FIFO. Como o campo de custo é obrigatório, o banco de dados rejeitava a operação.
- **Solução:** A lógica foi invertida. A view agora primeiro executa toda a baixa de estoque e calcula o `custo_compra_total_registrado`. Apenas com todos os dados em mãos, ela cria e salva o `ItemVenda` uma única vez.

### 3.6. Correção do Erro `TypeError: Decimal is not JSON serializable` no Dashboard

- **Problema:** A página do Dashboard quebrava com um erro de `TypeError`.
- **Causa:** Os valores monetários (do tipo `Decimal`) calculados para o gráfico não podiam ser convertidos para o formato JSON pela biblioteca padrão do Python.
- **Solução:** Na view `dashboard`, ao converter os dados do gráfico para JSON, foi utilizado o `DjangoJSONEncoder`, uma classe especial do Django que sabe como lidar com tipos de dados do banco de dados, como `Decimal`.

### 3.7. Atalho para Adicionar Lote na Lista de Produtos (Solicitado pelo Usuário)

- **Sugestão:** O fluxo para adicionar um novo lote a um produto existente exigia entrar primeiro na página de detalhes do produto.
- **Solução:** Para agilizar o processo de entrada de estoque, um botão de atalho "Adicionar Lote" foi adicionado diretamente na linha de cada produto na página principal de listagem (`listar_produtos.html`), levando o usuário diretamente ao formulário de adição de lote.

### 3.8. Refatoração do Cadastro de Fornecedores (Solicitado pelo Usuário)

- **Problema:** O gerenciamento de fornecedores era um processo separado, com suas próprias telas de CRUD, o que tornava o fluxo de cadastro de um novo produto com um novo fornecedor lento. Além disso, a tela de cadastro de produto continha campos considerados desnecessários ("Descrição", "Imagem").
- **Solução:** O fluxo foi completamente redesenhado para ser mais ágil e focado na velocidade:
    1.  **Remoção do CRUD de Fornecedores:** Toda a seção dedicada ao gerenciamento de fornecedores (menu lateral, URLs, views e templates) foi removida.
    2.  **Cadastro Rápido Integrado:** Na página "Adicionar Novo Produto", foi adicionado um campo de texto "Ou Cadastre um Novo Fornecedor". Isso permite ao usuário escolher um fornecedor da lista ou digitar o nome de um novo, que será criado automaticamente.
    3.  **Simplificação do Formulário de Produto:** Os campos "Descrição" e "Imagem" foram removidos do formulário e do modelo de dados para criar uma tela de cadastro mais limpa e direta.
    4.  **Validação:** Foi adicionada uma lógica para garantir que o usuário ou selecione um fornecedor existente ou digite o nome de um novo, mas não ambos.

### 3.9. Redesign da Página de Detalhes do Produto (Solicitado pelo Usuário)

- **Problema:** A página de detalhes do produto mostrava uma imagem grande (campo que foi removido do cadastro) e a disposição das informações não era otimizada.
- **Solução:** A página foi redesenhada para focar nas informações mais importantes e usar melhor o espaço:
    1.  **Remoção da Imagem:** A seção da imagem do produto foi completamente removida.
    2.  **Compactação das Informações:** As informações gerais (Quantidade, Preço de Venda, Status) foram movidas para cards de destaque no topo da página, oferecendo uma visão rápida e clara dos dados mais relevantes.
    3.  **Foco nos Lotes:** A tabela de lotes agora é o elemento principal da página, ocupando o espaço central.

### 3.10. Melhoria de Usabilidade na Página de Vendas (Solicitado pelo Usuário)

- **Problema:** Ao adicionar um produto na página de vendas, não havia indicação da quantidade disponível em estoque, e era possível tentar vender uma quantidade maior do que a existente.
- **Solução:** Foram implementadas melhorias no backend e no frontend para fornecer essa informação e validação em tempo real:
    1.  **API Enriquecida:** A view `buscar_produtos_json` foi atualizada para incluir a quantidade total em estoque (`estoque`) na sua resposta JSON.
    2.  **Exibição do Estoque:** O JavaScript da página de vendas agora exibe a quantidade disponível abaixo do nome do produto assim que ele é adicionado à lista de itens.
    3.  **Limite de Quantidade:** O campo de quantidade (`<input type="number">`) agora possui o atributo `max` definido com o valor do estoque disponível, impedindo que o usuário aumente a quantidade além do limite pelos botões do campo.
    4.  **Validação Adicional:** Uma validação extra via JavaScript foi adicionada para alertar o usuário e corrigir o valor caso ele digite manualmente um número maior que o estoque.

### 3.11. Refatoração do Preço de Venda e Edição de Produto (Solicitado pelo Usuário)

- **Problema:** O preço de venda era definido por lote, o que era inflexível. A página de edição de produto era a mesma da criação, exigindo o preenchimento de campos de lote que não faziam sentido no contexto de edição.
- **Solução:** Uma grande refatoração foi realizada para centralizar o preço de venda no produto e simplificar a edição:
    1.  **Mudança no Modelo de Dados:** O campo `preco_venda` foi movido do modelo `Lote` para o modelo `Produto`. O banco de dados foi atualizado através de uma nova migração.
    2.  **Formulário de Edição Simplificado:** Foi criado um novo `ProdutoEditForm` contendo apenas os campos `nome`, `preco_venda` e `ativo`, e a view `editar_produto` foi atualizada para usá-lo. Foi criado também um novo template `editar_produto.html` para este formulário.
    3.  **Ajuste no Fluxo de Criação:** A lógica de criação de produto e adição de lote foi atualizada em todos os formulários, views e templates para refletir que o preço de venda agora pertence ao produto e não é mais solicitado na entrada de lote.
    4.  **Consistência Geral:** Todas as partes do sistema que liam o preço de venda (Dashboard, API de busca, página de detalhes, etc.) foram atualizadas para buscar a informação do modelo `Produto`.

### 3.12. Correção da Seleção do Menu Lateral Ativo (UI Fix)

- **Problema:** A marcação de item ativo no menu lateral estava fixa no "Dashboard", independentemente da página que o usuário estivesse visitando.
- **Solução:** A lógica de seleção foi corrigida no template `base.html`. Agora, a classe CSS `active` é aplicada dinamicamente a cada link do menu usando a tag `{% if %}` do Django. O sistema verifica o nome da rota da URL atual (`request.resolver_match.url_name`) e aplica a classe ao link correspondente, garantindo que o menu sempre reflita a página atual do usuário. 

### 3.13. Implementação de Regra de Negócio de Divisão de Lucro (Solicitado pelo Usuário)

- **Problema:** O sistema calculava apenas o lucro bruto total, mas o cenário de negócio real exigia a diferenciação do lucro pessoal do usuário com base no local da venda (loja vs. externa).
- **Solução:** Uma nova lógica de negócio foi implementada em todo o sistema:
    1.  **Modelo de Dados:** O modelo `Venda` foi atualizado com um campo `tipo_venda` ('LOJA' ou 'EXTERNA') e um campo `desconto`. Propriedades inteligentes (`@property`) foram adicionadas para calcular `valor_bruto`, `valor_total` (pós-desconto), `custo_total`, `lucro_bruto` e, o mais importante, `meu_lucro`, que aplica a regra de divisão de 50% automaticamente se `tipo_venda` for 'LOJA'.
    2.  **Página de Venda:** A interface de "Registrar Nova Venda" foi atualizada para incluir um seletor de tipo de venda e um campo para aplicar descontos em valor (R$). O JavaScript foi ajustado para calcular o total final em tempo real.
    3.  **Lógica de Backend:** A view `criar_venda` agora salva o tipo de venda e o desconto no banco de dados.
    4.  **Dashboard Refatorado:** A view do Dashboard foi completamente ajustada para usar a nova propriedade `meu_lucro`. Agora, o card principal de lucro e o gráfico refletem apenas a parcela de lucro do usuário, de acordo com a regra de negócio.
    5.  **Atualização da Interface:** As páginas de listagem e detalhes de venda foram atualizadas para exibir o tipo de venda, o desconto aplicado e o valor do lucro pessoal em cada transação. 

### 3.14. Implementação de Alertas Visuais para Margem de Lucro

- **Problema:** Não havia uma forma rápida de identificar produtos com margem de lucro abaixo do esperado.
- **Solução:**
    1.  **Configuração Central:** Foi adicionado um campo "Margem de Lucro Ideal (%)" na página de Configurações, permitindo ao usuário definir sua própria meta.
    2.  **Destaques Visuais:** Na lista de produtos, a margem de cada item agora é exibida em um "badge" colorido: verde para margens que atingem ou superam a meta e vermelho para as que estão abaixo. Na página de detalhes do produto, o card da margem de lucro recebe uma borda da cor correspondente, criando um alerta visual imediato.

### 3.15. Reformulação Completa do Dashboard

- **Problema:** O Dashboard exibia estatísticas de um período fixo (30 dias) e apresentava os dados de forma limitada.
- **Solução:** O Dashboard foi completamente reconstruído para ser uma ferramenta de análise interativa e rica em informações:
    1.  **Filtro de Período Dinâmico:** Foi implementado um formulário que permite ao usuário visualizar as estatísticas dos últimos 7 dias, 30 dias, último ano, ou selecionar um intervalo de datas personalizado. Todos os cards e o gráfico de linhas se atualizam de acordo com o período selecionado.
    2.  **Novos Cards de Métricas:** Os cards foram reorganizados para dar destaque às métricas mais importantes do período selecionado: Receita Total, Seu Lucro e Número de Vendas. O card de Valor em Estoque (que não depende do período) foi mantido.
    3.  **Gráfico de Linhas Inteligente:** O gráfico de Receita vs. Lucro agora se adapta ao período. Para intervalos curtos (até 90 dias), ele mostra a evolução diária. Para intervalos longos, ele agrupa os dados por mês, mantendo a visualização sempre clara e relevante.
    4.  **Novo Gráfico de Atividade (Heatmap):** Inspirado no GitHub, foi adicionado um novo gráfico de "heatmap" que exibe a atividade de lucro do último ano. Cada dia do ano é representado por um quadrado, e a cor do quadrado fica mais escura conforme o lucro daquele dia foi maior, permitindo identificar rapidamente os dias e períodos de maior rentabilidade. 