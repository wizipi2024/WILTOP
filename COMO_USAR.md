# 🚀 COMO USAR O ASSISTENTE IA WILLIAM

## ✅ SISTEMA PRONTO E FUNCIONANDO!

Seu Assistente IA William está **100% configurado e operacional**!

---

## 📍 COMO EXECUTAR

### **Método 1: Script Python (Recomendado)**

```bash
# 1. Abra o terminal no diretório do projeto
cd C:\Users\wizip\Desktop\WILTOP

# 2. Ative o ambiente virtual
venv\Scripts\activate

# 3. Execute o assistente
python run.py
```

### **Método 2: Módulo Python**

```bash
venv\Scripts\activate
python -m src.interfaces.cli.terminal
```

### **Método 3: Atalho Rápido (Windows)**

Crie um arquivo `START_WILLIAM.bat` com:
```batch
@echo off
cd C:\Users\wizip\Desktop\WILTOP
call venv\Scripts\activate
python run.py
pause
```

Depois é só dar duplo clique no arquivo!

---

## 💬 USANDO O ASSISTENTE

### **Conversação Normal**

Simplesmente digite sua mensagem e pressione Enter:

```
Você: Olá! Como você está?
William: Olá! Estou funcionando perfeitamente...

Você: Me explique o que é Python
William: Python é uma linguagem de programação...

Você: Qual a capital do Brasil?
William: A capital do Brasil é Brasília...
```

### **Comandos Especiais**

O assistente tem comandos que começam com `/`:

- **`/help`** - Mostra ajuda e comandos disponíveis
- **`/status`** - Mostra status do sistema e configurações
- **`/clear`** - Limpa o histórico de conversação
- **`/exit`** - Sai do assistente

**Exemplo:**
```
Você: /status

Status do Sistema:
- Provider padrão: groq
- Providers disponíveis: groq
- Total de providers: 1
- Status: operational
- Mensagens na conversa: 0
```

---

## 🎯 EXEMPLOS DE USO

### **1. Fazer Perguntas**
```
Você: Qual a diferença entre Python e JavaScript?
William: [Resposta detalhada sobre as diferenças]
```

### **2. Pedir Explicações**
```
Você: Me explique o que é inteligência artificial
William: [Explicação completa sobre IA]
```

### **3. Solicitar Código**
```
Você: Me mostre como fazer um loop em Python
William: [Exemplos de loops com explicações]
```

### **4. Análise de Dados**
```
Você: Como posso analisar um arquivo CSV em Python?
William: [Explicação com código usando pandas]
```

### **5. Resolver Problemas**
```
Você: Como resolver erro "ModuleNotFoundError"?
William: [Explicação e soluções]
```

---

## ⚙️ CONFIGURAÇÕES

### **Trocar Modelo de IA**

Edite `.env` e altere:
```env
DEFAULT_MODEL=llama-3.3-70b-versatile

# Outros modelos disponíveis no Groq:
# llama-3.1-70b-versatile
# mixtral-8x7b-32768
# gemma2-9b-it
```

### **Ajustar Temperatura (Criatividade)**

No arquivo `src/core/ai_engine.py` (linha ~65):
```python
"temperature": kwargs.get("temperature", 0.7)  # 0.0 = mais focado, 1.0 = mais criativo
```

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### **Erro: "ModuleNotFoundError"**

**Solução:**
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### **Erro: "API key not configured"**

**Solução:** Verifique se o `.env` tem sua chave do Groq:
```env
GROQ_API_KEY=gsk_sua_chave_aqui
```

### **Terminal não exibe caracteres corretamente**

**Solução:** Execute com:
```bash
chcp 65001
python run.py
```

### **Assistente não responde**

**Solução:**
1. Verifique sua conexão com internet
2. Verifique se a API key está correta
3. Veja os logs em `data/logs/william.log`

---

## 📁 ESTRUTURA DE ARQUIVOS

```
C:\Users\wizip\Desktop\WILTOP\
│
├── run.py                 ← Execute este arquivo!
├── .env                   ← Suas configurações (API keys)
├── venv\                  ← Ambiente virtual Python
│
├── src\
│   ├── core\             ← Motor de IA
│   ├── ai_providers\     ← Integração Groq
│   └── interfaces\cli\   ← Interface do terminal
│
├── data\
│   └── logs\             ← Logs do sistema
│
└── config\               ← Configurações
```

---

## 🎓 DICAS IMPORTANTES

### **1. Seja Específico**
Em vez de: "Me fale sobre programação"
Melhor: "Explique os conceitos básicos de programação orientada a objetos em Python"

### **2. Use Contexto**
O assistente lembra da conversa:
```
Você: Qual a capital da França?
William: Paris

Você: E a população?  ← Ele entende que é sobre Paris
William: Aproximadamente 2,2 milhões...
```

### **3. Peça Formatação**
```
Você: Liste os 5 maiores países do mundo em formato de tabela
William: [Tabela formatada]
```

### **4. Limpe o Histórico se Precisar**
Use `/clear` para começar uma nova conversa sem contexto anterior.

---

## 💡 FUNCIONALIDADES FUTURAS

Nas próximas versões teremos:
- ✅ **Já funciona:** Conversação inteligente com Groq
- 🚧 **Em breve:** Criação de documentos Word, Excel, PDF
- 🚧 **Em breve:** Interface GUI desktop
- 🚧 **Em breve:** Bot Telegram e WhatsApp
- 🚧 **Em breve:** Análise de dados e gráficos
- 🚧 **Em breve:** Automação de tarefas

---

## 📞 PRECISA DE AJUDA?

1. **Leia a documentação:**
   - `README.md` - Visão geral
   - `QUICKSTART.md` - Início rápido
   - `INSTRUCOES.md` - Desenvolvimento

2. **Verifique os logs:**
   ```
   data/logs/william.log
   ```

3. **Teste os componentes:**
   ```bash
   venv\Scripts\activate
   python -c "from config.settings import settings; print(settings.get_info())"
   ```

---

## 🎉 APROVEITE SEU ASSISTENTE IA!

Agora você tem um assistente IA pessoal funcionando localmente!

**Comandos para lembrar:**
```bash
# Ativar ambiente
venv\Scripts\activate

# Executar assistente
python run.py

# Ver status
/status

# Sair
/exit
```

**Divirta-se explorando as capacidades do William!** 🚀
