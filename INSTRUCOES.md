# 🎯 INSTRUCOES - Assistente IA William

## ✅ O QUE JÁ ESTÁ PRONTO

### Estrutura Completa
- ✅ Todos os diretórios criados
- ✅ Arquivos `__init__.py` em todos os pacotes
- ✅ Estrutura de dados (memory/, logs/, cache/, exports/)

### Configurações
- ✅ `requirements.txt` - Todas as dependências listadas
- ✅ `.env` - Arquivo de variáveis de ambiente criado
- ✅ `.env.example` - Template de configuração
- ✅ `.gitignore` - Exclusões do Git configuradas
- ✅ `config/settings.py` - Sistema de configurações completo
- ✅ `config/prompts.yaml` - Templates de prompts IA

### Utilitários Implementados
- ✅ `src/utils/exceptions.py` - Hierarquia completa de exceções
- ✅ `src/utils/logger.py` - Sistema de logging avançado (Loguru)
- ✅ `src/utils/validators.py` - Validadores de entrada
- ✅ `src/utils/formatters.py` - Formatadores de saída

### Documentação
- ✅ `README.md` - Documentação completa do projeto
- ✅ `INSTRUCOES.md` - Este arquivo

### Ambiente Python
- ✅ Ambiente virtual criado em `venv/`
- ✅ Dependências essenciais instaladas

---

## 📋 PRÓXIMOS PASSOS ESSENCIAIS

### 1. Configurar API Keys (OBRIGATÓRIO)

Edite o arquivo `.env` e adicione **ao menos uma** API key:

```env
# Escolha pelo menos um:
GROQ_API_KEY=sua_chave_groq_aqui          # Grátis (recomendado para começar)
ANTHROPIC_API_KEY=sua_chave_claude_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
```

**Onde obter as chaves:**
- **Groq** (Grátis): https://console.groq.com/keys
- **Anthropic** (Claude): https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys

### 2. Instalar Todas as Dependências

Ative o ambiente virtual e instale as dependências:

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Instalar todas as dependências
pip install -r requirements.txt

# Isto pode levar alguns minutos...
```

### 3. Implementar os Módulos Core (Em Desenvolvimento)

Os seguintes arquivos precisam ser implementados:

#### Core IA (PRIORIDADE ALTA)
- `src/ai_providers/base_provider.py` - Interface para provedores IA
- `src/ai_providers/groq_provider.py` - Integração com Groq
- `src/ai_providers/claude_provider.py` - Integração com Claude
- `src/ai_providers/openai_provider.py` - Integração com OpenAI
- `src/core/ai_engine.py` - Motor principal IA
- `src/core/memory.py` - Sistema de memória
- `src/core/command_parser.py` - Parser de comandos

#### Interfaces (PRIORIDADE MÉDIA)
- `src/interfaces/cli/terminal.py` - Interface CLI
- `src/interfaces/gui/main_window.py` - Interface GUI

#### Módulos Funcionais (PRIORIDADE BAIXA)
- Documentos (Word, Excel, PDF, PPT)
- Sistema (file_manager, cleaner, backup)
- Internet (scraper, search, downloader)
- Automação (scheduler, triggers)
- Análise (data_analyzer, charts)

---

## 🚀 COMO EXECUTAR (Quando Estiver Pronto)

### Interface CLI
```bash
venv\Scripts\activate
py -m src.interfaces.cli.terminal
```

### Interface GUI
```bash
venv\Scripts\activate
py -m src.interfaces.gui.main_window
```

### API REST
```bash
venv\Scripts\activate
py -m src.interfaces.api.rest_api
```

---

## 📁 ESTRUTURA DO PROJETO

```
WILTOP/
├── config/                    ✅ COMPLETO
│   ├── settings.py           # Configurações centralizadas
│   └── prompts.yaml          # Templates de prompts
│
├── src/
│   ├── core/                 🚧 EM DESENVOLVIMENTO
│   │   ├── ai_engine.py     # Motor IA principal
│   │   ├── memory.py        # Sistema de memória
│   │   └── command_parser.py
│   │
│   ├── ai_providers/         🚧 EM DESENVOLVIMENTO
│   │   ├── base_provider.py
│   │   ├── groq_provider.py
│   │   ├── claude_provider.py
│   │   └── openai_provider.py
│   │
│   ├── modules/              📅 PENDENTE
│   │   ├── documents/       # Word, Excel, PDF, PPT
│   │   ├── system/          # File ops, cleaning, backup
│   │   ├── internet/        # Web scraping, downloads
│   │   ├── automation/      # Scheduler, triggers
│   │   └── analysis/        # Data analysis, charts
│   │
│   ├── interfaces/           🚧 EM DESENVOLVIMENTO
│   │   ├── gui/             # Interface gráfica
│   │   ├── cli/             # Terminal
│   │   ├── api/             # REST API
│   │   └── bots/            # Telegram, WhatsApp
│   │
│   └── utils/                ✅ COMPLETO
│       ├── exceptions.py     # Exceções customizadas
│       ├── logger.py         # Sistema de logging
│       ├── validators.py     # Validadores
│       └── formatters.py     # Formatadores
│
├── data/                     ✅ PRONTO
│   ├── memory/              # Banco de memória
│   ├── logs/                # Logs do sistema
│   ├── cache/               # Cache temporário
│   └── exports/             # Arquivos gerados
│
├── tests/                    📅 PENDENTE
│   ├── unit/                # Testes unitários
│   └── integration/         # Testes de integração
│
├── .env                      ⚠️  CONFIGURAR API KEYS
├── .gitignore                ✅ COMPLETO
├── requirements.txt          ✅ COMPLETO
├── README.md                 ✅ COMPLETO
└── venv/                     ✅ AMBIENTE CRIADO
```

---

## 🔍 TESTANDO O QUE JÁ FUNCIONA

### Testar Configurações
```python
from config.settings import settings

