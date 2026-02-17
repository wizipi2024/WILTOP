"""
Interface GUI MELHORADA do Assistente IA William.
Versão com executor inteligente integrado.
"""

import customtkinter as ctk
import threading
from datetime import datetime
from pathlib import Path

from src.core.ai_engine import get_engine
from src.core.smart_executor import get_smart_executor
from src.utils.logger import setup_logging, get_logger
from src.utils.exceptions import AIProviderError
from config.settings import settings

# Setup logging
setup_logging(log_file=settings.LOG_FILE, log_level=settings.LOG_LEVEL)
log = get_logger(__name__)

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class EnhancedWilliamGUI:
    """Interface gráfica MELHORADA do Assistente William."""

    def __init__(self):
        """Inicializa a interface gráfica."""
        self.engine = None
        self.executor = None
        self.conversation_history = []
        self.authorized = False

        # Cria janela principal
        self.window = ctk.CTk()
        self.window.title("Assistente IA William - Versão Completa")
        self.window.geometry("1000x750")
        self.window.minsize(900, 650)

        self.setup_ui()
        self.initialize()

    def setup_ui(self):
        """Configura a interface do usuário."""

        # ===== HEADER =====
        header_frame = ctk.CTkFrame(self.window, fg_color=("#2b2b2b", "#1a1a1a"))
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame,
            text="*** Assistente IA William - MODO COMPLETO ***",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=12)

        self.status_label = ctk.CTkLabel(
            header_frame,
            text="Inicializando...",
            font=ctk.CTkFont(size=12),
            text_color="orange"
        )
        self.status_label.pack(pady=(0, 5))

        self.auth_label = ctk.CTkLabel(
            header_frame,
            text="Verificando autorizacao...",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.auth_label.pack(pady=(0, 10))

        # ===== ÁREA DE CHAT =====
        chat_frame = ctk.CTkFrame(self.window)
        chat_frame.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        self.chat_display = ctk.CTkTextbox(
            chat_frame,
            font=ctk.CTkFont(size=13),
            wrap="word",
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== ÁREA DE INPUT =====
        input_frame = ctk.CTkFrame(self.window)
        input_frame.pack(fill="x", padx=20, pady=15)

        self.input_field = ctk.CTkEntry(
            input_frame,
            placeholder_text="Digite sua mensagem ou comando...",
            font=ctk.CTkFont(size=14),
            height=45
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(10, 5))
        self.input_field.bind("<Return>", lambda e: self.send_message())

        self.send_button = ctk.CTkButton(
            input_frame,
            text="Enviar",
            command=self.send_message,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            width=110
        )
        self.send_button.pack(side="right", padx=(5, 10))

        # ===== BOTÕES DE AÇÃO =====
        action_frame = ctk.CTkFrame(self.window)
        action_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkButton(
            action_frame,
            text="Limpar Chat",
            command=self.clear_chat,
            fg_color="gray",
            hover_color="darkgray",
            width=100
        ).pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            action_frame,
            text="Status",
            command=self.show_status,
            fg_color="gray",
            hover_color="darkgray",
            width=100
        ).pack(side="left", padx=8, pady=8)

        ctk.CTkButton(
            action_frame,
            text="Capacidades",
            command=self.show_capabilities,
            fg_color="gray",
            hover_color="darkgray",
            width=120
        ).pack(side="left", padx=8, pady=8)

        # Mensagem inicial
        self.add_system_message("Bem-vindo ao Assistente IA William - Versao Completa!")
        self.add_system_message("Inicializando sistemas...")

    def initialize(self):
        """Inicializa os sistemas."""
        def init():
            try:
                # Inicializa motor IA
                self.engine = get_engine()
                status = self.engine.get_status()

                # Verifica autorizacao PRIMEIRO
                auth_file = Path(__file__).parent.parent.parent / ".authorized"
                self.authorized = auth_file.exists()
                log.info(f"Verificacao de autorizacao: arquivo existe = {self.authorized}")

                # Inicializa executor JA AUTORIZADO
                self.executor = get_smart_executor(authorized=self.authorized)
                log.info(f"Executor criado com authorized={self.authorized}")

                # FORÇA autorização se arquivo existe
                if self.authorized:
                    self.executor.authorized = True
                    self.executor.system.authorized = True
                    log.info("FORCADO: executor.authorized = True e system.authorized = True")

                # Atualiza UI
                self.window.after(0, lambda: self.status_label.configure(
                    text=f"[OK] Online - Provider: {status['default_provider']}",
                    text_color="lightgreen"
                ))

                if self.authorized:
                    self.window.after(0, lambda: self.auth_label.configure(
                        text="[OK] SISTEMA AUTORIZADO - Controle Total Ativo",
                        text_color="lightgreen"
                    ))
                    self.window.after(0, lambda: self.add_system_message(
                        "*** MODO COMPLETO ATIVADO ***\nO William tem acesso total ao sistema!"
                    ))
                else:
                    self.window.after(0, lambda: self.auth_label.configure(
                        text="[!] Modo Conversa - Execute AUTORIZAR_TUDO.py para modo completo",
                        text_color="yellow"
                    ))
                    self.window.after(0, lambda: self.add_system_message(
                        "Modo conversa ativado. Para poderes totais, execute AUTORIZAR_TUDO.py"
                    ))

                self.window.after(0, lambda: self.add_system_message(
                    f"Sistema iniciado! Usando {status['default_provider'].upper()}"
                ))

                log.info(f"GUI Enhanced: Inicializado (autorizado: {self.authorized})")

            except Exception as e:
                error_msg = f"Erro: {str(e)}"
                self.window.after(0, lambda: self.status_label.configure(
                    text="[ERRO] Falha na inicializacao",
                    text_color="red"
                ))
                self.window.after(0, lambda: self.add_system_message(f"ERRO: {error_msg}"))
                log.error(f"GUI Enhanced: {error_msg}")

        threading.Thread(target=init, daemon=True).start()

    def add_message(self, sender: str, message: str, color: str = None):
        """Adiciona mensagem ao chat."""
        self.chat_display.configure(state="normal")

        timestamp = datetime.now().strftime("%H:%M")

        if color:
            self.chat_display.insert("end", f"\n[{timestamp}] {sender}:\n", "timestamp")
            self.chat_display.insert("end", f"{message}\n", color)
        else:
            self.chat_display.insert("end", f"\n[{timestamp}] {sender}:\n{message}\n")

        self.chat_display.tag_config("timestamp", foreground="gray")
        self.chat_display.tag_config("user", foreground="lightblue")
        self.chat_display.tag_config("assistant", foreground="lightgreen")
        self.chat_display.tag_config("system", foreground="orange")
        self.chat_display.tag_config("action", foreground="yellow")

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

        self.input_field.delete(0, "end")
        self.add_message("Voce", message, "user")
        self.send_button.configure(state="disabled", text="Pensando...")

        def process():
            try:
                if not self.engine:
                    self.window.after(0, lambda: self.add_system_message(
                        "Motor de IA nao esta inicializado."
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

                # Se autorizado, tenta executar ações
                if self.authorized and self.executor:
                    result = self.executor.interpret_and_execute(message, response)

                    if result.get("executed"):
                        # Mostra resposta melhorada
                        final_response = result.get("enhanced_response", response)
                        self.window.after(0, lambda: self.add_message(
                            "William", final_response, "assistant"
                        ))

                        # Mostra ações executadas
                        for action in result.get("actions", []):
                            if action.get("success"):
                                self.window.after(0, lambda a=action: self.add_message(
                                    "ACAO", a.get("message", "Acao executada"), "action"
                                ))
                    else:
                        self.window.after(0, lambda: self.add_message("William", response, "assistant"))
                else:
                    self.window.after(0, lambda: self.add_message("William", response, "assistant"))

                # Adiciona resposta ao histórico
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                self.window.after(0, lambda: self.add_system_message(f"Erro: {str(e)}"))
                log.error(f"Erro ao processar: {e}", exc_info=True)
            finally:
                self.window.after(0, lambda: self.send_button.configure(
                    state="normal", text="Enviar"
                ))

        threading.Thread(target=process, daemon=True).start()

    def clear_chat(self):
        """Limpa o histórico de chat."""
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        self.conversation_history = []
        self.add_system_message("Chat limpo!")

    def show_status(self):
        """Mostra status do sistema."""
        if not self.engine:
            self.add_system_message("Motor de IA nao inicializado.")
            return

        status = self.engine.get_status()
        status_text = f"""Status do Sistema:
- Provider: {status['default_provider']}
- Providers disponiveis: {', '.join(status['providers_available'])}
- Total de providers: {status['total_providers']}
- Status: {status['status']}
- Mensagens: {len(self.conversation_history)}
- Autorizado: {'SIM - Controle Total' if self.authorized else 'NAO - Apenas Conversa'}"""

        self.add_system_message(status_text)

    def show_capabilities(self):
        """Mostra capacidades do sistema."""
        if self.authorized:
            caps = """Capacidades Ativas (MODO COMPLETO):
[OK] Executar comandos do Windows
[OK] Criar/ler/modificar/deletar arquivos
[OK] Abrir e fechar programas
[OK] Gerenciar processos
[OK] Acessar informacoes do sistema
[OK] Navegar pelo sistema de arquivos
[OK] E MUITO MAIS!

Exemplos de comandos:
- "Abra o bloco de notas"
- "Crie um arquivo teste.txt na area de trabalho"
- "Liste arquivos da pasta Downloads"
- "Mostre uso de memoria"
- "Execute o comando dir"
"""
        else:
            caps = """Capacidades Ativas (MODO CONVERSA):
[OK] Conversar e responder perguntas
[OK] Explicar conceitos
[OK] Ajudar com codigo
[OK] Dar conselhos

[!] Para ativar CONTROLE TOTAL:
1. Execute: AUTORIZAR_TUDO.py
2. Digite: SIM AUTORIZO TUDO
3. Reinicie o William
"""

        self.add_system_message(caps)

    def run(self):
        """Inicia o loop principal da GUI."""
        log.info("Iniciando GUI Enhanced...")
        self.window.mainloop()


def main():
    """Ponto de entrada da GUI."""
    app = EnhancedWilliamGUI()
    app.run()


if __name__ == "__main__":
    main()
