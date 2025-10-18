# 📦 Sistema de Gestão de Estoque

Sistema completo de gestão de estoque desenvolvido em Django com rastreamento FIFO, análise de tendências e previsão de reposição.

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

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

## 🚀 Deploy Grátis (100% Free Forever)

### Render.com + Neon.tech (Recomendado)

**Stack 100% gratuita permanente:**
- ✅ Hospedagem: Render.com (Free Tier)
- ✅ PostgreSQL: Neon.tech (0.5GB gratuito)
- ✅ PWA: Instalável como app no celular
- ✅ Sincronização automática entre dispositivos

1. **Criar banco PostgreSQL no Neon.tech**
   - Acesse [neon.tech](https://neon.tech)
   - Crie um novo projeto (sem cartão de crédito)
   - Copie a connection string PostgreSQL

2. **Deploy no Render.com**
   - Fork este repositório
   - Conecte no [Render](https://render.com)
   - Configure as variáveis de ambiente
   - Deploy automático via GitHub!

📖 **Guia passo a passo**: Veja [RENDER_NEON_DEPLOY.md](RENDER_NEON_DEPLOY.md)  
📱 **Instalar como app**: Veja [INSTALAR_PWA.md](INSTALAR_PWA.md)

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
- **Banco de Dados**: PostgreSQL (Neon.tech) / SQLite (dev)
- **Frontend**: Bootstrap 5, Chart.js
- **Deploy**: Render.com
- **Armazenamento**: Whitenoise (estáticos)
- **Rate Limiting**: django-ratelimit
- **PWA**: Service Worker + Manifest

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

## 💰 Custos (R$ 0,00 para sempre!)

### Neon.tech (PostgreSQL)
- **Plano Gratuito Permanente**: ✅ Sem expiração
  - 0.5 GB storage por projeto
  - 10 projetos gratuitos
  - Backups automáticos (7 dias)
  - Sem cartão de crédito necessário

### Render.com (Hospedagem)
- **Plano Gratuito Permanente**: ✅ Sem expiração
  - 750 horas/mês (suficiente para 1 app 24/7)
  - SSL automático (HTTPS)
  - Builds ilimitados
  - Deploy automático via GitHub

**Total**: R$ 0,00/mês agora e sempre! 🎉

⚠️ **Limitação:** Cold start após 15min de inatividade (~30s para acordar)

## 📱 PWA (Progressive Web App)

O sistema é um **PWA completo** instalável como app nativo:

### ✅ Recursos PWA
- **Instalável** em Android, iOS e Desktop
- **Ícone na tela inicial** (como apps nativos)
- **Abre em tela cheia** (sem barra do navegador)
- **Sincronização automática** entre todos os dispositivos
- **Atualizações automáticas** (sem precisar reinstalar)
- **Cache inteligente** de assets (Bootstrap, jQuery, Chart.js)
- **Página offline** com reconexão automática

### 📱 Como Instalar

**Android (Chrome):**
1. Acesse o app no navegador
2. Toque em "Adicionar à tela inicial"
3. Pronto! Ícone aparece na tela inicial

**iOS (Safari):**
1. Toque no botão compartilhar (⬆️)
2. Selecione "Adicionar à Tela de Início"
3. Pronto!

📖 **Guia completo de instalação**: [INSTALAR_PWA.md](INSTALAR_PWA.md)

### 🔄 Sincronização Entre Dispositivos

Todos os dispositivos acessam o **mesmo banco PostgreSQL**:
- Venda no celular → **aparece no computador instantaneamente**
- Atualiza estoque no tablet → **todos veem a mudança**
- Backup automático na nuvem

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

