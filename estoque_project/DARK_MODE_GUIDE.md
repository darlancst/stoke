# 🌙 Guia do Dark Mode - Sistema Stoke

## ✨ Recursos Implementados

### 1. **Toggle Visual no Header**
- Botão elegante com ícone de lua/sol
- Localizado no topo à direita, próximo ao menu hambúrguer
- Animação suave de hover e click

### 2. **Persistência de Preferência**
- Usa `localStorage` para salvar a escolha do usuário
- Mantém o tema mesmo após fechar o navegador
- Sincronizado com a preferência do sistema operacional

### 3. **Detecção Automática**
- Detecta automaticamente se o SO está em dark mode
- Se nenhuma preferência foi salva, usa a do sistema
- Atualiza automaticamente se o usuário mudar no SO

### 4. **Transições Suaves**
- Animações CSS de 0.3s para todas as mudanças
- Transição suave entre temas claro e escuro
- Botão toggle com animação de scale

### 5. **Atalho de Teclado**
- Pressione `Ctrl + Shift + D` para alternar rapidamente
- Funciona em qualquer página do sistema

### 6. **Zero Flash (FOUC Prevention)**
- Script inline no `<head>` aplica o tema ANTES do CSS carregar
- Navegação entre páginas mantém o tema sem piscar
- Experiência fluida e profissional

## 🎨 Paleta de Cores (GitHub-inspired)

### Dark Mode
- **Fundo Principal:** `#0d1117` (Azul muito escuro)
- **Fundo Secundário:** `#161b22` (Cards, sidebar)
- **Bordas:** `#30363d`
- **Texto Principal:** `#c9d1d9` (Cinza claro)
- **Texto Secundário:** `#8b949e` (Cinza médio)
- **Destaque:** `#58a6ff` (Azul)

### Light Mode
- Cores padrão do Bootstrap 5

## 🔧 Componentes Estilizados

✅ **Estrutura**
- Navbar
- Sidebar
- Main content area

✅ **Formulários**
- Inputs text
- Selects
- Textareas
- Placeholders
- Campos desabilitados

✅ **Tabelas**
- Headers
- Rows
- Hover effects
- Bordas

✅ **Cards**
- Background
- Headers
- Bordas

✅ **Alertas**
- Info (azul)
- Success (verde)
- Warning (amarelo/laranja)
- Danger (vermelho)

✅ **Badges**
- Todas as variantes do Bootstrap

✅ **Botões**
- Outline-secondary
- Hover states

✅ **Outros**
- Modals
- Dropdowns
- List groups
- Tooltips (via Bootstrap)
- jQuery UI Autocomplete
- Heatmap (Dashboard) com legend adaptativo
- Gráficos Chart.js com cores dinâmicas
- Input date picker
- Scrollbars customizadas
- Links dentro de cards/tabelas
- Tabelas striped

## 🚀 Como Usar

### Para o Usuário Final:

1. **Ativar Dark Mode:**
   - Clique no botão com ícone de lua no topo da página
   - OU pressione `Ctrl + Shift + D`

2. **Desativar Dark Mode:**
   - Clique novamente no botão (agora com ícone de sol)
   - OU pressione `Ctrl + Shift + D`

### Para Desenvolvedores:

#### Adicionar novos estilos para dark mode:

```css
/* No arquivo base.html ou em custom CSS */
[data-theme="dark"] .seu-elemento {
    background-color: #161b22;
    color: #c9d1d9;
    border-color: #30363d;
}
```

#### Acessar o tema atual via JavaScript:

```javascript
// Verificar tema atual
const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

// Obter cores para gráficos
const chartColors = window.getChartColors();
console.log(chartColors.gridColor);
console.log(chartColors.textColor);
```

#### Escutar mudanças de tema:

```javascript
// Observar mudanças no atributo data-theme
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.attributeName === 'data-theme') {
            const newTheme = mutation.target.getAttribute('data-theme');
            console.log('Tema mudou para:', newTheme);
            // Atualize seus componentes aqui
        }
    });
});

observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
});
```

## 📱 Compatibilidade

✅ **Navegadores:**
- Chrome/Edge (v90+)
- Firefox (v88+)
- Safari (v14+)
- Opera (v76+)

✅ **Dispositivos:**
- Desktop (Windows, macOS, Linux)
- Mobile (Android, iOS)
- Tablets

## 🎯 Benefícios

1. **Redução de fadiga ocular** em ambientes com pouca luz
2. **Economia de bateria** em dispositivos OLED
3. **Experiência personalizada** para o usuário
4. **UI Moderna** seguindo tendências de design
5. **Acessibilidade** para usuários sensíveis à luz

## 🔮 Melhorias Futuras (Opcional)

- [ ] Modo "Auto" que muda baseado no horário
- [ ] Customização de cores pelo usuário
- [ ] Tema "High Contrast" para acessibilidade
- [ ] Preview do tema antes de aplicar
- [ ] Múltiplos temas (não apenas dark/light)

---

**Desenvolvido com ❤️ para o Sistema Stoke**

