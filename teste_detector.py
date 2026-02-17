"""
Teste rapido do detector de intencoes.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.smart_executor import SmartExecutor

def test():
    print("="*60)
    print("TESTE DO DETECTOR DE INTENCOES")
    print("="*60)
    print()

    # Cria executor
    executor = SmartExecutor(authorized=True)
    print(f"Executor criado. Autorizado: {executor.authorized}")
    print()

    # Testes
    tests = [
        "abra o bloco de notas",
        "abre a calculadora",
        "crie um arquivo teste.txt na area de trabalho",
        "mostre uso de memoria",
        "liste arquivos da pasta downloads"
    ]

    for test_msg in tests:
        print(f"\nTESTANDO: '{test_msg}'")
        print("-" * 60)

        # Detecta ações
        actions = executor._detect_actions(test_msg.lower())

        if actions:
            print(f"[OK] {len(actions)} acao(oes) detectada(s):")
            for action in actions:
                print(f"  - Tipo: {action['type']}")
                if 'target' in action:
                    print(f"    Target: {action['target']}")
                if 'path' in action:
                    print(f"    Path: {action['path']}")
        else:
            print("[ERRO] NENHUMA ACAO DETECTADA!")

    print()
    print("="*60)
    print("TESTE COMPLETO!")
    print("="*60)

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

    input("\nPressione ENTER para sair...")
