# 📱 Como Instalar o Stoke como App no Celular

O **Stoke** é um PWA (Progressive Web App), o que significa que você pode instalá-lo no seu celular como se fosse um aplicativo nativo, sem precisar de lojas de apps!

---

## 🌟 Vantagens do PWA

- ✅ **Ícone na tela inicial** (como apps nativos)
- ✅ **Abre em tela cheia** (sem barra do navegador)
- ✅ **Funciona offline** (shell do app)
- ✅ **Sincronização em tempo real** entre dispositivos
- ✅ **Atualizações automáticas** (sem downloads)
- ✅ **Ocupa pouco espaço** (~5MB vs 50MB+ de apps nativos)
- ✅ **Sem precisar de Google Play ou App Store**

---

## 📱 Instalação no Android

### Chrome/Edge (recomendado)

1. **Abra o Chrome** no seu Android
2. **Acesse** seu app: `https://stoke.onrender.com` (ou seu domínio)
3. **Aguarde** 1-2 segundos na página inicial
4. **Um banner aparecerá** na parte inferior: "Adicionar Stoke à tela inicial"
   - Se não aparecer, vá para o método alternativo abaixo

**✅ Pronto! O app está instalado na tela inicial.**

---

### Método Alternativo (Android)

Se o banner não aparecer automaticamente:

1. Abra o Chrome e acesse: `https://stoke.onrender.com`
2. Toque nos **3 pontinhos** (⋮) no canto superior direito
3. Selecione **"Adicionar à tela inicial"** ou **"Instalar app"**
4. Uma janela aparecerá com o ícone e nome do app
5. Toque em **"Adicionar"** ou **"Instalar"**
6. O ícone do **Stoke** aparecerá na sua tela inicial

**🎉 Instalado! Agora abra o app pela tela inicial.**

---

### Verificar se instalou corretamente

1. Vá na **tela inicial** do Android
2. Procure o ícone **"Stoke"** (ícone azul/escuro)
3. Toque no ícone
4. O app deve abrir **em tela cheia** (sem barra de endereço)

---

## 🍎 Instalação no iOS/iPadOS

### Safari (obrigatório no iOS)

⚠️ **Importante:** No iOS, PWAs só funcionam no Safari (não funciona no Chrome iOS).

1. **Abra o Safari** no seu iPhone/iPad
2. **Acesse** seu app: `https://stoke.onrender.com`
3. Toque no **botão de compartilhar** (ícone com seta para cima ⬆️)
   - Fica na barra inferior (iPhone) ou superior (iPad)
4. Role para baixo e selecione **"Adicionar à Tela de Início"**
5. Edite o nome se quiser (ex: "Stoke")
6. Toque em **"Adicionar"** no canto superior direito

**✅ Pronto! O app está instalado na tela inicial.**

---

### Verificar se instalou corretamente (iOS)

1. Vá na **tela inicial** do iPhone/iPad
2. Procure o ícone **"Stoke"**
3. Toque no ícone
4. O app deve abrir **em tela cheia** (sem barra do Safari)

---

## 💻 Instalação no Desktop

### Chrome/Edge (Windows, Mac, Linux)

1. Abra o Chrome/Edge no computador
2. Acesse: `https://stoke.onrender.com`
3. Procure o **ícone de instalação** (⊕) na barra de endereço
4. Clique nele e selecione **"Instalar"**

**Ou:**

1. Clique nos **3 pontinhos** (⋮) no canto superior direito
2. Vá em **"Instalar Stoke..."** ou **"Criar atalho..."**
3. Marque **"Abrir como janela"**
4. Clique em **"Instalar"**

O app será adicionado:
- **Windows:** Menu Iniciar e área de trabalho
- **Mac:** Pasta de Aplicativos e Dock
- **Linux:** Menu de aplicativos

---

## 🔄 Como Funciona a Sincronização

### Entre Dispositivos

Todos os dispositivos acessam o **mesmo banco de dados** na nuvem:

```
Celular → https://stoke.onrender.com ← Computador
           ↓
    PostgreSQL (Neon.tech)
```

**O que acontece:**
1. Você faz uma venda no **celular**
2. Os dados são salvos instantaneamente no **PostgreSQL** na nuvem
3. Ao abrir o app no **computador**, você vê a venda imediatamente

**⚠️ Requer internet para sincronizar.**

---

### Offline vs Online

| Recurso | Offline | Online |
|---------|---------|--------|
| **Abrir o app** | ✅ Sim | ✅ Sim |
| **Ver interface** | ✅ Sim (shell) | ✅ Sim |
| **Criar vendas** | ❌ Não | ✅ Sim |
| **Ver produtos** | ❌ Não | ✅ Sim |
| **Análises** | ❌ Não | ✅ Sim |

**💡 Por que não funciona 100% offline?**
- Para **garantir sincronização** entre dispositivos
- Evitar **conflitos de dados**
- Manter **backup automático** na nuvem

---

## 🎯 Testando a Sincronização

### Teste Prático

1. **Instale o app** no celular e no computador
2. **Faça login** em ambos (se tiver autenticação)
3. No **celular:**
   - Abra o app
   - Adicione um novo produto (ex: "Teste Sync")
