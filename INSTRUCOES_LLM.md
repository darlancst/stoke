## Instruções para a LLM: Criação de Sistema de Controle de Estoque com Implantação no PythonAnywhere

**Objetivo:** Desenvolver um sistema de controle de estoque completo e moderno em Django e prepará-lo para implantação na plataforma PythonAnywhere. O sistema deve ser baseado na lógica de um projeto existente, mas com um front-end totalmente novo, elegante e intuitivo. As principais características incluem controle de estoque no modelo FIFO (Primeiro que Entra, Primeiro que Sai) e a capacidade de registrar vendas com múltiplos produtos para um mesmo cliente.

### 1. Tecnologias e Estrutura do Projeto

- **Backend:** Python com Django
- **Frontend:** HTML, CSS, JavaScript, com o framework **Bootstrap 5** para o layout.
- **Banco de Dados:** SQLite (padrão do Django para desenvolvimento).
- **Estrutura de Arquivos:** Crie um projeto Django chamado `estoque_project` e um app principal chamado `inventario`.

```
estoque_project/
├── estoque_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventario/
│   ├── migrations/
│   ├── templates/
│   │   └── inventario/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
└── manage.py
```

### 2. Modelos de Dados (`inventario/models.py`)

Implemente os seguintes modelos. A estrutura de `Lote` é crucial para o controle FIFO, e a relação `Venda` -> `ItemVenda` é a base para vendas com múltiplos produtos.

<details>
<summary>Clique para ver o código dos Models</summary>

```python
# inventario/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum
import uuid
from decimal import Decimal

class Fornecedor(models.Model):
    nome = models.CharField('Nome', max_length=100)
    cnpj = models.CharField('CNPJ', max_length=20, blank=True)
    contato = models.CharField('Nome de Contato', max_length=100, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    endereco = models.TextField('Endereço', blank=True)
    data_criacao = models.DateTimeField('Data de Cadastro', auto_now_add=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    imagem = models.ImageField('Imagem', upload_to='produtos/', blank=True, null=True)
    ativo = models.BooleanField('Ativo', default=True)

    @property
    def quantidade_total(self):
        return self.lotes.aggregate(total=Sum('quantidade_atual'))['total'] or 0

    @property
    def preco_venda_atual(self):
        lote_mais_antigo = self.lotes.filter(quantidade_atual__gt=0).order_by('data_entrada').first()
        return lote_mais_antigo.preco_venda if lote_mais_antigo else None

    def __str__(self):
        return self.nome

class Lote(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='lotes')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade_inicial = models.PositiveIntegerField('Quantidade Inicial')
    quantidade_atual = models.PositiveIntegerField('Quantidade Atual')
    preco_compra = models.DecimalField('Preço de Compra', max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField('Preço de Venda', max_digits=10, decimal_places=2)
    data_entrada = models.DateTimeField('Data de Entrada', default=timezone.now)

    def __str__(self):
        return f"Lote de {self.produto.nome} ({self.quantidade_atual} un.)"

class Venda(models.Model):
    cliente_nome = models.CharField('Nome do Cliente', max_length=100)
    data = models.DateTimeField('Data da Venda', default=timezone.now)
    status = models.CharField('Status', max_length=20, default='Concluída')

    @property
    def valor_total(self):
        return self.itens.aggregate(total=Sum(models.F('quantidade') * models.F('preco_venda_unitario')))['total'] or Decimal('0')

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente_nome}"

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField('Quantidade')
    preco_venda_unitario = models.DecimalField('Preço de Venda (no ato)', max_digits=10, decimal_places=2)
    custo_compra_total_registrado = models.DecimalField('Custo de Compra Total (FIFO)', max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

class Configuracao(models.Model):
    nome_empresa = models.CharField(max_length=100, default='Minha Empresa')
    limite_estoque_baixo = models.PositiveIntegerField(default=10)
    logo = models.ImageField(upload_to='logo/', blank=True, null=True)

# Outros modelos como Promocao, NotaFiscal, Devolucao podem ser adicionados posteriormente
# para manter o foco inicial na lógica principal de estoque e venda.
```
</details>

### 3. Lógica de Negócio (`inventario/views.py`)

#### 3.1. CRUDs Padrão
Crie as views para o gerenciamento completo (Listar, Criar, Editar, Detalhar, Excluir) das seguintes entidades:
- `Produto`
- `Fornecedor`

#### 3.2. Entrada de Estoque (`adicionar_estoque`)
- Crie uma view onde o usuário seleciona um `Produto` e adiciona um novo `Lote`.
- O formulário deve pedir: `Fornecedor`, `Quantidade`, `Preço de Compra` e `Preço de Venda`.
- Ao submeter, um novo objeto `Lote` deve ser criado, com `quantidade_inicial` e `quantidade_atual` iguais à quantidade informada.

