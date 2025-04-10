
# Gevurah – Tracker de Treino Pessoal

**Gevurah** é um aplicativo web pessoal criado com Flask para registrar, acompanhar e visualizar sua evolução em treinos de musculação. Inspirado em temas como disciplina, foco e força interior, o nome vem da Cabala, significando "poder" e "autocontrole".

---

## 🏋️ Funcionalidades

- ✅ Dashboard com nome do exercício, número de séries e carga utilizada
- 📅 Registro automático da data do treino
- 📈 Gráfico de evolução de carga por exercício
- ⏱️ Cronômetro de tempo total de treino
- 🧠 Interface dark com layout limpo e objetivo
- 🛠️ Possibilidade de alterar exercícios e ordens conforme a periodização
- 📲 Suporte a modo PWA (em breve)

---

## 🚀 Como rodar localmente

1. Clone o repositório:
```bash
git clone https://github.com/pedrocamposlive/Gevurah.git
cd Gevurah
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

3. Instale as dependências:
```bash
pip install flask
```

4. Rode o app:
```bash
python app.py
```

5. Acesse no navegador:
```
http://localhost:5000
```

---

## 📂 Estrutura do Projeto

```
Gevurah/
│
├── app.py
├── database.db (criado automaticamente)
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── timer.js
└── README.md
```

---

## 💡 Futuras melhorias

- Autenticação de usuário
- Suporte a múltiplos perfis
- Deploy no Render com PWA ativo
- Exportação de histórico para PDF/CSV
- Filtros por exercício e estatísticas mais avançadas

---

## ✨ Inspiração

> “A disciplina é a ponte entre metas e realizações.” – Jim Rohn

---

## 🔗 Licença

Este projeto é de uso pessoal e livre para adaptações.

---
