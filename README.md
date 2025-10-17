# 📦 Sistema de Gestão de Estoque

Sistema completo de gestão de estoque desenvolvido em Django com rastreamento FIFO, análise de tendências e previsão de reposição.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/seu-usuario/seu-repo)

## ✨ Funcionalidades

### 📊 Dashboard Analítico
- Estatísticas em tempo real (estoque, vendas, lucro)
- Gráficos de receita e lucro por período
- Heatmap de lucros dos últimos 365 dias
- Top 5 produtos mais vendidos e lucrativos
- Alertas de estoque baixo e produtos parados

### 📦 Gestão de Produtos
- CRUD completo de produtos
- Upload de imagens
- Vinculação com fornecedores
- Controle de produtos ativos/pausados
- Múltiplos lotes por produto (FIFO)
- Rastreamento completo de lotes utilizados em vendas

### 💰 Vendas
- Registro de vendas (loja física / externas)
- Suporte a brindes
- Descontos
- Cálculo automático de custos e lucros
- Visualização transparente dos lotes FIFO utilizados
- Busca em tempo real de produtos

### 🔄 Devoluções
- Registro de devoluções totais ou parciais
- Retorno automático aos lotes FIFO originais
- Rastreamento de itens devolvidos ao estoque
- Histórico completo de devoluções

### 📈 Análise de Tendências
- Previsão de demanda baseada em histórico
- Cálculo automático de ponto de reposição
- Sugestões de compra com custos estimados
- Detecção de sazonalidade
- Médias móveis (7, 14 e 30 dias)
- Análise de dias de cobertura de estoque

### 🚚 Produtos Chegando
- Pré-cadastro de produtos comprados
- Controle de data prevista de chegada
- Inclusão facilitada no estoque
- Vinculação automática com produtos existentes

### ⚙️ Configurações
- Gestão de fornecedores
- Configuração de limites de estoque
- Margem de lucro ideal
- Período de análise de tendências
- Upload de logo da empresa

## 🚀 Deploy Rápido

### Vercel + Supabase (Recomendado)

1. **Criar projeto no Supabase**
   - Acesse [supabase.com](https://supabase.com)
   - Crie um novo projeto (plano gratuito)
   - Copie a string de conexão do banco (Transaction Mode)

2. **Deploy no Vercel**
   - Fork este repositório
   - Importe no [Vercel](https://vercel.com)
   - Configure as variáveis de ambiente (veja `ENV_SETUP.md`)
   - Deploy automático!

📖 **Guia completo**: Veja [DEPLOY.md](DEPLOY.md)

## 💻 Desenvolvimento Local

### Requisitos
- Python 3.11+
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente (Windows)
venv\Scripts\activate

# Ative o ambiente (Linux/Mac)
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
# Copie ENV_SETUP.md e crie seu .env

# Execute migrações
cd estoque_project
python manage.py migrate

# Crie superusuário
python manage.py createsuperuser

# Execute o servidor
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## 🏗️ Tecnologias

- **Backend**: Django 5.2.4
- **Banco de Dados**: PostgreSQL (Supabase) / SQLite (dev)
- **Frontend**: Bootstrap 5, Chart.js
- **Deploy**: Vercel
- **Armazenamento**: Whitenoise (estáticos)
- **Rate Limiting**: django-ratelimit

## 📂 Estrutura do Projeto

```
estoque_project/
├── inventario/              # App principal
│   ├── models.py           # Modelos (Produto, Venda, Lote, etc)
│   ├── views.py            # Views e lógica de negócio
│   ├── forms.py            # Formulários
│   ├── urls.py             # Rotas
│   ├── middleware.py       # Rate limiting
│   └── templates/          # Templates HTML
├── estoque_project/        # Configurações Django
│   ├── settings.py         # Configurações
│   ├── urls.py             # URLs principais
│   └── wsgi.py             # WSGI
└── manage.py               # CLI Django
```

## 🔒 Segurança

- Rate limiting em APIs de busca
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection
- Secure cookies em produção
- SSL redirect automático

## 💡 Recursos Técnicos

### FIFO Transparente
- Rastreamento completo de lotes utilizados em cada venda
- Devoluções inteligentes aos lotes originais
- Visualização clara dos custos por lote

### Performance
- Queries otimizadas com `select_related` e `prefetch_related`
- Paginação em todas as listagens
- Cache de cálculos complexos
- Índices no banco de dados

### Análise Preditiva
- Cálculo automático de ponto de reposição
- Estoque de segurança baseado em volatilidade
- Previsão de demanda com médias móveis
- Detecção de sazonalidade por dia da semana

## 💰 Custos

### Supabase (Banco de Dados)
- **Plano Gratuito**: ✅ Suficiente para pequenas empresas
  - 500 MB banco de dados
  - 1 GB armazenamento
  - Múltiplos projetos permitidos

### Vercel (Hospedagem)
- **Plano Gratuito**: ✅ Suficiente para uso normal
  - 100 GB de transferência/mês
  - Builds ilimitados
  - SSL automático

**Total**: R$ 0,00/mês para começar! 🎉

## 📱 PWA Ready

O sistema está preparado para funcionar como PWA (Progressive Web App):
- Instalável em dispositivos móveis
- Funciona offline (parcialmente)
- Ícones e manifest configurados

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é de código aberto para fins educacionais.

## 👨‍💻 Autor

Desenvolvido com ❤️ para ajudar pequenas empresas a gerenciar seu estoque de forma eficiente.

## 🐛 Suporte

Encontrou um bug? Tem uma sugestão? Abra uma [issue](https://github.com/seu-usuario/seu-repo/issues)!

---

⭐ Se este projeto foi útil, considere dar uma estrela!

