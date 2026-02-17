# ⚡ QUICK START - Assistente IA William

**Comece a usar em 5 minutos!**

---

## 🚀 INÍCIO RÁPIDO

### Passo 1: Configure uma API Key

Escolha **UMA** das opções abaixo e configure:

#### Opção A: Groq (Recomendado - GRÁTIS)
1. Acesse: https://console.groq.com/keys
2. Faça login/cadastro
3. Crie uma nova API key
4. Copie a chave

#### Opção B: Anthropic (Claude)
1. Acesse: https://console.anthropic.com/
2. Faça login/cadastro
3. Vá em "API Keys"
4. Crie e copie a chave

#### Opção C: OpenAI (GPT)
1. Acesse: https://platform.openai.com/api-keys
2. Faça login
3. Crie nova chave
4. Copie a chave

### Passo 2: Adicione a Chave no .env

Abra o arquivo `.env` e adicione sua chave:

```env
# Se escolheu Groq:
GROQ_API_KEY=gsk_sua_chave_aqui

# Se escolheu Claude:
ANTHROPIC_API_KEY=sk-ant-sua_chave_aqui

# Se escolheu OpenAI:
OPENAI_API_KEY=sk-sua_chave_aqui
```

Salve o arquivo!

### Passo 3: Instale as Dependências

```bash
# Ative o ambiente virtual
venv\Scripts\activate

# Instale tudo
pip install -r requirements.txt
```

⏱️  **Tempo:** 2-5 minutos (depende da internet)

### Passo 4: Execute!

```bash
# Testar configurações
py -c "from config.settings import settings; print(settings.get_info())"

# Iniciar CLI (quando implementada)
py -m src.interfaces.cli.terminal

# Iniciar GUI (quando implementada)
py -m src.interfaces.gui.main_window
```

---

## 🧪 TESTE RÁPIDO

Teste se tudo está funcionando:

```python
# Execute este código Python
py -c "from config.settings import settings; issues = settings.validate(); print('\n'.join(issues) if issues else 'Tudo OK!')"
```

Se aparecer "Tudo OK!" ou apenas avisos (⚠️), está pronto!

---

## ❓ PROBLEMAS COMUNS

### "ModuleNotFoundError"
**Solução:** Ative o ambiente virtual
```bash
venv\Scripts\activate
```

### "API key not configured"
**Solução:** Edite `.env` e adicione sua chave (veja Passo 2)

### "pip: command not found"
**Solução:** Use `py -m pip` em vez de `pip`
```bash
py -m pip install -r requirements.txt
```

---

## 📚 PRÓXIMOS PASSOS

Depois de configurar:
1. Leia o `README.md` para entender o projeto
2. Veja `INSTRUCOES.md` para desenvolvimento
3. Cheque `STATUS.md` para ver o que está pronto

---

## 💡 DICA PRO

Para não precisar ativar o venv toda vez:

**Windows:**
```bash
# Crie um atalho
echo @echo off > start.bat
echo call venv\Scripts\activate >> start.bat
echo py -m src.interfaces.cli.terminal >> start.bat

# Execute
start.bat
```

---

**Pronto para começar! 🎉**

Se tiver dúvidas, veja `INSTRUCOES.md` ou `README.md`
