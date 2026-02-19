# 🤖 Assistente IA William — v4

Assistente de IA focado em **negócios de auto peças e e-commerce no Mercado Livre**.
Multi-provider (Groq, Claude, OpenAI) com automação via Telegram, GUI desktop e API REST.

---

## ⚡ Início Rápido

```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 2. Configurar API key (editar .env)
#    Mínimo: GROQ_API_KEY (gratuito em console.groq.com)

# 3. Rodar
python run.py                  # CLI (mais leve, recomendado)
python run_gui.py              # Interface gráfica desktop
python run_telegram.py         # Bot do Telegram
python run_service.py          # Serviço em background
```

---

## 📦 Instalação do Zero

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edite .env com suas API keys
python run.py
```

---

## 🧠 Skills de Negócio

| Skill | Função | Status |
|---|---|---|
| 🛒 MercadoLivre | Anúncios, vendas, frete, métricas | ✅ |
| 🔧 AutoPeças | Catálogo, preços, compatibilidade | ✅ |
| 💰 Pricing | Cálculo de preços, margens, markup | ✅ |
| 📢 Marketing | Copy, campanhas, criativos, leads | ✅ |
| 📊 Reports | Relatórios vendas, financeiro, KPIs | ✅ |
| 🎧 Atendimento | Tickets, FAQs, respostas automáticas | ✅ |
| 🔨 Leilão | Monitoramento de oportunidades | ✅ |

---

## 🏗️ Arquitetura

```
WILTOP/
├── run.py              → Entry point CLI
├── run_gui.py          → Entry point GUI
├── run_telegram.py     → Entry point Telegram bot
├── run_service.py      → Entry point serviço background
├── config/             → Configurações centralizadas
├── src/
│   ├── core/           → Motor IA, Orchestrator, Memory, Security
│   ├── ai_providers/   → Groq, OpenAI, Anthropic, Ollama
│   ├── skills/
│   │   ├── business/   → Skills de negócio (ML, AutoPeças, etc.)
│   │   └── builtin/    → Skills gerais do sistema
│   ├── interfaces/
│   │   ├── cli/        → Terminal interativo
│   │   ├── gui/        → Desktop (CustomTkinter)
│   │   ├── api/        → REST API (FastAPI)
│   │   └── bots/       → Telegram bot
│   └── utils/          → Logger, exceptions, validators
├── data/               → Memória, logs, cache, exports
├── tests/              → Testes automatizados
└── docs/               → Documentação técnica
```

---

## 🔑 API Keys

| Provedor | Link | Custo |
|---|---|---|
| Groq (recomendado) | https://console.groq.com/keys | Gratuito |
| Anthropic (Claude) | https://console.anthropic.com | Pago |
| OpenAI | https://platform.openai.com/api-keys | Pago |

---

## 🧪 Testes

```bash
pytest tests/ -v
```

---

## 📄 Licença

MIT — Desenvolvido por William / WILTOP
