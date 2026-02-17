"""
Interface CLI (Terminal) do Assistente William.
Interface de linha de comando interativa.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from src.core.ai_engine import get_engine
from src.utils.logger import setup_logging, get_logger
from src.utils.exceptions import AIProviderError
from config.settings import settings

# Setup logging
setup_logging(
    log_file=settings.LOG_FILE,
    log_level=settings.LOG_LEVEL
)

log = get_logger(__name__)
console = Console()


class WilliamCLI:
    """Interface CLI do Assistente William."""

    def __init__(self):
        """Inicializa a CLI."""
        self.engine = None
        self.conversation_history = []
        self.running = True

    def initialize(self):
        """Inicializa o motor de IA."""
        try:
            console.print("[bold cyan]Inicializando Assistente William...[/bold cyan]")
            self.engine = get_engine()

            status = self.engine.get_status()
            console.print(f"[green][OK][/green] Motor IA inicializado")
            console.print(f"[green][OK][/green] Provider: {status['default_provider']}")
            console.print(f"[green][OK][/green] Providers disponíveis: {', '.join(status['providers_available'])}")
            console.print()

        except Exception as e:
            console.print(f"[red][ERRO] Erro ao inicializar: {e}[/red]")
            console.print("\n[yellow]Verifique se sua API key está configurada no arquivo .env[/yellow]")
            sys.exit(1)

    def show_welcome(self):
        """Mostra mensagem de boas-vindas."""
        welcome_text = """
# *** Assistente IA William

Bem-vindo! Estou aqui para ajudar com:
- Conversação inteligente
- Responder perguntas
- Análise e processamento de informações
- E muito mais!

**Comandos disponíveis:**
- `/help` - Mostrar ajuda
- `/status` - Status do sistema
- `/clear` - Limpar histórico
- `/exit` - Sair

Digite sua mensagem e pressione Enter!
"""
        console.print(Panel(Markdown(welcome_text), border_style="cyan"))
        console.print()

    def process_command(self, user_input: str) -> bool:
        """
        Processa comandos especiais.

        Args:
            user_input: Entrada do usuário

        Returns:
            True se foi um comando, False caso contrário
        """
        if not user_input.startswith("/"):
            return False

        command = user_input.lower().strip()

        if command == "/exit" or command == "/quit":
            console.print("[yellow]Até logo! ![/yellow]")
            self.running = False
            return True

        elif command == "/help":
            help_text = """
**Comandos Disponíveis:**

- `/help` - Mostra esta ajuda
- `/status` - Mostra status do sistema
- `/clear` - Limpa histórico de conversação
- `/exit` - Sai do assistente

**Como usar:**
Simplesmente digite sua pergunta ou mensagem e pressione Enter.
O assistente irá processar e responder!
"""
            console.print(Panel(Markdown(help_text), title="Ajuda", border_style="blue"))
            return True

        elif command == "/status":
            status = self.engine.get_status()
            status_text = f"""
**Status do Sistema:**

- Provider padrão: `{status['default_provider']}`
- Providers disponíveis: `{', '.join(status['providers_available'])}`
- Total de providers: `{status['total_providers']}`
- Status: `{status['status']}`
- Mensagens na conversa: `{len(self.conversation_history)}`
"""
            console.print(Panel(Markdown(status_text), title="Status", border_style="green"))
            return True

        elif command == "/clear":
            self.conversation_history = []
            console.print("[green][OK] Histórico limpo![/green]")
            return True

        else:
            console.print(f"[red]Comando desconhecido: {command}[/red]")
            console.print("[yellow]Digite /help para ver comandos disponíveis[/yellow]")
            return True

    def chat(self, message: str):
        """
        Processa mensagem do usuário.

        Args:
            message: Mensagem do usuário
        """
        try:
            # Adiciona ao histórico
            self.conversation_history.append({
                "role": "user",
                "content": message
            })

            # Mostra que está processando
            with console.status("[bold cyan]Pensando...[/bold cyan]", spinner="dots"):
                # Processa com IA
                response = self.engine.chat(
                    message=message,
                    context=self.conversation_history[:-1] if len(self.conversation_history) > 1 else None
                )

            # Adiciona resposta ao histórico
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })

            # Exibe resposta
            console.print()
            console.print(Panel(
                Markdown(response),
                title="[bold cyan]William[/bold cyan]",
                border_style="cyan"
            ))
            console.print()

        except AIProviderError as e:
            console.print(f"[red]Erro na IA: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Erro inesperado: {e}[/red]")
            log.error(f"Erro no chat: {e}", exc_info=True)

    def run(self):
        """Loop principal da CLI."""
        self.initialize()
        self.show_welcome()

        while self.running:
            try:
                # Prompt para usuário
                user_input = Prompt.ask("[bold green]Você[/bold green]").strip()

                if not user_input:
                    continue

                # Processa comando ou mensagem
                if not self.process_command(user_input):
                    self.chat(user_input)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use /exit para sair[/yellow]")
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Erro: {e}[/red]")
                log.error(f"Erro no loop principal: {e}", exc_info=True)


def main():
    """Ponto de entrada da CLI."""
    cli = WilliamCLI()
    cli.run()


if __name__ == "__main__":
    main()