#### 3.3. **View de Nova Venda (Lógica Principal)**
Esta é a funcionalidade mais importante a ser criada.

**URL:** `vendas/nova/` -> `views.criar_venda_nova`

**Template (`nova_venda.html`):**
- A página deve ter um formulário para os dados gerais da venda (`cliente_nome`).
- Inclua um campo de busca de produtos com autocompletar (usando JavaScript e uma view de API auxiliar que retorna produtos em JSON).
- Abaixo, uma tabela vazia com o cabeçalho: "Produto", "Qtd.", "Preço Unit.", "Subtotal", "Ação".
- Quando um produto é selecionado na busca, o JavaScript deve:
    1.  Adicioná-lo como uma nova linha na tabela.
    2.  Incluir um campo `<input type="number">` para a quantidade.
    3.  Preencher o preço de venda automaticamente (baseado no `preco_venda_atual` do produto).
    4.  Calcular e exibir o subtotal (`quantidade * preço`).
    5.  Adicionar um botão "Remover" para a linha.
- Um campo de "Total da Venda" na parte inferior da página deve ser atualizado em tempo real.
- Ao submeter o formulário, o JavaScript deve coletar os dados de todos os itens da tabela (ID do produto e quantidade) e enviá-los junto com o formulário principal (por exemplo, dentro de um `<input type="hidden">` com valor em formato JSON).

**View (`criar_venda_nova`):**
- **GET:** Apenas renderiza a página com o formulário inicial.
- **POST:**
    1.  Use `@transaction.atomic` para garantir que a operação inteira seja segura.
    2.  Parse os dados do cliente e a lista de itens (JSON) do `request.POST`.
    3.  Crie e salve o objeto `Venda` principal com o nome do cliente.
    4.  **Inicie um loop para cada item da venda:**
        a. Recupere o objeto `Produto`. Verifique se a `quantidade_total` em estoque é suficiente. Se não for, retorne um erro.
        b. **Lógica FIFO para baixa de estoque:**
            i.   Obtenha todos os `Lote`s do produto com `quantidade_atual > 0`, ordenados por `data_entrada` (do mais antigo para o mais novo).
            ii.  Crie um `ItemVenda`, associando-o à `Venda` e ao `Produto`. Preencha o `preco_venda_unitario`.
            iii. Inicialize `custo_total_item = 0` e `quantidade_a_baixar = quantidade_do_item_na_venda`.
            iv.  **Itere sobre os lotes obtidos:**
                - Se `lote.quantidade_atual >= quantidade_a_baixar`:
                    - `custo_total_item += quantidade_a_baixar * lote.preco_compra`
                    - `lote.quantidade_atual -= quantidade_a_baixar`
                    - `lote.save()`
                    - `quantidade_a_baixar = 0`
                    - Saia do loop de lotes (break).
                - Se `lote.quantidade_atual < quantidade_a_baixar`:
                    - `custo_total_item += lote.quantidade_atual * lote.preco_compra`
                    - `quantidade_a_baixar -= lote.quantidade_atual`
                    - `lote.quantidade_atual = 0`
                    - `lote.save()`
        c.  Após o loop de lotes, salve o `custo_compra_total_registrado` no `ItemVenda`.
        d.  Salve o objeto `ItemVenda`.
    5.  Se o loop de itens terminar com sucesso, redirecione para a página de `detalhe_venda`. Se falhar, a transação será revertida.

### 4. Design e Front-end

- **Layout Base (`base.html`):** Crie um template base com uma barra de navegação lateral (sidebar) e uma área de conteúdo principal.
    - **Sidebar:** Links para Dashboard, Produtos, Vendas, Fornecedores e Configurações.
- **Dashboard:**
    - Use "Cards" do Bootstrap 5 para exibir estatísticas rápidas: Valor Total do Estoque, Número de Vendas (mês), Lucro (mês).
    - Use **Chart.js** para exibir um gráfico de "Receita vs. Custo" dos últimos 30 dias.
    - Inclua uma tabela com "Produtos com Estoque Baixo" (baseado no `limite_estoque_baixo` das `Configuracao`).
- **Tabelas:** Todas as listagens (produtos, vendas, etc.) devem ser em tabelas limpas do Bootstrap 5, com cabeçalhos claros e dados bem alinhados.
- **Formulários:** Use os componentes de formulário do Bootstrap 5 para um visual limpo e moderno. Os campos devem ter `labels` claras.

### 5. Passos de Desenvolvimento Local