# Ver info do sistema
print(settings.get_info())

# Validar configurações
issues = settings.validate()
for issue in issues:
    print(issue)
```

### Testar Logger
```python
from src.utils.logger import get_logger

log = get_logger("test")
log.info("Testando sistema de logging")
log.warning("Este é um aviso")
log.error("Este é um erro")
```

### Testar Validadores
```python
from src.utils.validators import InputValidator

# Validar URL
try:
    InputValidator.validate_url("https://example.com")
    print("URL válida!")
except Exception as e:
    print(f"Erro: {e}")
```

---

## 💡 DICAS IMPORTANTES

### 1. Desenvolvimento Incremental
Implemente os módulos nesta ordem:
1. **Core IA** (ai_providers + ai_engine + memory) - Base do sistema
2. **CLI básico** - Para testar rapidamente
3. **Um módulo funcional** (ex: documents) - Funcionalidade concreta
4. **GUI** - Interface visual
5. **Demais módulos** - Expandir funcionalidades

### 2. Testes Frequentes
Teste cada componente isoladamente antes de integrar:
```python
# Exemplo: testar provider IA
from src.ai_providers.groq_provider import GroqProvider

provider = GroqProvider()
response = provider.chat("Olá, você está funcionando?")
print(response)
```

### 3. Logs São Seus Amigos
O sistema de logging está completo. Use para debug:
```python
from src.utils.logger import get_logger

log = get_logger(__name__)
log.debug("Informação de debug")
log.info("Informação geral")
log.error("Erro ocorrido", extra={"context": "..."})
```

### 4. Exceções Customizadas
Use as exceções específicas do projeto:
```python
from src.utils.exceptions import AIProviderError, ValidationError

try:
    # seu código
    pass
except Exception as e:
    raise AIProviderError("Falha no provider", {"error": str(e)})
```

---

## 📚 RECURSOS ÚTEIS

### Documentação das Bibliotecas
- **Groq**: https://console.groq.com/docs
- **Anthropic**: https://docs.anthropic.com
- **OpenAI**: https://platform.openai.com/docs
- **Loguru**: https://loguru.readthedocs.io
- **CustomTkinter**: https://customtkinter.tomschimansky.com

### Exemplos de Código
Veja a pasta `docs/` para exemplos específicos de cada módulo.

---

## ⚠️  PROBLEMAS COMUNS

### "ModuleNotFoundError"
- Certifique-se que o ambiente virtual está ativado
- Reinstale as dependências: `pip install -r requirements.txt`

### "API Key not configured"
- Edite `.env` e adicione sua(s) chave(s) de API
- Reinicie o programa após alterar `.env`

### "Permission denied"
- Algumas operações de sistema requerem privilégios de administrador
- Execute o terminal como administrador se necessário

---

## 🎯 ROADMAP

### Fase 1 (Semanas 1-2) - MVP
- [ ] Implementar provedores IA (Groq, Claude, OpenAI)
- [ ] Implementar motor IA (ai_engine.py)
- [ ] Implementar CLI básica
- [ ] Teste de conversação simples

### Fase 2 (Semanas 3-4) - Funcionalidades
- [ ] Módulo de documentos (Word, Excel, PDF)
- [ ] Módulo de sistema (arquivos, limpeza)
- [ ] Testes unitários

### Fase 3 (Semanas 5-6) - Interface
- [ ] GUI completa
- [ ] Memória persistente
- [ ] Análise de dados

### Fase 4 (Semanas 7-8) - Integrações
- [ ] API REST
- [ ] Bot Telegram
- [ ] Automação avançada

---

## 🏁 STATUS ATUAL

```
FASE ATUAL: FUNDAÇÃO COMPLETA ✅

Próximo passo: Implementar Core IA
Prioridade: Alta
Tempo estimado: 2-3 dias
```

---

## 📞 SUPORTE

Se tiver dúvidas ou problemas:
1. Consulte o `README.md`
2. Verifique a pasta `docs/`
3. Revise os logs em `data/logs/`

**Bom desenvolvimento! 🚀**
