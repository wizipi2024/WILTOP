# 🤖 Assistente IA William

**Assistente IA completo e profissional** com capacidades avançadas de processamento de linguagem natural, automação, gerenciamento de documentos e integração com múltiplos sistemas.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Funcionalidades

### 🧠 Motor IA Avançado
- Suporte a múltiplos provedores (Groq, Claude, OpenAI)
- Sistema de memória contextual
- Fallback automático entre provedores
- Processamento de linguagem natural

### 📄 Gerenciamento de Documentos
- **Word**: Criar/editar documentos profissionais
- **Excel**: Planilhas com fórmulas e gráficos
- **PDF**: Criar, ler e mesclar PDFs
- **PowerPoint**: Apresentações com múltiplos layouts

### 💻 Operações de Sistema
- Gerenciamento de arquivos (listar, organizar, renomear)
- Limpeza e otimização de sistema
- Sistema de backup automático
- Monitoramento de recursos (CPU, RAM, disco)

### 🌐 Capacidades Web
- Web scraping (páginas estáticas e dinâmicas)
- Pesquisa na web
- Downloads com barra de progresso
- Cliente para APIs REST

### ⚙️ Automação
- Agendamento de tarefas (cron, diário, semanal)
- Triggers baseados em eventos
- Workflows complexos
- Execução em background

### 📊 Análise de Dados
- Estatísticas descritivas
- Geração de gráficos (linha, barra, pizza, scatter, heatmap)
- Relatórios automáticos em PDF/Word
- Detecção de padrões e correlações

### 💬 Múltiplas Interfaces
- **GUI Desktop**: Interface gráfica moderna (customtkinter)
- **CLI**: Terminal interativo com autocomplete
- **API REST**: Integração com outros sistemas
- **Telegram Bot**: Controle remoto via Telegram
- **WhatsApp Bot**: Controle via WhatsApp (experimental)

---

## 📦 Instalação

### Requisitos
- Python 3.9 ou superior
- Windows 10+ (algumas funcionalidades são Windows-específicas)
- 4GB RAM mínimo
- Conexão com internet

### Passo a Passo

1. **Clone ou baixe o projeto**
   ```bash
   git clone https://github.com/seu-usuario/assistente-william.git
   cd assistente-william
   ```

2. **Crie ambiente virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Instale dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure variáveis de ambiente**
   ```bash
   copy .env.example .env
   # Edite .env e adicione suas API keys
   ```

