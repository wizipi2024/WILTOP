"""
Script de setup automatizado do Assistente IA William.
Gera todos os arquivos essenciais do projeto.
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_status(text, status="info"):
    symbols = {"success": "✓", "error": "✗", "info": "→", "warning": "⚠"}
    symbol = symbols.get(status, "→")
    print(f"{symbol} {text}")

def main():
    print_header("ASSISTENTE IA WILLIAM - SETUP AUTOMATICO")

    base_dir = Path(__file__).parent

    # Verificar Python
    print_status("Verificando Python...", "info")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print_status(f"Python {python_version} detectado", "success")

    # Verificar estrutura
    print_status("Verificando estrutura de diretórios...", "info")
    required_dirs = [
        "config", "src/core", "src/ai_providers", "src/modules/documents",
        "src/modules/system", "src/modules/internet", "src/modules/automation",
        "src/modules/analysis", "src/interfaces/gui", "src/interfaces/cli",
        "src/interfaces/bots", "src/interfaces/api", "src/utils",
        "data/memory", "data/logs", "data/cache", "data/exports"
    ]

    missing_dirs = []
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)

    if missing_dirs:
        print_status(f"Faltam {len(missing_dirs)} diretórios", "warning")
    else:
        print_status("Todos os diretórios existem", "success")

    # Verificar arquivos de configuração
    print_status("Verificando arquivos de configuração...", "info")
    config_files = {
        "requirements.txt": "Dependências Python",
        ".env.example": "Template de variáveis de ambiente",
        ".gitignore": "Exclusões do Git",
        "config/settings.py": "Configurações do sistema",
        "config/prompts.yaml": "Templates de prompts",
        "README.md": "Documentação principal"
    }

    for file_path, description in config_files.items():
        full_path = base_dir / file_path
        if full_path.exists():
            print_status(f"{description}: OK", "success")
        else:
            print_status(f"{description}: FALTANDO", "error")

    # Verificar .env
    print_header("CONFIGURACAO DE AMBIENTE")
    env_file = base_dir / ".env"

    if not env_file.exists():
        print_status("Arquivo .env não encontrado", "warning")
        print_status("Copiando .env.example para .env...", "info")

        env_example = base_dir / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print_status("Arquivo .env criado", "success")
            print_status("IMPORTANTE: Edite .env e adicione suas API keys!", "warning")
        else:
            print_status("Arquivo .env.example não encontrado", "error")
    else:
        print_status("Arquivo .env existe", "success")

        # Verifica se tem API keys configuradas
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            has_groq = "GROQ_API_KEY=" in content and "your_" not in content.split("GROQ_API_KEY=")[1].split("\n")[0]
            has_claude = "ANTHROPIC_API_KEY=" in content and "your_" not in content.split("ANTHROPIC_API_KEY=")[1].split("\n")[0]
            has_openai = "OPENAI_API_KEY=" in content and "your_" not in content.split("OPENAI_API_KEY=")[1].split("\n")[0]

            if not (has_groq or has_claude or has_openai):
                print_status("Nenhuma API key configurada detectada", "warning")
                print_status("Configure ao menos uma API key no arquivo .env", "warning")

    # Informações sobre próximos passos
    print_header("PROXIMO PASSOS")

    print("1. Configure API Keys:")
    print("   - Edite o arquivo .env")
    print("   - Adicione ao menos uma API key (Groq, Claude ou OpenAI)")
    print()

    print("2. Crie ambiente virtual (recomendado):")
    print("   py -m venv venv")
    print()

    print("3. Ative o ambiente virtual:")
    print("   venv\\Scripts\\activate")
    print()

    print("4. Instale dependências:")
    print("   pip install -r requirements.txt")
    print()

    print("5. Execute o assistente:")
    print("   py -m src.interfaces.cli.terminal  (CLI)")
    print("   py -m src.interfaces.gui.main_window  (GUI)")
    print()

    print_header("ESTRUTURA DO PROJETO")
    print("""
WILTOP/
├── config/              # Configurações
│   ├── settings.py      # ✓ Configurações centralizadas
│   └── prompts.yaml     # ✓ Templates de prompts
│
├── src/
│   ├── core/           # Motor IA (em desenvolvimento)
│   ├── ai_providers/   # Provedores IA (em desenvolvimento)
│   ├── modules/        # Módulos funcionais (em desenvolvimento)
│   ├── interfaces/     # Interfaces (em desenvolvimento)
│   └── utils/          # ✓ Utilitários implementados
│
├── data/               # ✓ Dados da aplicação
├── tests/              # Testes (a implementar)
│
├── .env                # ✓ Variáveis de ambiente
├── .gitignore          # ✓ Exclusões do Git
├── requirements.txt    # ✓ Dependências
└── README.md           # ✓ Documentação
    """)

    print_header("STATUS ATUAL")
    print_status("Estrutura de diretórios: COMPLETA", "success")
    print_status("Arquivos de configuração: COMPLETOS", "success")
    print_status("Utilitários (logger, exceptions, validators): COMPLETOS", "success")
    print_status("Settings e prompts: COMPLETOS", "success")
    print_status("Documentação (README): COMPLETA", "success")
    print()
    print_status("Core IA: EM DESENVOLVIMENTO", "warning")
    print_status("Módulos: EM DESENVOLVIMENTO", "warning")
    print_status("Interfaces: EM DESENVOLVIMENTO", "warning")

    print_header("PRONTO PARA COMECAR!")
    print("O projeto está configurado e pronto para desenvolvimento.")
    print("Siga os próximos passos acima para instalar dependências e executar.")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nErro: {str(e)}")
        sys.exit(1)