4. No **computador:**
   - Recarregue a página (F5)
   - O produto "Teste Sync" deve aparecer!

**🎉 Se aparecer, a sincronização está funcionando!**

---

## 🔧 Atualizar o App

### Atualizações Automáticas

O PWA atualiza automaticamente quando você:
1. Fecha e reabre o app
2. Recarrega a página (arrastar para baixo no mobile)
3. Fica inativo por alguns minutos

**Não precisa reinstalar ou baixar atualizações manualmente!**

---

### Forçar Atualização Manual

Se algo estiver com problema:

**Android/iOS:**
1. Abra o app instalado
2. **Arraste de cima para baixo** para recarregar
3. Ou feche completamente o app e reabra

**Desktop:**
1. Abra o app
2. Pressione **Ctrl + R** (Windows/Linux) ou **Cmd + R** (Mac)

---

## ❌ Desinstalar o App

### Android

1. **Pressione e segure** o ícone do Stoke na tela inicial
2. Arraste para **"Desinstalar"** ou toque em **"Remover"**
3. Confirme

**Ou:**
1. Vá em **Configurações** → **Apps**
2. Procure por **"Stoke"**
3. Toque em **"Desinstalar"**

---

### iOS

1. **Pressione e segure** o ícone do Stoke
2. Toque em **"Remover App"**
3. Selecione **"Excluir do iPhone"**

---

### Desktop

**Chrome (Windows):**
1. Abra o app
2. Clique nos **3 pontinhos** (⋮)
3. Selecione **"Desinstalar Stoke..."**

**Mac:**
1. Vá na pasta **Aplicativos**
2. Arraste o ícone do Stoke para a **Lixeira**

---

## 🐛 Problemas Comuns

### ❌ "Adicionar à tela inicial" não aparece

**Causas possíveis:**
1. Você já instalou o app antes
2. O site não está em HTTPS
3. O manifest.json não está configurado corretamente

**Solução:**
- Verifique se o URL é `https://` (não `http://`)
- Limpe o cache do navegador
- Tente novamente após alguns minutos

---

### ❌ App não abre em tela cheia

**Causa:** O app não foi instalado corretamente.

**Solução:**
1. Desinstale o app (veja seção acima)
2. Limpe o cache do navegador
3. Reinstale usando o método correto

---

### ❌ Dados não sincronizam

**Causas possíveis:**
1. Sem conexão com a internet
2. App está usando cache antigo

**Solução:**
1. Verifique sua conexão Wi-Fi/dados móveis
2. Recarregue o app (arrastar para baixo)
3. Se persistir, feche e reabra o app

---

### ❌ Ícone não aparece corretamente

**Causa:** O navegador não baixou os ícones ainda.

**Solução:**
1. Desinstale o app
2. Limpe o cache: Chrome → Configurações → Privacidade → Limpar dados
3. Acesse o site novamente e aguarde 10 segundos
4. Reinstale

---

## 🎨 Personalizar Ícone

Os ícones estão em:
- `estoque_project/static/icons/icon-192.png` (192x192px)
- `estoque_project/static/icons/icon-512.png` (512x512px)

Para mudar:
1. Substitua esses arquivos PNG
2. Faça commit e push para o GitHub
3. O Render fará deploy automático
4. Desinstale e reinstale o app no celular

---

## ✅ Checklist de Instalação

- [ ] App instalado no celular
- [ ] Ícone aparece na tela inicial
- [ ] App abre em tela cheia (sem barra do navegador)
- [ ] Consigo criar/visualizar dados
- [ ] Testei sincronização entre 2 dispositivos
- [ ] Verifiquei que funciona offline (mostra página "sem conexão")

---

## 💡 Dicas Extras

### Para Melhor Experiência

1. **Use sempre o app instalado** (não o navegador)
2. **Mantenha internet ativa** para sincronização
3. **Recarregue ocasionalmente** para pegar atualizações
4. **Não desinstale** se só quiser atualizar (atualiza automaticamente)

### Recursos Offline

O que funciona sem internet:
- ✅ Abrir o app (shell)
- ✅ Ver página "offline"
- ❌ Criar/editar dados
- ❌ Ver produtos/vendas

### Comparação: PWA vs App Nativo

| Característica | PWA (Stoke) | App Nativo |
|----------------|-------------|------------|
| **Instalação** | Direto do navegador | Loja de apps |
| **Tamanho** | ~5MB | 50-200MB |
| **Atualizações** | Automáticas | Manual |
| **Multiplataforma** | Android + iOS + Desktop | Apenas 1 plataforma |
| **Desenvolvimento** | 1 código | 3 códigos (Android/iOS/Web) |

---

## 📞 Precisa de Ajuda?

Se tiver problemas com a instalação:
1. Verifique se o app está em **HTTPS** (cadeado no navegador)
2. Limpe o cache do navegador
3. Tente em outro navegador (Chrome recomendado no Android)
4. Consulte a documentação do navegador

---

**🎉 Aproveite seu app Stoke instalado! Agora você tem acesso rápido e sincronização entre todos os seus dispositivos!**

