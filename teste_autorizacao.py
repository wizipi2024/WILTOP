"""
Teste de autorizacao - mostra estado exato.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test():
    print("="*70)
    print("TESTE DE AUTORIZACAO")
    print("="*70)
    print()

    # Verifica arquivo
    auth_file = Path(__file__).parent / ".authorized"
    print(f"1. Arquivo .authorized:")
    print(f"   Caminho: {auth_file}")
    print(f"   Existe: {auth_file.exists()}")
    print()

    # Testa SmartExecutor direto
    print("2. Criando SmartExecutor com authorized=True:")
    from src.core.smart_executor import SmartExecutor

    executor = SmartExecutor(authorized=True)
    print(f"   executor.authorized: {executor.authorized}")
    print(f"   executor.system.authorized: {executor.system.authorized}")
    print()

    # Testa get_smart_executor
    print("3. Usando get_smart_executor(authorized=True):")
    from src.core.smart_executor import get_smart_executor

    executor2 = get_smart_executor(authorized=True)
    print(f"   executor.authorized: {executor2.authorized}")
    print(f"   executor.system.authorized: {executor2.system.authorized}")
    print()

    # Testa interpret_and_execute
    print("4. Testando interpret_and_execute:")
    result = executor2.interpret_and_execute(
        "abra o bloco de notas",
        "Vou abrir o Bloco de Notas!"
    )
    print(f"   Executed: {result.get('executed')}")
    print(f"   Actions: {len(result.get('actions', []))}")
    if result.get('actions'):
        for action in result['actions']:
            print(f"   - Success: {action.get('success')}")
            print(f"   - Message: {action.get('message')}")
    print()

    print("="*70)
    print("TESTE COMPLETO!")
    print("="*70)

    if result.get('executed'):
        print("\n[OK] TUDO FUNCIONANDO!")
    else:
        print("\n[ERRO] Algo errado com autorizacao!")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()

    input("\nPressione ENTER para sair...")