1.  Execute `python manage.py makemigrations` e `python manage.py migrate`.
2.  Crie um superusuário com `python manage.py createsuperuser`.
3.  Registre os modelos no `admin.py`, usando `ItemVendaInline` no `VendaAdmin` para permitir a gestão de vendas também pelo painel de admin.
4.  Inicie o servidor com `python manage.py runserver` e teste o fluxo completo.

---

### 6. Instruções de Implantação no PythonAnywhere

Após desenvolver e testar o projeto localmente, siga estes passos para hospedá-lo.

#### 6.1. Preparação
1.  **Crie uma conta** no [PythonAnywhere](https://www.pythonanywhere.com/).
2.  **Faça o upload do projeto:** A maneira mais fácil é versionar seu projeto com Git, publicá-lo em um repositório (GitHub, GitLab) e clonar no PythonAnywhere.
    - Abra um **"Bash Console"** no PythonAnywhere.
    - Clone seu repositório: `git clone https://github.com/seu-usuario/seu-repositorio.git seu_projeto_online`

#### 6.2. Configure o Ambiente Virtual
1.  No mesmo console Bash, crie um ambiente virtual para o projeto. Escolha uma versão do Python compatível com seu Django (ex: Python 3.10).
    ```bash
    mkvirtualenv --python=python3.10 venv_online
    ```
2.  Ative o ambiente virtual (geralmente é ativado automaticamente, mas caso precise: `workon venv_online`).
3.  Navegue até a pasta do seu projeto e instale as dependências:
    ```bash
    cd ~/seu_projeto_online
    pip install -r requirements.txt
    ```
    *Observação: Certifique-se de que seu `requirements.txt` contém todas as bibliotecas necessárias, como Django, Pillow (para imagens), etc.*

#### 6.3. Configure o Web App
1.  Vá para a aba **"Web"** no painel do PythonAnywhere.
2.  Clique em **"Add a new web app"**.
3.  Selecione **"Manual configuration"** (não "Django").
4.  Escolha a versão do Python que você usou no ambiente virtual (ex: Python 3.10).

#### 6.4. Configurações no `settings.py`
Antes de prosseguir, edite o seu arquivo `settings.py` no PythonAnywhere (na aba "Files").
1.  Adicione seu domínio do PythonAnywhere a `ALLOWED_HOSTS`:
    ```python
    ALLOWED_HOSTS = ['seu-usuario.pythonanywhere.com']
    ```
2.  Configure o `STATIC_ROOT` para a coleta de arquivos estáticos:
    ```python
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    ```
3.  Defina `DEBUG = False`.

#### 6.5. Coleta de Arquivos Estáticos
1.  Volte ao seu console Bash com o ambiente virtual ativado.
2.  Execute o comando `collectstatic`:
    ```bash
    python manage.py collectstatic
    ```

#### 6.6. Configure o WSGI
1.  Na aba **"Web"**, vá até a seção **"Code"** e clique no link do arquivo **WSGI configuration file**.
2.  Substitua o conteúdo do arquivo para apontar para o seu projeto. O código deve ser semelhante a este:
    ```python
    import os
    import sys

    # Adicione o caminho do seu projeto ao Python path
    path = '/home/seu-usuario/seu_projeto_online'
    if path not in sys.path:
        sys.path.insert(0, path)

    # Adicione o caminho do projeto Django (a pasta que contém settings.py)
    path_django = '/home/seu-usuario/seu_projeto_online/estoque_project'
    if path_django not in sys.path:
        sys.path.insert(0, path_django)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'estoque_project.settings'

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    ```
    *Atenção: Substitua `seu-usuario` e `seu_projeto_online` pelos seus nomes corretos.*

#### 6.7. Mapeamento de Arquivos Estáticos e de Mídia
1.  Na aba **"Web"**, vá para a seção **"Static files"**.
2.  Configure o mapeamento para os arquivos estáticos:
    - **URL:** `/static/`
    - **Directory:** `/home/seu-usuario/seu_projeto_online/staticfiles`
3.  Se você usa uploads de imagens (`ImageField`), configure também os arquivos de mídia:
    - **URL:** `/media/`
    - **Directory:** `/home/seu-usuario/seu_projeto_online/media`
    *(Certifique-se de que a pasta `media` existe no seu projeto e que as variáveis `MEDIA_URL` e `MEDIA_ROOT` estão definidas no seu `settings.py`)*

#### 6.8. Finalização
1.  Na aba **"Web"**, clique no grande botão verde **"Reload seu-usuario.pythonanywhere.com"**.
2.  Acesse seu site e verifique se tudo está funcionando. Verifique os logs de erro ("Error log") se encontrar algum problema. 