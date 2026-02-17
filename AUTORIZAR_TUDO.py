"""
Script para AUTORIZAR O WILLIAM A FAZER TUDO NO SEU PC!

ATENÇÃO: Isto dá ao William acesso TOTAL ao seu computador!

Ele poderá:
- Executar qualquer comando do Windows
- Criar, ler, modificar e deletar arquivos
- Abrir e fechar programas
- Gerenciar processos
- Acessar informações do sistema
- E MUITO MAIS!

Use apenas se você REALMENTE confiar no assistente!
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.action_executor import get_action_executor
from src.modules.system.system_control import get_system_controller
from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    """Autoriza o William a ter controle total."""

    # Banner de aviso
    warning = """
[bold red]⚠️  ATENÇÃO - AUTORIZAÇÃO TOTAL ⚠️[/bold red]

Você está prestes a dar ao William ACESSO TOTAL ao seu PC!

[yellow]O que ele poderá fazer:[/yellow]
✓ Executar qualquer comando do Windows
✓ Criar, ler, modificar e deletar QUALQUER arquivo
✓ Abrir e fechar programas
✓ Gerenciar processos do sistema
✓ Modificar configurações
✓ Instalar/desinstalar programas
✓ Acessar qualquer pasta
✓ E MUITO MAIS!

[bold]Isto é PERMANENTE durante a sessão![/bold]

[green]Use apenas se você CONFIA TOTALMENTE no assistente![/green]
"""

    console.print(Panel(warning, border_style="red", title="[bold]AVISO IMPORTANTE[/bold]"))
    console.print()

    # Confirmação
    resposta = input("Digite 'SIM AUTORIZO TUDO' para confirmar: ").strip()

    if resposta == "SIM AUTORIZO TUDO":
        # Autoriza o executor de ações
        executor = get_action_executor(authorized=True)

        # Autoriza o controlador de sistema
        controller = get_system_controller(authorized=True)

        console.print()
        console.print("[bold green]✓ WILLIAM AUTORIZADO![/bold green]")
        console.print()
        console.print("O assistente agora tem acesso total ao seu sistema.")
        console.print("Esta configuração vale para esta sessão.")
        console.print()
        console.print("[cyan]Você pode usar o William normalmente agora![/cyan]")
        console.print()

        # Cria arquivo de flag de autorização
        flag_file = os.path.join(os.path.dirname(__file__), ".authorized")
        with open(flag_file, 'w') as f:
            f.write("AUTHORIZED")

        console.print(f"[dim]Arquivo de autorização criado: {flag_file}[/dim]")
        console.print()

        console.print("[bold yellow]Agora você pode:[/bold yellow]")
        console.print("1. Executar: python run_gui.py")
        console.print("2. Ou duplo clique em: ABRIR_WILLIAM.bat")
        console.print()
        console.print("E o William terá poderes totais! 🚀")

    else:
        console.print()
        console.print("[yellow]Autorização cancelada.[/yellow]")
        console.print("O William continuará funcionando normalmente,")
        console.print("mas sem acesso às funções do sistema.")

    console.print()
    input("Pressione ENTER para sair...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelado pelo usuário.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Erro: {e}[/red]")
