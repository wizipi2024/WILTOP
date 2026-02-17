"""
Interface GUI do Assistente IA William.
Interface gráfica moderna com customtkinter.
"""

import customtkinter as ctk
from tkinter import scrolledtext
import threading
from datetime import datetime

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

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WilliamGUI:
    """Interface gráfica do Assistente William."""

    def __init__(self):
        """Inicializa a interface gráfica."""
        self.engine = None
        self.conversation_history = []

        # Cria janela principal
        self.window = ctk.CTk()
        self.window.title("Assistente IA William")
        self.window.geometry("900x700")

        # Impede que a janela seja redimensionada muito pequena
        self.window.minsize(800, 600)

        self.setup_ui()
        self.initialize_engine()

    def setup_ui(self):
        """Configura a interface do usuário."""

        # ===== HEADER =====
        header_frame = ctk.CTkFrame(self.window, fg_color=("#2b2b2b", "#1a1a1a"))
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🤖 Assistente IA William",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=15)

        self.status_label = ctk.CTkLabel(
            header_frame,
            text="Inicializando...",
            font=ctk.CTkFont(size=12),
            text_color="orange"
        )
        self.status_label.pack(pady=(0, 10))

        # ===== ÁREA DE CHAT =====
        chat_frame = ctk.CTkFrame(self.window)
        chat_frame.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        # Área de mensagens (scrollable)
        self.chat_display = ctk.CTkTextbox(
            chat_frame,
            font=ctk.CTkFont(size=13),
            wrap="word",
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== ÁREA DE INPUT =====
        input_frame = ctk.CTkFrame(self.window)
        input_frame.pack(fill="x", padx=20, pady=20)

        # Campo de texto
        self.input_field = ctk.CTkEntry(
            input_frame,
            placeholder_text="Digite sua mensagem aqui...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(10, 5))
        self.input_field.bind("<Return>", lambda e: self.send_message())

        # Botão enviar
        self.send_button = ctk.CTkButton(
            input_frame,
            text="Enviar",
            command=self.send_message,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=100
        )
        self.send_button.pack(side="right", padx=(5, 10))

        # ===== BOTÕES DE AÇÃO =====
        action_frame = ctk.CTkFrame(self.window)
        action_frame.pack(fill="x", padx=20, pady=(0, 20))

        clear_button = ctk.CTkButton(
            action_frame,
            text="Limpar Chat",
            command=self.clear_chat,
            fg_color="gray",
            hover_color="darkgray",
            width=120
        )
        clear_button.pack(side="left", padx=10, pady=10)

        status_button = ctk.CTkButton(
            action_frame,
            text="Ver Status",
            command=self.show_status,
            fg_color="gray",
            hover_color="darkgray",
            width=120
        )
        status_button.pack(side="left", padx=10, pady=10)

        # Mensagem inicial
        self.add_system_message("Bem-vindo ao Assistente IA William! 🤖")
        self.add_system_message("Digite sua mensagem abaixo e pressione Enter ou clique em Enviar.")

    def initialize_engine(self):
        """Inicializa o motor de IA."""
        def init():
            try:
                self.engine = get_engine()
                status = self.engine.get_status()

                # Atualiza status na UI
                self.window.after(0, lambda: self.status_label.configure(
                    text=f"✓ Online - Provider: {status['default_provider']}",
                    text_color="lightgreen"
                ))

                self.window.after(0, lambda: self.add_system_message(
                    f"Sistema iniciado com sucesso! Usando {status['default_provider'].upper()}"
                ))

                log.info("GUI: Motor IA inicializado com sucesso")

            except Exception as e:
                error_msg = f"Erro ao inicializar: {str(e)}"
                self.window.after(0, lambda: self.status_label.configure(
                    text="✗ Erro na inicialização",
                    text_color="red"
                ))
                self.window.after(0, lambda: self.add_system_message(
                    f"ERRO: {error_msg}\nVerifique o arquivo .env"
                ))
                log.error(f"GUI: {error_msg}")

        # Inicializa em thread separada para não travar a UI
        thread = threading.Thread(target=init, daemon=True)
        thread.start()

    def add_message(self, sender: str, message: str, color: str = None):
        """
        Adiciona mensagem ao chat.

        Args:
            sender: Nome do remetente (Você, William, Sistema)
            message: Conteúdo da mensagem
            color: Cor do texto (opcional)
        """
        self.chat_display.configure(state="normal")

        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")

        # Formata e adiciona mensagem
        if color:
            self.chat_display.insert("end", f"\n[{timestamp}] {sender}:\n", "timestamp")
            self.chat_display.insert("end", f"{message}\n", color)
        else:
            self.chat_display.insert("end", f"\n[{timestamp}] {sender}:\n{message}\n")

        # Configurar tags de cor
        self.chat_display.tag_config("timestamp", foreground="gray")
        self.chat_display.tag_config("user", foreground="lightblue")
        self.chat_display.tag_config("assistant", foreground="lightgreen")
        self.chat_display.tag_config("system", foreground="orange")

        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def add_system_message(self, message: str):
        """Adiciona mensagem do sistema."""
        self.add_message("Sistema", message, "system")

    def send_message(self):
        """Envia mensagem para o assistente."""
        message = self.input_field.get().strip()

        if not message:
            return

        # Limpa campo de input
        self.input_field.delete(0, "end")

        # Adiciona mensagem do usuário
        self.add_message("Você", message, "user")

        # Desabilita botão enquanto processa
        self.send_button.configure(state="disabled", text="Pensando...")

        # Processa em thread separada
        def process():
            try:
                if not self.engine:
                    self.window.after(0, lambda: self.add_system_message(
                        "Motor de IA não está inicializado. Aguarde..."
                    ))
                    return

                # Adiciona ao histórico
                self.conversation_history.append({
                    "role": "user",
                    "content": message
                })

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
                self.window.after(0, lambda: self.add_message("William", response, "assistant"))

            except AIProviderError as e:
                self.window.after(0, lambda: self.add_system_message(f"Erro na IA: {str(e)}"))
            except Exception as e:
                self.window.after(0, lambda: self.add_system_message(f"Erro: {str(e)}"))
                log.error(f"Erro ao processar mensagem: {e}", exc_info=True)
            finally:
                # Reabilita botão
                self.window.after(0, lambda: self.send_button.configure(
                    state="normal",
                    text="Enviar"
                ))

        thread = threading.Thread(target=process, daemon=True)
        thread.start()

    def clear_chat(self):
        """Limpa o histórico de chat."""
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")

        self.conversation_history = []
        self.add_system_message("Chat limpo! Você pode começar uma nova conversa.")

    def show_status(self):
        """Mostra status do sistema."""
        if not self.engine:
            self.add_system_message("Motor de IA não está inicializado.")
            return

        status = self.engine.get_status()
        status_text = f"""Status do Sistema:
- Provider padrão: {status['default_provider']}
- Providers disponíveis: {', '.join(status['providers_available'])}
- Total de providers: {status['total_providers']}
- Status: {status['status']}
- Mensagens na conversa: {len(self.conversation_history)}"""

        self.add_system_message(status_text)

    def run(self):
        """Inicia o loop principal da GUI."""
        log.info("Iniciando GUI...")
        self.window.mainloop()


def main():
    """Ponto de entrada da GUI."""
    app = WilliamGUI()
    app.run()


if __name__ == "__main__":
    main()
