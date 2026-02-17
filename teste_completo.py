"""
Teste completo do fluxo: deteccao -> execucao.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.smart_executor import get_smart_executor

def test():
    print("="*70)
    print("TESTE COMPLETO DO WILLIAM")
    print("="*70)
    print()

    # Verifica autorizacao
    auth_file = Path(__file__).parent / ".authorized"
    print(f"1. Verificando autorizacao...")
    if auth_file.exists():
        print(f"   [OK] Arquivo .authorized existe: {auth_file}")
    else:
        print(f"   [ERRO] Arquivo .authorized NAO existe!")
        print(f"   Execute: python AUTORIZAR_TUDO.py")
        return

    # Cria executor
    print()
    print(f"2. Criando executor...")
    executor = get_smart_executor(authorized=False)
    print(f"   Executor criado.")

    # Checa autorizacao
    print()
    print(f"3. Checando autorizacao...")
    is_auth = executor.check_authorization()
    print(f"   Autorizado: {is_auth}")
    print(f"   executor.authorized: {executor.authorized}")

    if not is_auth:
        print()
        print("[ERRO] Executor NAO esta autorizado!")
        print("Execute: python AUTORIZAR_TUDO.py")
        return

    # Testa comando
    print()
    print("="*70)
    print("TESTE 1: Abrir Bloco de Notas")
    print("="*70)

    user_msg = "abra o bloco de notas"
    ai_response = "Vou abrir o Bloco de Notas para voce!"

    print(f"Usuario: {user_msg}")
    print(f"IA: {ai_response}")
    print()

    result = executor.interpret_and_execute(user_msg, ai_response)

    print(f"Resultado:")
    print(f"  - Executed: {result.get('executed')}")
    print(f"  - Actions: {len(result.get('actions', []))}")
    print()

    if result.get('executed'):
        print("[OK] Acao FOI executada!")
        for action in result.get('actions', []):
            print(f"  - Success: {action.get('success')}")
            print(f"  - Message: {action.get('message')}")
    else:
        print("[ERRO] Acao NAO foi executada!")
        print(f"  Motivo: {result.get('message', 'Desconhecido')}")

    # Teste 2
    print()
    print("="*70)
    print("TESTE 2: Criar Arquivo")
    print("="*70)

    user_msg = "crie um arquivo teste.txt na area de trabalho"
    ai_response = "Vou criar o arquivo teste.txt na sua area de trabalho."

    print(f"Usuario: {user_msg}")
    print(f"IA: {ai_response}")
    print()

    result = executor.interpret_and_execute(user_msg, ai_response)

    print(f"Resultado:")
    print(f"  - Executed: {result.get('executed')}")
    print(f"  - Actions: {len(result.get('actions', []))}")
    print()

    if result.get('executed'):
        print("[OK] Acao FOI executada!")
        for action in result.get('actions', []):
            print(f"  - Success: {action.get('success')}")
            print(f"  - Message: {action.get('message')}")
    else:
        print("[ERRO] Acao NAO foi executada!")

    # Teste 3
    print()
    print("="*70)
    print("TESTE 3: Informacoes do Sistema")
    print("="*70)

    user_msg = "mostre uso de memoria"
    ai_response = "Vou verificar o uso de memoria para voce."

    print(f"Usuario: {user_msg}")
    print(f"IA: {ai_response}")
    print()

    result = executor.interpret_and_execute(user_msg, ai_response)

    print(f"Resultado:")
    print(f"  - Executed: {result.get('executed')}")
    print(f"  - Actions: {len(result.get('actions', []))}")
    print()

    if result.get('executed'):
        print("[OK] Acao FOI executada!")
        for action in result.get('actions', []):
            print(f"  - Success: {action.get('success')}")
            if action.get('message'):
                msg = action.get('message')[:200]
                print(f"  - Message: {msg}...")
    else:
        print("[ERRO] Acao NAO foi executada!")

    print()
    print("="*70)
    print("TESTE COMPLETO!")
    print("="*70)
    print()
    print("Se TODOS os testes mostraram [OK], o William esta funcionando!")
    print()

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"\nERRO CRITICO: {e}")
        import traceback
        traceback.print_exc()

    input("\nPressione ENTER para sair...")
