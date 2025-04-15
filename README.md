
 
 
 
   ██████      ███████     ██    ██     ██    ██     ██████       █████      ██   ██ 
   ██           ██          ██    ██     ██    ██     ██   ██     ██   ██     ██   ██ 
   ██   ███     █████       ██    ██     ██    ██     ██████      ███████     ███████ 
   ██    ██     ██           ██  ██      ██    ██     ██   ██     ██   ██     ██   ██ 
    ██████      ███████       ████        ██████      ██   ██     ██   ██     ██   ██  


Gevurah – Fit Progress 🏋🏽‍♂️

é um app pessoal de acompanhamento de treino de força e hipertrofia, criado com Flask + HTML/CSS, e agora como um **PWA (Progressive Web App)**.  
Ideal para visualizar progresso real, série por série, exercício por exercício, com dados salvos localmente e usabilidade offline.

---

##  Funcionalidades

### Registro de Treino
- Cadastro de **exercícios únicos** com nome personalizado
- Registro de cada **série individualmente**:
  - Nº da série
  - Carga utilizada
  - Nº de repetições
  - Data automática
- Histórico completo com todas as séries ordenadas por data

### Dashboard de Progresso
- Gráfico com **média de carga** por exercício ao longo do tempo
- Visualização clara da **evolução semanal** ou por periodização
- Botão para **revelar o gráfico sob demanda**

### Interface Responsiva
- Visual escuro (`dark theme`)
- Layout otimizado para celular (formato 9:16)
- Interface fluida, moderna e limpa com Tailwind CSS

###   Catálogo de Exercícios
- Dropdown com exercícios já cadastrados
- Evita erros de digitação (consistência para os gráficos)
- Interface separada para **criação de novos exercícios**

###   Progressive Web App (PWA)
- Instalável no Android, iOS e desktop
- Tela cheia (standalone), ícone customizado com o logo do app
- `manifest.json` e `service-worker.js` configurados
- **Splash screen automático** com fundo escuro e logo

###   Modo Offline
- Funciona **sem internet** após primeiro acesso
- Arquivos estáticos e offline.html **cacheados**
- Mostra mensagem amigável quando está sem conexão

---

##   Tecnologias utilizadas

- Python + Flask
- HTML5 + Tailwind CSS
- Chart.js (para gráficos)
- SQLite3
- JavaScript (fetch, service worker)
- PWA (manifest, cache offline)

---

##   Estrutura de diretórios