5. **Configure API Keys**

   Obtenha suas chaves em:
   - **Groq**: [https://console.groq.com/keys](https://console.groq.com/keys)
   - **Anthropic** (Claude): [https://console.anthropic.com/](https://console.anthropic.com/)
   - **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

   Edite o arquivo `.env` e adicione ao menos uma chave:
   ```env
   GROQ_API_KEY=your_key_here
   # ou
   ANTHROPIC_API_KEY=your_key_here
   # ou
   OPENAI_API_KEY=your_key_here
   ```

---

## 🚀 Uso

### Interface CLI (Terminal)
```bash
python -m src.interfaces.cli.terminal
```

Comandos disponíveis:
- `/help` - Mostra ajuda
- `/status` - Status do sistema
- `/history` - Histórico de conversas
- `/clear` - Limpa histórico
- `/exit` - Sair

### Interface GUI (Desktop)
```bash
python -m src.interfaces.gui.main_window
```

### API REST
```bash
python -m src.interfaces.api.rest_api
```

Acesse a documentação interativa em: `http://localhost:8000/docs`

### Bot Telegram
```bash
python -m src.interfaces.bots.telegram_bot
```

---

## 📖 Exemplos de Uso

### Criar Documento Word
```python
from src.modules.documents.word_handler import WordHandler

handler = WordHandler()
handler.create_document()
handler.add_heading("Relatório Mensal", level=1)
handler.add_paragraph("Este é um relatório gerado automaticamente.")
handler.save("relatorio.docx")
```

### Pesquisar na Web
```python
from src.modules.internet.search_engine import SearchEngine

search = SearchEngine()
results = search.search_web("Python tutorials", num_results=5)
for result in results:
    print(f"{result['title']}: {result['url']}")
```

### Analisar Dados
```python
from src.modules.analysis.data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()
analyzer.load_data("dados.csv")
stats = analyzer.describe_data()
analyzer.create_line_chart(x="date", y="sales")
```

### Agendar Tarefa
```python
from src.modules.automation.scheduler import TaskScheduler

scheduler = TaskScheduler()
scheduler.schedule_daily(time="14:30", task=backup_files)
```

---

## 🏗️ Arquitetura

```
WILTOP/
├── config/              # Configurações
├── src/
│   ├── core/           # Motor IA e memória
│   ├── ai_providers/   # Integrações com LLMs
│   ├── modules/        # Módulos funcionais
│   ├── interfaces/     # GUI, CLI, API, Bots
│   └── utils/          # Utilitários
├── data/               # Dados persistentes
├── tests/              # Testes automatizados
└── docs/               # Documentação
```

### Fluxo de Dados

```
Usuário → Interface → Command Parser → AI Engine → Memory
                                           ↓
                                    Plugin Manager
                                           ↓
                                   Módulo Específico
                                           ↓
                                      Resposta
```

---

## ⚙️ Configuração Avançada

### Arquivo .env

Todas as configurações podem ser ajustadas no arquivo `.env`:

```env
# Provedor IA padrão
DEFAULT_AI_PROVIDER=groq
DEFAULT_MODEL=llama-3.3-70b-versatile

# Nível de log
LOG_LEVEL=INFO

# Funcionalidades
ENABLE_WEB_SCRAPING=true
ENABLE_FILE_OPERATIONS=true
ENABLE_SYSTEM_OPERATIONS=true

# Limites
MAX_FILE_SIZE_MB=100
MAX_CONCURRENT_TASKS=5
```

### Habilitar/Desabilitar Módulos

Edite `config/settings.py`:
```python
ENABLED_MODULES = [
    "documents",
    "system",
    "internet",
    "automation",
    "analysis"
]
```

---

## 🧪 Testes

Execute os testes:
```bash
pytest tests/ -v
```

Com cobertura:
```bash
pytest --cov=src tests/
```

---

## 📊 Status do Projeto

### ✅ Implementado
- [x] Estrutura do projeto
- [x] Sistema de configurações
- [x] Utilitários (logging, exceptions, validators, formatters)
- [x] Templates de prompts

### 🚧 Em Desenvolvimento
- [ ] Core IA (ai_engine, memory, providers)
- [ ] Módulos funcionais
- [ ] Interfaces (GUI, CLI, API)
- [ ] Testes unitários

### 📅 Roadmap

**Fase 1** (Semanas 1-2): Core IA
- Implementar provedores IA
- Sistema de memória
- Parser de comandos

**Fase 2** (Semanas 3-4): Módulos
- Documentos (Word, Excel, PDF, PPT)
- Sistema (arquivos, limpeza, backup)
- Internet (scraping, download, search)

**Fase 3** (Semanas 5-6): Interfaces
- CLI funcional
- GUI desktop completa

**Fase 4** (Semanas 7-8): Integrações
- API REST
- Bot Telegram
- Módulos de automação e análise

**Fase 5** (Semanas 9-10): Polimento
- Testes completos
- Documentação
- Otimizações

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙋 Suporte

Tem dúvidas ou encontrou um bug?

- Abra uma [issue](https://github.com/seu-usuario/assistente-william/issues)
- Email: contato@exemplo.com

---

## 🌟 Agradecimentos

- [Groq](https://groq.com/) - LLMs rápidos
- [Anthropic](https://www.anthropic.com/) - Claude
- [OpenAI](https://openai.com/) - GPT
- Comunidade Python

---

## 📝 Changelog

### v1.0.0 (Em desenvolvimento)
- ✨ Estrutura inicial do projeto
- ✨ Sistema de configurações
- ✨ Utilit\u00e1rios essenciais
- 🚧 Core IA em desenvolvimento

---

<div align="center">

**Desenvolvido com ❤️ por [Seu Nome]**

[⬆ Voltar ao topo](#-assistente-ia-william)

</div>
