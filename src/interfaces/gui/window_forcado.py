"""
Interface GUI FORCADA - COM AUTORIZACAO GARANTIDA
"""

import customtkinter as ctk
import threading
from datetime import datetime
from pathlib import Path

from src.core.ai_engine import get_engine
from src.core.smart_executor import SmartExecutor  # Import direto!
from src.utils.logger import setup_logging, get_logger
from config.settings import settings

# Setup logging
setup_logging(log_file=settings.LOG_FILE, log_level=settings.LOG_LEVEL)
log = get_logger(__name__)

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WilliamGUIForcado:
    """Interface gráfica com autorização FORÇADA."""

    def __init__(self):
        """Inicializa a interface gráfica."""
        self.engine = None
        self.executor = None
        self.conversation_history = []
        self.authorized = False
        self.system_prompt = self._load_system_prompt()

        # Cria janela principal
        self.window = ctk.CTk()
        self.window.title("William - Assistente IA Completo [MODO FORCADO]")
        self.window.geometry("1000x750")
        self.window.minsize(900, 650)

        self.setup_ui()
        self.initialize()

    def _load_system_prompt(self) -> str:
        """Carrega o system prompt forçado."""
        try:
            prompt_file = Path(__file__).parent.parent.parent / "config" / "system_prompt_forcado.txt"
            if prompt_file.exists():
                return prompt_file.read_text(encoding='utf-8')
            return ""
        except:
            return ""

    def setup_ui(self):
        """Configura a interface do usuário."""

        # ===== HEADER =====
        header_frame = ctk.CTkFrame(self.window, fg_color=("#2b2b2b", "#1a1a1a"))
        header_frame.pack(fill="x", padx=0, pady=0)

        title_label = ctk.CTkLabel(
            header_frame,
            text="*** WILLIAM - ASSISTENTE IA COMPLETO ***",
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

        # Mensagem inicial
        self.add_system_message("Bem-vindo ao William - Modo Forcado!")
        self.add_system_message("Inicializando sistemas...")

    def initialize(self):
        """Inicializa os sistemas COM AUTORIZACAO FORCADA."""
        def init():
            try:
                # FORÇA CAMINHO ABSOLUTO
                import os
                projeto_root = Path(r"C:\Users\wizip\Desktop\WILTOP")
                auth_file = projeto_root / ".authorized"

                # SEMPRE TRUE se arquivo existe
                self.authorized = auth_file.exists()

                log.info(f"===== INICIALIZACAO FORCADA =====")
                log.info(f"Arquivo .authorized: {auth_file}")
                log.info(f"Existe: {self.authorized}")

                # FORÇA TRUE se arquivo existe
                if auth_file.exists():
                    self.authorized = True
                    log.info("FORCANDO authorized = True (arquivo existe!)")

                # Inicializa motor IA
                self.engine = get_engine()
                status = self.engine.get_status()

                # CRIA EXECUTOR DIRETAMENTE (sem singleton!)
                if self.authorized:
                    log.info("Criando SmartExecutor DIRETO com authorized=True")
                    self.executor = SmartExecutor(authorized=True)
                    log.info(f"Executor criado: authorized={self.executor.authorized}")
                    log.info(f"System autorizado: {self.executor.system.authorized}")
                else:
                    log.warning("Arquivo .authorized NAO existe!")
                    self.executor = SmartExecutor(authorized=False)

                # Atualiza UI
                self.window.after(0, lambda: self.status_label.configure(
                    text=f"[OK] Online - Provider: {status['default_provider']}",
                    text_color="lightgreen"
                ))

                if self.authorized:
                    self.window.after(0, lambda: self.auth_label.configure(
                        text="[OK] SISTEMA AUTORIZADO - Controle Total Ativo [FORCADO]",
                        text_color="lightgreen"
                    ))
                    self.window.after(0, lambda: self.add_system_message(
                        "*** MODO COMPLETO ATIVADO (FORCADO) ***\nO William tem acesso total ao sistema!"
                    ))
                else:
                    self.window.after(0, lambda: self.auth_label.configure(
                        text="[!] NAO AUTORIZADO - Execute AUTORIZAR_TUDO.py",
                        text_color="yellow"
                    ))

                self.window.after(0, lambda: self.add_system_message(
                    f"Sistema iniciado! Usando {status['default_provider'].upper()}"
                ))

                log.info(f"GUI Forcado: Inicializado (autorizado: {self.authorized})")

            except Exception as e:
                error_msg = f"Erro: {str(e)}"
                self.window.after(0, lambda: self.status_label.configure(
                    text="[ERRO] Falha na inicializacao",
                    text_color="red"
                ))
                self.window.after(0, lambda: self.add_system_message(f"ERRO: {error_msg}"))
                log.error(f"GUI Forcado: {error_msg}", exc_info=True)

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

                # Prepara contexto COM system prompt
                context_with_system = []
                if self.system_prompt and self.authorized:
                    # Adiciona system prompt no início
                    context_with_system.append({
                        "role": "system",
                        "content": self.system_prompt
                    })

                # Adiciona histórico anterior
                if len(self.conversation_history) > 1:
                    context_with_system.extend(self.conversation_history[:-1])

                # Processa com IA
                response = self.engine.chat(
                    message=message,
                    context=context_with_system if context_with_system else None
                )

                # Se autorizado, tenta executar ações
                if self.authorized and self.executor:
                    log.info("===== TENTANDO EXECUTAR ACOES =====")
                    log.info(f"self.authorized: {self.authorized}")
                    log.info(f"self.executor.authorized: {self.executor.authorized}")

                    result = self.executor.interpret_and_execute(message, response)

                    log.info(f"Resultado executed: {result.get('executed')}")
                    log.info(f"Total de acoes: {len(result.get('actions', []))}")

                    if result.get("executed"):
                        # Mostra resposta melhorada
                        final_response = result.get("enhanced_response", response)
                        self.window.after(0, lambda r=final_response: self.add_message(
                            "William", r, "assistant"
                        ))

                        # Mostra ações executadas
                        for action in result.get("actions", []):
                            if action.get("success"):
                                msg = action.get("message", "Acao executada")
                                self.window.after(0, lambda m=msg: self.add_message(
                                    "ACAO", m, "action"
                                ))
                    else:
                        self.window.after(0, lambda r=response: self.add_message("William", r, "assistant"))
                else:
                    log.warning(f"NAO executou acoes. authorized={self.authorized}, executor={self.executor is not None}")
                    self.window.after(0, lambda r=response: self.add_message("William", r, "assistant"))

                # Adiciona resposta ao histórico
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                error_msg = f"Erro: {str(e)}"
                self.window.after(0, lambda: self.add_system_message(error_msg))
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

    def run(self):
        """Inicia o loop principal da GUI."""
        log.info("Iniciando GUI Forcado...")
        self.window.mainloop()


def main():
    """Ponto de entrada da GUI."""
    app = WilliamGUIForcado()
    app.run()


if __name__ == "__main__":
    main()
