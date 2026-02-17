"""
Script de diagnóstico do William.
Verifica se tudo está configurado corretamente.
"""

import os
import sys
from pathlib import Path

def check_authorization():
    """Verifica autorização."""
    auth_file = Path(__file__).parent / ".authorized"
    if auth_file.exists():
        print("[OK] Sistema AUTORIZADO")
        return True
    else:
        print("[!] Sistema NAO AUTORIZADO")
        print("    Execute: python AUTORIZAR_TUDO.py")
        return False

def check_environment():
    """Verifica ambiente virtual."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("[OK] Ambiente virtual ativado")
        return True
    else:
        print("[!] Ambiente virtual NAO ativado")
        print("    Execute: venv\\Scripts\\activate")
        return False

def check_dependencies():
    """Verifica dependências principais."""
    deps = {
        "groq": "Groq API",
        "customtkinter": "Interface GUI",
        "psutil": "Informacoes do sistema",
        "rich": "Terminal colorido"
    }

    all_ok = True
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"[OK] {name} instalado")
        except ImportError:
            print(f"[ERRO] {name} NAO instalado")
            all_ok = False

    return all_ok

def check_api_key():
    """Verifica API key."""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("[ERRO] Arquivo .env NAO encontrado")
        return False

    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "GROQ_API_KEY=" in content and len(content.split("GROQ_API_KEY=")[1].split("\n")[0]) > 10:
                print("[OK] API Key Groq configurada")
                return True
            else:
                print("[ERRO] API Key Groq NAO configurada")
                return False
    except Exception as e:
        print(f"[ERRO] Erro ao ler .env: {e}")
        return False

def check_directories():
    """Verifica estrutura de diretórios."""
    dirs = ["data", "data/logs", "data/memory", "src", "config"]
    all_ok = True

    for dir_name in dirs:
        dir_path = Path(__file__).parent / dir_name
        if dir_path.exists():
            print(f"[OK] Diretorio {dir_name} existe")
        else:
            print(f"[ERRO] Diretorio {dir_name} NAO existe")
            all_ok = False

    return all_ok

def test_smart_executor():
    """Testa detector de intenções."""
    print("\n" + "="*60)
    print("TESTE DO DETECTOR DE INTENCOES")
    print("="*60)

    try:
        from src.core.smart_executor import SmartExecutor

        executor = SmartExecutor(authorized=True)

        test_messages = [
            "abra o bloco de notas",
            "crie um arquivo teste.txt na area de trabalho",
            "mostre uso de memoria",
            "liste arquivos da pasta downloads"
        ]

        for msg in test_messages:
            actions = executor._detect_actions(msg.lower())
            if actions:
                print(f"\n[OK] '{msg}' -> {len(actions)} acao(oes) detectada(s)")
                for action in actions:
                    print(f"     Tipo: {action['type']}")
            else:
                print(f"\n[ERRO] '{msg}' -> Nenhuma acao detectada")

        return True

    except Exception as e:
        print(f"\n[ERRO] Falha ao testar: {e}")
        return False

def main():
    """Função principal."""
    print("="*60)
    print("DIAGNOSTICO DO WILLIAM")
    print("="*60)
    print()

    results = []

    print("1. Verificando ambiente virtual...")
    results.append(check_environment())
    print()

    print("2. Verificando autorizacao...")
    results.append(check_authorization())
    print()

    print("3. Verificando dependencias...")
    results.append(check_dependencies())
    print()

    print("4. Verificando API Key...")
    results.append(check_api_key())
    print()

    print("5. Verificando diretorios...")
    results.append(check_directories())
    print()

    print("6. Testando detector de intencoes...")
    results.append(test_smart_executor())
    print()

    # Resumo
    print()
    print("="*60)
    print("RESUMO")
    print("="*60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"\n[OK] Todos os testes passaram! ({passed}/{total})")
        print("\nO William esta pronto para usar!")
        print("Execute: ABRIR_COMPLETO.bat")
    else:
        print(f"\n[!] {total - passed} problema(s) encontrado(s)")
        print("\nResolva os problemas acima antes de usar o William.")

    print()
    input("Pressione ENTER para sair...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERRO CRITICO: {e}")
        input("Pressione ENTER para sair...")
