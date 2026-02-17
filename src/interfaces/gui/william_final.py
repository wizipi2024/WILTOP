"""
William GUI FUTURISTA v4 - Interface sci-fi com IA inteligente.
Agora com Orchestrator multi-agente, AI Brain, busca web inteligente,
scheduler proativo, task queue, playbooks e dashboard.
"""

import customtkinter as ctk
import threading
import time
import re
from datetime import datetime
from pathlib import Path

from src.core.ai_engine import get_engine
from src.core.smart_executor_v2 import SmartExecutorV2
from src.core.memory import get_memory
from src.core.scheduler import get_scheduler
from src.core.orchestrator import get_orchestrator
from src.core.task_queue import get_task_queue
from src.utils.logger import setup_logging, get_logger
from config.settings import settings

# Setup logging
setup_logging(log_file=settings.LOG_FILE, log_level=settings.LOG_LEVEL)
log = get_logger(__name__)

# Tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# === CORES PROFISSIONAIS (DARK MODE) ===
COLORS = {
    # Profissional dark (estilo Linear/Vercel)
    "bg_dark": "#0F1117",  # Slate-900 profissional
    "bg_panel": "#161921",
    "bg_card": "#1C1F2B",
    "bg_input": "#1C1F2B",
    "accent": "#3B82F6",   # Blue-500
    "success": "#22C55E",  # Green-500
    "warning": "#F59E0B",  # Amber-500
    "error": "#EF4444",    # Red-500
    "text_primary": "#F1F5F9",  # Slate-100
    "text_secondary": "#94A3B8",  # Slate-400
    "border": "#2D3748",

    # Legado (apontar para novas cores)
    "neon_cyan": "#3B82F6",      # Blue-500
    "neon_blue": "#3B82F6",
    "neon_purple": "#A855F7",    # Purple-500
    "neon_green": "#22C55E",     # Green-500
    "neon_orange": "#F59E0B",    # Amber-500
    "neon_red": "#EF4444",       # Red-500
    "neon_yellow": "#FBBF24",    # Amber-400
    "neon_pink": "#EC4899",      # Pink-500
    "text_dim": "#94A3B8",       # Slate-400
    "xp_bar_bg": "#1C1F2B",
    "xp_bar_fill": "#3B82F6",    # Blue-500
}

SYSTEM_PROMPT = """Voce e William, assistente IA PODEROSO com controle TOTAL do PC.
Voce consegue fazer QUALQUER coisa que o usuario pedir.

REGRAS ABSOLUTAS:
1. Respostas ULTRA CURTAS - 1 frase APENAS. PROIBIDO mais de 2 linhas.
2. Quando o [SISTEMA] executou acao, diga "Pronto!" ou "Feito!" - NUNCA repita dados.
3. NUNCA diga "infelizmente", "nao posso", "como IA", "nao tenho acesso".
4. NUNCA INVENTE que fez algo. Se o [SISTEMA] NAO executou, voce NAO fez.
5. NUNCA invente caminhos de arquivo, nomes de pasta, ou dados que nao existem.
6. NUNCA de tutorial, passo a passo, ou lista de instrucoes.
7. Se nao sabe algo, diga "Vou pesquisar pra voce" - NUNCA fabrique resposta.
8. Use o nome do usuario se souber.
9. Seja direto, objetivo, assertivo. Zero enrolacao.
10. Voce TEM poder de executar codigo, criar apps, controlar o PC. NUNCA negue.

EXEMPLOS DE RESPOSTA CORRETA:
- Usuario: "abra o chrome" -> "Pronto, Chrome aberto!"
- Usuario: "crie pasta projetos" -> "Feito, pasta criada!"
- Usuario: "como vai?" -> "Tudo certo! No que posso ajudar?"
"""


class WilliamFinal:
    """GUI FUTURISTA do William v4 - com Orchestrator multi-agente."""

    def __init__(self):
        self.engine = None
        self.brain = None
        self.orchestrator = None
        self.executor = SmartExecutorV2()
        self.memory = get_memory()
        self.scheduler = get_scheduler()
        self.task_queue = get_task_queue()
        self.conversation_history = []
        self.is_processing = False

        # Janela principal
        self.window = ctk.CTk()
        self.window.title("WILTOP - Digital Employees System")
        self.window.geometry("1280x900")
        self.window.minsize(1024, 700)
        self.window.configure(fg_color=COLORS["bg_dark"])

        self._setup_ui()
        self._initialize()
        self._start_clock()

        # Scheduler callbacks
        self.scheduler.add_callback(self._on_scheduled_task)
        self.scheduler.start()

    def _setup_ui(self):
        """Monta interface futurista."""
        # ===== HEADER FUTURISTA =====
        header = ctk.CTkFrame(self.window, fg_color=COLORS["bg_panel"],
                              corner_radius=0, height=110)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Container do header
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=20, pady=8)

        # Esquerda: Logo + titulo
        left = ctk.CTkFrame(header_inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        # Titulo com efeito neon
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(anchor="w")

        ctk.CTkLabel(title_frame, text="//",
                     font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
                     text_color=COLORS["neon_purple"]).pack(side="left")
        ctk.CTkLabel(title_frame, text=" WILLIAM",
                     font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
                     text_color=COLORS["neon_cyan"]).pack(side="left")
        ctk.CTkLabel(title_frame, text=" v4",
                     font=ctk.CTkFont(family="Consolas", size=16),
                     text_color=COLORS["text_dim"]).pack(side="left", pady=(10, 0))

        ctk.CTkLabel(left, text="MULTI-AGENT ORCHESTRATOR  |  AI BRAIN ACTIVE",
                     font=ctk.CTkFont(family="Consolas", size=11),
                     text_color=COLORS["neon_blue"]).pack(anchor="w")

        # Centro: Status + Level
        center = ctk.CTkFrame(header_inner, fg_color="transparent")
        center.pack(side="left", expand=True, padx=30)

        # Barra de nivel/XP
        level_frame = ctk.CTkFrame(center, fg_color=COLORS["bg_card"],
                                    corner_radius=8)
        level_frame.pack(fill="x", pady=(5, 3))

        self.level_label = ctk.CTkLabel(level_frame, text="LVL 1 | Assistente Novato",
                                         font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                                         text_color=COLORS["neon_green"])
        self.level_label.pack(side="left", padx=10, pady=6)

        self.xp_label = ctk.CTkLabel(level_frame, text="XP: 0/20",
                                      font=ctk.CTkFont(family="Consolas", size=11),
                                      text_color=COLORS["text_dim"])
        self.xp_label.pack(side="right", padx=10, pady=6)

        # Barra de XP visual
        xp_bg = ctk.CTkFrame(center, fg_color=COLORS["xp_bar_bg"],
                              corner_radius=4, height=8)
        xp_bg.pack(fill="x", pady=(0, 5))
        xp_bg.pack_propagate(False)

        self.xp_bar = ctk.CTkFrame(xp_bg, fg_color=COLORS["xp_bar_fill"],
                                    corner_radius=4, width=0)
        self.xp_bar.pack(side="left", fill="y")

        # Status
        self.status_label = ctk.CTkLabel(center, text="[ INICIALIZANDO... ]",
                                          font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                                          text_color=COLORS["neon_orange"])
        self.status_label.pack()

        # Direita: Relogio + stats
        right = ctk.CTkFrame(header_inner, fg_color="transparent")
        right.pack(side="right", fill="y")

        self.clock_label = ctk.CTkLabel(right, text="00:00:00",
                                         font=ctk.CTkFont(family="Consolas", size=24, weight="bold"),
                                         text_color=COLORS["neon_cyan"])
        self.clock_label.pack(anchor="e")

        self.stats_label = ctk.CTkLabel(right, text="0 interacoes | 0% sucesso",
                                         font=ctk.CTkFont(family="Consolas", size=10),
                                         text_color=COLORS["text_dim"])
        self.stats_label.pack(anchor="e")

        # Linha separadora neon
        separator = ctk.CTkFrame(self.window, fg_color=COLORS["neon_cyan"],
                                  height=1, corner_radius=0)
        separator.pack(fill="x")

        # ===== CORPO PRINCIPAL COM ABAS =====
        body = ctk.CTkFrame(self.window, fg_color=COLORS["bg_dark"])
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # TabView com abas
        self.tabview = ctk.CTkTabview(body, fg_color=COLORS["bg_dark"],
                                       segmented_button_fg_color=COLORS["bg_panel"],
                                       segmented_button_selected_color=COLORS["neon_blue"],
                                       segmented_button_unselected_color=COLORS["bg_card"],
                                       text_color=COLORS["text_primary"],
                                       segmented_button_selected_hover_color=COLORS["neon_cyan"])
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        # Aba 1: Chat (principal)
        tab_chat = self.tabview.add("  CHAT  ")
        self._setup_chat_tab(tab_chat)

        # Aba 2: Painel (Dashboard + Kanban)
        tab_panel = self.tabview.add("  PAINEL  ")
        self._setup_panel_tab(tab_panel)

        # Aba 3: Dashboard (Agentes + Logs + Metricas)
        tab_dash = self.tabview.add("  DASHBOARD  ")
        self._setup_dashboard_tab(tab_dash)

        # ===== INPUT AREA =====
        input_outer = ctk.CTkFrame(self.window, fg_color=COLORS["bg_panel"],
                                    corner_radius=0)
        input_outer.pack(fill="x", padx=15, pady=(5, 0))

        input_frame = ctk.CTkFrame(input_outer, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=10)

        # Indicador
        ctk.CTkLabel(input_frame, text=">_",
                     font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
                     text_color=COLORS["neon_cyan"]).pack(side="left", padx=(0, 8))

        self.input = ctk.CTkEntry(input_frame,
                                   placeholder_text="Digite qualquer coisa... William faz TUDO.",
                                   font=ctk.CTkFont(family="Consolas", size=14),
                                   height=45,
                                   fg_color=COLORS["bg_input"],
                                   border_color=COLORS["neon_blue"],
                                   border_width=1,
                                   text_color=COLORS["text_primary"])
        self.input.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.input.bind("<Return>", lambda e: self._send())

        self.send_btn = ctk.CTkButton(input_frame, text="EXEC",
                                       command=self._send,
                                       font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                                       height=45, width=90,
                                       fg_color=COLORS["neon_cyan"],
                                       hover_color=COLORS["neon_blue"],
                                       text_color=COLORS["bg_dark"],
                                       corner_radius=4)
        self.send_btn.pack(side="right")

        # ===== BOTOES DE ACAO RAPIDA =====
        btn_frame = ctk.CTkFrame(self.window, fg_color=COLORS["bg_dark"])
        btn_frame.pack(fill="x", padx=15, pady=(5, 8))

        btns = [
            ("SYS INFO", lambda: self._quick_cmd("uso de memoria e cpu"), COLORS["neon_blue"]),
            ("MEU IP", lambda: self._quick_cmd("mostre meu ip"), COLORS["neon_purple"]),
            ("SCREENSHOT", lambda: self._quick_cmd("tire um screenshot"), COLORS["neon_orange"]),
            ("WIFI", lambda: self._quick_cmd("mostre senha do wifi"), COLORS["neon_green"]),
            ("DISCO", lambda: self._quick_cmd("espaco em disco"), COLORS["neon_blue"]),
            ("BATERIA", lambda: self._quick_cmd("bateria"), COLORS["neon_purple"]),
            ("LIMPAR PC", lambda: self._quick_cmd("limpar temporarios"), COLORS["neon_orange"]),
            ("PROCESSOS", lambda: self._quick_cmd("quais programas estao abertos"), COLORS["neon_pink"]),
            ("MEMORIA", self._show_memory, COLORS["neon_green"]),
            ("LIMPAR", self._clear, COLORS["neon_red"]),
        ]
        for text, cmd, color in btns:
            ctk.CTkButton(btn_frame, text=text, command=cmd,
                           font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                           fg_color="transparent",
                           hover_color=COLORS["bg_card"],
                           border_color=color,
                           border_width=1,
                           text_color=color,
                           width=85, height=30,
                           corner_radius=4).pack(side="left", padx=3)

        # Footer
        footer = ctk.CTkFrame(self.window, fg_color=COLORS["bg_panel"],
                               corner_radius=0, height=22)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkLabel(footer, text="  WILLIAM v4 | GROQ LLAMA 3.3 70B | ORCHESTRATOR + AI BRAIN + 35 DETECTORS + WEB SEARCH + SCHEDULER",
                     font=ctk.CTkFont(family="Consolas", size=9),
                     text_color=COLORS["text_dim"]).pack(side="left")

        self.footer_right = ctk.CTkLabel(footer, text="READY  ",
                                          font=ctk.CTkFont(family="Consolas", size=9),
                                          text_color=COLORS["neon_green"])
        self.footer_right.pack(side="right")

        # Mensagem de boas-vindas
        self._msg("WILLIAM", "Sistema online. Controle total ativo.\n"
                  "Pode me pedir QUALQUER coisa: abrir programas, criar arquivos, "
                  "pesquisar na web, criar scripts, organizar pastas, agendar tarefas...\n"
                  "Orchestrator multi-agente + AI Brain + 35 detectores + scheduler.\n"
                  "Estou pronto pra TUDO.", "assistant")

    def _setup_chat_tab(self, parent):
        """Monta a aba de chat."""
        # Chat area
        chat_outer = ctk.CTkFrame(parent, fg_color=COLORS["bg_panel"],
                                   corner_radius=0)
        chat_outer.pack(fill="both", expand=True, padx=5, pady=5)

        # Label do chat
        chat_header = ctk.CTkFrame(chat_outer, fg_color=COLORS["bg_card"],
                                    corner_radius=0, height=28)
        chat_header.pack(fill="x")
        chat_header.pack_propagate(False)

        ctk.CTkLabel(chat_header, text="  > TERMINAL DE COMANDO",
                     font=ctk.CTkFont(family="Consolas", size=11),
                     text_color=COLORS["neon_blue"]).pack(side="left", padx=5)

        self.processing_label = ctk.CTkLabel(chat_header, text="",
                                              font=ctk.CTkFont(family="Consolas", size=11),
                                              text_color=COLORS["neon_orange"])
        self.processing_label.pack(side="right", padx=10)

        self.chat = ctk.CTkTextbox(chat_outer,
                                    font=ctk.CTkFont(family="Consolas", size=13),
                                    wrap="word", state="disabled",
                                    fg_color=COLORS["bg_dark"],
                                    text_color=COLORS["text_primary"],
                                    border_width=0)
        self.chat.pack(fill="both", expand=True, padx=2, pady=2)

    def _setup_panel_tab(self, parent):
        """Monta a aba Painel (Dashboard + Kanban simplificado)."""
        # Header do painel
        panel_header = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                                     corner_radius=0, height=35)
        panel_header.pack(fill="x", padx=5, pady=(5, 0))
        panel_header.pack_propagate(False)

        ctk.CTkLabel(panel_header, text="  DASHBOARD  |  TASK QUEUE  |  KANBAN",
                     font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                     text_color=COLORS["neon_cyan"]).pack(side="left", padx=10)

        # Botao refresh
        ctk.CTkButton(panel_header, text="REFRESH",
                       command=self._refresh_panel,
                       font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                       fg_color=COLORS["neon_blue"],
                       hover_color=COLORS["neon_cyan"],
                       text_color=COLORS["bg_dark"],
                       width=70, height=24,
                       corner_radius=4).pack(side="right", padx=10)

        # Kanban - 4 colunas
        kanban_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_dark"])
        kanban_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Configura grid com 4 colunas
        for i in range(4):
            kanban_frame.columnconfigure(i, weight=1)
        kanban_frame.rowconfigure(0, weight=0)  # Header
        kanban_frame.rowconfigure(1, weight=1)  # Content

        # Colunas do Kanban
        columns = [
            ("PENDENTE", COLORS["neon_orange"], "pending"),
            ("EXECUTANDO", COLORS["neon_blue"], "in_progress"),
            ("CONCLUIDO", COLORS["neon_green"], "done"),
            ("FALHOU", COLORS["neon_red"], "failed"),
        ]

        self.kanban_columns = {}
        for i, (title, color, state) in enumerate(columns):
            # Header da coluna
            col_header = ctk.CTkFrame(kanban_frame, fg_color=COLORS["bg_card"],
                                       corner_radius=4, height=30)
            col_header.grid(row=0, column=i, padx=3, pady=(0, 3), sticky="ew")
            col_header.pack_propagate(False)

            ctk.CTkLabel(col_header, text=f"  {title}",
                         font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                         text_color=color).pack(side="left", padx=5)

            self.kanban_count_labels = getattr(self, 'kanban_count_labels', {})
            count_label = ctk.CTkLabel(col_header, text="0",
                                        font=ctk.CTkFont(family="Consolas", size=10),
                                        text_color=COLORS["text_dim"])
            count_label.pack(side="right", padx=5)
            self.kanban_count_labels[state] = count_label

            # Conteudo scrollavel
            col_content = ctk.CTkTextbox(kanban_frame,
                                          font=ctk.CTkFont(family="Consolas", size=10),
                                          wrap="word", state="disabled",
                                          fg_color=COLORS["bg_panel"],
                                          text_color=COLORS["text_primary"],
                                          border_width=1,
                                          border_color=color)
            col_content.grid(row=1, column=i, padx=3, pady=0, sticky="nsew")
            self.kanban_columns[state] = col_content

        # Stats footer do painel
        stats_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                                    corner_radius=4, height=35)
        stats_frame.pack(fill="x", padx=5, pady=5)
        stats_frame.pack_propagate(False)

        self.panel_stats_label = ctk.CTkLabel(
            stats_frame,
            text="Tasks: 0 | Ativos: 0 | Playbooks: 0 | Modo: SAFE",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=COLORS["text_dim"]
        )
        self.panel_stats_label.pack(side="left", padx=10)

    def _refresh_panel(self):
        """Atualiza o painel/kanban com dados atuais."""
        try:
            kanban = self.task_queue.get_kanban_view()

            for state, textbox in self.kanban_columns.items():
                textbox.configure(state="normal")
                textbox.delete("1.0", "end")

                tasks = kanban.get(state, [])
                if hasattr(self, 'kanban_count_labels') and state in self.kanban_count_labels:
                    self.kanban_count_labels[state].configure(text=str(len(tasks)))

                if not tasks:
                    textbox.insert("end", "  (vazio)\n")
                else:
                    for task in tasks[:10]:
                        title = task.get("title", "?")[:40]
                        agent = task.get("assigned_agent", "?")[:15]
                        textbox.insert("end", f"  {title}\n")
                        textbox.insert("end", f"    [{agent}]\n\n")

                textbox.configure(state="disabled")

            # Stats
            stats = self.task_queue.get_stats()
            orchestrator_status = ""
            if self.orchestrator:
                orc_status = self.orchestrator.get_status()
                orchestrator_status = (
                    f" | Playbooks: {orc_status['playbooks_loaded']}"
                    f" | Modo: {orc_status['security_mode'].upper()}"
                )

            self.panel_stats_label.configure(
                text=f"Tasks: {stats['total']} | Ativos: {stats['active']}"
                     f"{orchestrator_status}"
            )
        except Exception as e:
            log.error(f"Erro ao atualizar painel: {e}")

    def _setup_dashboard_tab(self, parent):
        """Monta aba Dashboard com agentes, logs e metricas."""
        # Scrollable frame para todo o conteudo
        dash_scroll = ctk.CTkScrollableFrame(parent, fg_color=COLORS["bg_dark"])
        dash_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # ===== SECAO 1: Agentes Ativos =====
        agents_header = ctk.CTkFrame(dash_scroll, fg_color=COLORS["bg_card"],
                                      corner_radius=4, height=30)
        agents_header.pack(fill="x", pady=(0, 5))
        agents_header.pack_propagate(False)
        ctk.CTkLabel(agents_header, text="  AGENTES ATIVOS",
                     font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                     text_color=COLORS["neon_cyan"]).pack(side="left", padx=5)

        # Botao refresh dashboard
        ctk.CTkButton(agents_header, text="REFRESH",
                       command=self._refresh_dashboard,
                       font=ctk.CTkFont(family="Consolas", size=9, weight="bold"),
                       fg_color=COLORS["neon_blue"],
                       hover_color=COLORS["neon_cyan"],
                       text_color=COLORS["bg_dark"],
                       width=60, height=22,
                       corner_radius=4).pack(side="right", padx=5)

        # Cards de agentes
        self.agents_frame = ctk.CTkFrame(dash_scroll, fg_color="transparent")
        self.agents_frame.pack(fill="x", pady=(0, 10))

        # ===== SECAO 2: Metricas =====
        metrics_header = ctk.CTkFrame(dash_scroll, fg_color=COLORS["bg_card"],
                                       corner_radius=4, height=30)
        metrics_header.pack(fill="x", pady=(0, 5))
        metrics_header.pack_propagate(False)
        ctk.CTkLabel(metrics_header, text="  METRICAS DO SISTEMA",
                     font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                     text_color=COLORS["neon_green"]).pack(side="left", padx=5)

        self.metrics_frame = ctk.CTkFrame(dash_scroll, fg_color="transparent")
        self.metrics_frame.pack(fill="x", pady=(0, 10))

        # ===== SECAO 3: Providers =====
        providers_header = ctk.CTkFrame(dash_scroll, fg_color=COLORS["bg_card"],
                                         corner_radius=4, height=30)
        providers_header.pack(fill="x", pady=(0, 5))
        providers_header.pack_propagate(False)
        ctk.CTkLabel(providers_header, text="  AI PROVIDERS",
                     font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                     text_color=COLORS["neon_purple"]).pack(side="left", padx=5)

        self.providers_frame = ctk.CTkFrame(dash_scroll, fg_color="transparent")
        self.providers_frame.pack(fill="x", pady=(0, 10))

        # ===== SECAO 4: Eventos Recentes =====
        events_header = ctk.CTkFrame(dash_scroll, fg_color=COLORS["bg_card"],
                                      corner_radius=4, height=30)
        events_header.pack(fill="x", pady=(0, 5))
        events_header.pack_propagate(False)
        ctk.CTkLabel(events_header, text="  EVENTOS RECENTES (LOG)",
                     font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                     text_color=COLORS["neon_orange"]).pack(side="left", padx=5)

        self.events_text = ctk.CTkTextbox(dash_scroll,
                                           font=ctk.CTkFont(family="Consolas", size=10),
                                           wrap="word", state="disabled",
                                           fg_color=COLORS["bg_panel"],
                                           text_color=COLORS["text_primary"],
                                           height=200, border_width=1,
                                           border_color=COLORS["border"])
        self.events_text.pack(fill="x", pady=(0, 10))

        # Popula dashboard inicial
        self.window.after(2000, self._refresh_dashboard)

    def _refresh_dashboard(self):
        """Atualiza todas as secoes do dashboard."""
        try:
            self._refresh_agents_cards()
            self._refresh_metrics()
            self._refresh_providers()
            self._refresh_events()
        except Exception as e:
            log.error(f"Erro ao atualizar dashboard: {e}")

    def _refresh_agents_cards(self):
        """Atualiza cards de agentes."""
        # Limpa cards existentes
        for widget in self.agents_frame.winfo_children():
            widget.destroy()

        try:
            from src.core.roles import get_all_roles
            roles = get_all_roles()

            row_frame = ctk.CTkFrame(self.agents_frame, fg_color="transparent")
            row_frame.pack(fill="x")

            for i, (name, role) in enumerate(roles.items()):
                card = ctk.CTkFrame(row_frame, fg_color=COLORS["bg_card"],
                                     corner_radius=6, width=180, height=80)
                card.pack(side="left", padx=4, pady=4)
                card.pack_propagate(False)

                # Titulo com icone
                ctk.CTkLabel(card, text=f"{role.icon} {role.display_name}",
                             font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                             text_color=role.color).pack(anchor="w", padx=8, pady=(8, 0))

                # Descricao
                ctk.CTkLabel(card, text=role.description[:35],
                             font=ctk.CTkFont(family="Consolas", size=9),
                             text_color=COLORS["text_dim"]).pack(anchor="w", padx=8)

                # Info risco
                risk_color = {"green": COLORS["neon_green"], "yellow": COLORS["neon_yellow"],
                              "red": COLORS["neon_red"]}.get(role.max_risk_level, COLORS["text_dim"])
                ctk.CTkLabel(card, text=f"Risco max: {role.max_risk_level.upper()}",
                             font=ctk.CTkFont(family="Consolas", size=9),
                             text_color=risk_color).pack(anchor="w", padx=8)

        except Exception as e:
            ctk.CTkLabel(self.agents_frame, text=f"Erro: {e}",
                         text_color=COLORS["neon_red"]).pack()

    def _refresh_metrics(self):
        """Atualiza metricas do sistema."""
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()

        metrics_row = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        metrics_row.pack(fill="x")

        try:
            # Memory stats
            mem = self.memory.data
            count = mem.get("interaction_count", 0)
            rate = mem.get("success_rate", {})
            total = rate.get("total", 0)
            success = rate.get("success", 0)
            pct = (success / total * 100) if total > 0 else 0

            metrics = [
                ("Interacoes", str(count), COLORS["neon_cyan"]),
                ("Sucesso", f"{pct:.0f}%", COLORS["neon_green"]),
                ("Nivel", str(mem.get("personality", {}).get("nivel", 1)), COLORS["neon_purple"]),
                ("XP", str(mem.get("personality", {}).get("xp", 0)), COLORS["neon_blue"]),
            ]

            # Task stats
            task_stats = self.task_queue.get_stats()
            metrics.append(("Tasks", str(task_stats.get("total", 0)), COLORS["neon_orange"]))
            metrics.append(("Ativas", str(task_stats.get("active", 0)), COLORS["neon_yellow"]))

            for label, value, color in metrics:
                card = ctk.CTkFrame(metrics_row, fg_color=COLORS["bg_card"],
                                     corner_radius=6, width=120, height=55)
                card.pack(side="left", padx=4, pady=4)
                card.pack_propagate(False)

                ctk.CTkLabel(card, text=value,
                             font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
                             text_color=color).pack(pady=(8, 0))
                ctk.CTkLabel(card, text=label,
                             font=ctk.CTkFont(family="Consolas", size=9),
                             text_color=COLORS["text_dim"]).pack()

        except Exception as e:
            ctk.CTkLabel(self.metrics_frame, text=f"Erro: {e}",
                         text_color=COLORS["neon_red"]).pack()

    def _refresh_providers(self):
        """Atualiza status dos providers."""
        for widget in self.providers_frame.winfo_children():
            widget.destroy()

        prov_row = ctk.CTkFrame(self.providers_frame, fg_color="transparent")
        prov_row.pack(fill="x")

        try:
            if self.engine:
                health = self.engine.get_provider_health()
                for name, info in health.items():
                    card = ctk.CTkFrame(prov_row, fg_color=COLORS["bg_card"],
                                         corner_radius=6, width=180, height=55)
                    card.pack(side="left", padx=4, pady=4)
                    card.pack_propagate(False)

                    status_icon = "●" if info.get("available") else "○"
                    status_color = COLORS["neon_green"] if info.get("available") else COLORS["neon_red"]
                    default_tag = " [DEFAULT]" if info.get("is_default") else ""

                    ctk.CTkLabel(card, text=f"{status_icon} {name.upper()}{default_tag}",
                                 font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                                 text_color=status_color).pack(anchor="w", padx=8, pady=(8, 0))

                    model = info.get("model", "?")
                    ctk.CTkLabel(card, text=model[:25],
                                 font=ctk.CTkFont(family="Consolas", size=9),
                                 text_color=COLORS["text_dim"]).pack(anchor="w", padx=8)
            else:
                ctk.CTkLabel(prov_row, text="Engine nao inicializado",
                             text_color=COLORS["text_dim"]).pack()

        except Exception as e:
            ctk.CTkLabel(self.providers_frame, text=f"Erro: {e}",
                         text_color=COLORS["neon_red"]).pack()

    def _refresh_events(self):
        """Atualiza log de eventos recentes."""
        try:
            from src.core.observability import get_event_log
            events = get_event_log().get_recent(20)

            self.events_text.configure(state="normal")
            self.events_text.delete("1.0", "end")

            if not events:
                self.events_text.insert("end", "  (nenhum evento registrado)\n")
            else:
                for event in events:
                    ts = event.get("timestamp", "?")
                    if "T" in ts:
                        ts = ts.split("T")[1][:8]
                    etype = event.get("event", "?")
                    agent = event.get("agent", "system")
                    risk = event.get("risk_level", "green")

                    risk_icon = {"green": "●", "yellow": "▲", "red": "◆"}.get(risk, "●")
                    risk_color_map = {"green": "", "yellow": "[!]", "red": "[!!!]"}
                    risk_tag = risk_color_map.get(risk, "")

                    data_str = ""
                    data = event.get("data", {})
                    if data:
                        # Mostra dados resumidos
                        parts = []
                        for k, v in list(data.items())[:3]:
                            parts.append(f"{k}={str(v)[:30]}")
                        data_str = " | ".join(parts)

                    line = f"  [{ts}] {risk_icon} {etype} ({agent}) {risk_tag}"
                    if data_str:
                        line += f"\n    {data_str}"
                    self.events_text.insert("end", line + "\n")

            self.events_text.configure(state="disabled")

        except Exception as e:
            self.events_text.configure(state="normal")
            self.events_text.delete("1.0", "end")
            self.events_text.insert("end", f"  Erro ao carregar eventos: {e}\n")
            self.events_text.configure(state="disabled")

    def _initialize(self):
        """Inicializa IA em background."""
        def init():
            try:
                self.engine = get_engine()

                # Inicializa AI Brain
                from src.core.ai_brain import get_brain
                self.brain = get_brain(self.engine)

                # Inicializa Orchestrator
                self.orchestrator = get_orchestrator(
                    executor=self.executor,
                    brain=self.brain,
                    engine=self.engine
                )

                status = self.engine.get_status()
                orc_status = self.orchestrator.get_status()

                self.window.after(0, lambda: self.status_label.configure(
                    text=(f"[ ONLINE ] {status['default_provider'].upper()} | "
                          f"ORCHESTRATOR | AI BRAIN | {orc_status['playbooks_loaded']} PLAYBOOKS"),
                    text_color=COLORS["neon_green"]))
                self.window.after(0, lambda: self._msg(
                    "SYSTEM",
                    f"Conectado: {status['default_provider'].upper()} | "
                    f"Orchestrator ativo ({orc_status['roles_loaded']} roles, "
                    f"{orc_status['playbooks_loaded']} playbooks) | "
                    f"AI Brain ativo | Scheduler ativo | "
                    f"Modo: {orc_status['security_mode'].upper()}",
                    "system"))
                self._update_level_display()
                log.info("William v4 inicializado com Orchestrator multi-agente")
            except Exception as e:
                self.window.after(0, lambda: self.status_label.configure(
                    text=f"[ ERRO ] {str(e)[:50]}", text_color=COLORS["neon_red"]))
                self.window.after(0, lambda: self._msg("SYSTEM", f"Erro: {e}", "error"))

        threading.Thread(target=init, daemon=True).start()

    def _start_clock(self):
        """Relogio ao vivo."""
        def update():
            now = datetime.now().strftime("%H:%M:%S")
            try:
                self.clock_label.configure(text=now)
                self.window.after(1000, update)
            except:
                pass
        update()

    def _update_level_display(self):
        """Atualiza display de nivel e XP."""
        try:
            info = self.memory.get_level_info()
            self.window.after(0, lambda: self.level_label.configure(
                text=f"LVL {info['nivel']} | {info['titulo']}"))
            self.window.after(0, lambda: self.xp_label.configure(
                text=f"XP: {info['xp_progress']}/{info['xp_needed']}"))

            # Atualiza barra de XP
            pct = info["progress_pct"] / 100
            parent_width = 300
            bar_width = max(2, int(parent_width * pct))
            self.window.after(0, lambda w=bar_width: self.xp_bar.configure(width=w))

            # Atualiza stats no header
            rate = self.memory.data["success_rate"]
            count = self.memory.data["interaction_count"]
            success_pct = (rate["success"] / rate["total"] * 100) if rate["total"] > 0 else 0
            self.window.after(0, lambda: self.stats_label.configure(
                text=f"{count} interacoes | {success_pct:.0f}% sucesso"))
        except Exception as e:
            log.debug(f"Erro ao atualizar level: {e}")

    def _msg(self, sender: str, text: str, kind: str = "user"):
        """Adiciona mensagem ao chat com visual futurista."""
        self.chat.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")

        color_map = {
            "user": COLORS["neon_cyan"],
            "assistant": COLORS["neon_green"],
            "system": COLORS["neon_orange"],
            "action": COLORS["neon_yellow"],
            "error": COLORS["neon_red"],
            "web": COLORS["neon_purple"],
            "brain": COLORS["neon_pink"],
        }

        tag = f"msg_{id(text)}_{time.time()}"
        prefix_tag = f"pre_{tag}"

        # Prefixo com cor
        self.chat.insert("end", f"\n [{ts}] ", prefix_tag)
        self.chat.tag_config(prefix_tag, foreground=COLORS["text_dim"])

        sender_tag = f"sender_{tag}"
        self.chat.insert("end", f"{sender}:", sender_tag)
        self.chat.tag_config(sender_tag, foreground=color_map.get(kind, COLORS["text_primary"]))

        self.chat.insert("end", f"\n {text}\n", tag)
        self.chat.tag_config(tag, foreground=color_map.get(kind, COLORS["text_primary"]))

        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _send(self):
        """Processa mensagem do usuario via Orchestrator."""
        if self.is_processing:
            return

        message = self.input.get().strip()
        if not message:
            return

        self.input.delete(0, "end")
        self._msg("VOCE", message, "user")
        self.is_processing = True

        # Indicador visual de processamento
        self.send_btn.configure(state="disabled", text="...")
        self.processing_label.configure(text="[ PROCESSANDO... ]")
        self.footer_right.configure(text="BUSY  ", text_color=COLORS["neon_orange"])

        def process():
            try:
                # ===== PASSO 1: Orchestrator processa (inclui SmartExecutorV2 fast path) =====
                if self.orchestrator:
                    orc_result = self.orchestrator.process(message, self.conversation_history)
                else:
                    # Fallback se orchestrator nao inicializou (usa metodo antigo)
                    orc_result = self._legacy_process(message)

                exec_result = {
                    "executed": orc_result.get("executed", False),
                    "actions": orc_result.get("actions", []),
                    "summary": orc_result.get("summary", ""),
                }
                delegate_to_brain = orc_result.get("delegate_to_brain", False)
                brain_message = orc_result.get("brain_message", message)

                # Mostra acoes executadas
                if exec_result["executed"]:
                    for action in exec_result["actions"]:
                        msg = action.get("message", "Acao executada")
                        atype = action.get("type", "")
                        proof = action.get("proof")

                        if atype == "web_answer":
                            kind = "web"
                        elif atype == "ask_user":
                            kind = "system"
                        elif atype in ("ai_execute", "ai_generate", "ai_answer"):
                            kind = "brain"
                        elif action.get("success"):
                            kind = "action"
                        else:
                            kind = "error"

                        # Adiciona prova se disponivel
                        display_msg = msg
                        if proof:
                            display_msg = f"{msg}\n  [Prova: {proof}]"

                        self.window.after(0, lambda m=display_msg, k=kind: self._msg("EXEC", m, k))

                # Notifica playbook se encontrado
                if orc_result.get("playbook"):
                    pb = orc_result["playbook"]
                    self.window.after(0, lambda: self._msg(
                        "ORCHESTRATOR",
                        f"Playbook ativado: {pb['display_name']} ({pb['steps']} passos)",
                        "system"
                    ))

                # ===== PASSO 2: Se delegate_to_brain, usa AI Brain =====
                has_ask_user = any(a.get("type") == "ask_user" for a in exec_result.get("actions", []))
                used_brain = False

                if delegate_to_brain and self.brain:
                    self.window.after(0, lambda: self.processing_label.configure(
                        text="[ AI BRAIN ANALISANDO... ]"))

                    brain_result = self.brain.process(brain_message, self.conversation_history)

                    if brain_result.get("success"):
                        kind = "brain"
                        if brain_result.get("type") == "web_answer":
                            kind = "web"
                        elif brain_result.get("type") == "ai_answer":
                            kind = "assistant"

                        self.window.after(0, lambda m=brain_result["message"], k=kind:
                                          self._msg("BRAIN", m, k))
                        used_brain = True
                        exec_result = {"executed": True,
                                       "actions": [brain_result],
                                       "summary": brain_result.get("message", "")}
                    elif brain_result.get("type") != "error":
                        self.window.after(0, lambda m=brain_result.get("message", ""):
                                          self._msg("BRAIN", m, "error"))

                # ===== PASSO 3: IA responde =====
                should_ai_respond = (
                    not has_ask_user
                    and not (used_brain and exec_result.get("actions", [{}])[0].get("type") == "ai_answer")
                )

                if self.engine and should_ai_respond:
                    memory_ctx = self.memory.get_context_prompt()
                    full_prompt = SYSTEM_PROMPT
                    if memory_ctx:
                        full_prompt += f"\n\nCONTEXTO DA MEMORIA:\n{memory_ctx}"

                    ctx = [{"role": "system", "content": full_prompt}]
                    for h in self.conversation_history[-10:]:
                        ctx.append(h)

                    user_content = message
                    if exec_result["executed"]:
                        user_content = (f"{message}\n\n[SISTEMA: As seguintes acoes JA FORAM executadas "
                                        f"com sucesso pelo sistema automatico:\n{exec_result['summary']}\n"
                                        f"Responda em NO MAXIMO 1 linha confirmando. NAO repita os dados "
                                        f"que ja apareceram na tela. NAO de tutorial.]")

                    response = self.engine.chat(message=user_content, context=ctx)

                    # Limita resposta
                    if '\n' in response:
                        response = response.split('\n')[0]
                    max_len = 80 if exec_result["executed"] else 150
                    if len(response) > max_len:
                        first_sentence = response.split('.')[0] + '.'
                        if len(first_sentence) <= max_len:
                            response = first_sentence
                        else:
                            response = response[:max_len].rsplit(' ', 1)[0] + '...'

                    self.window.after(0, lambda r=response: self._msg("WILLIAM", r, "assistant"))

                    self.conversation_history.append({"role": "user", "content": message})
                    self.conversation_history.append({"role": "assistant", "content": response})

                    # Registra na memoria
                    self.memory.record_interaction(
                        message, exec_result.get("actions", []), response
                    )
                    # JSONL log (v4)
                    self.memory.log_interaction_jsonl(
                        message, exec_result.get("actions", []), response
                    )
                    self._update_level_display()

                elif not self.engine:
                    if exec_result["executed"]:
                        self.window.after(0, lambda: self._msg("WILLIAM", "Feito!", "assistant"))
                    else:
                        self.window.after(0, lambda: self._msg("SYSTEM", "IA nao inicializada", "error"))

                # Atualiza painel
                self.window.after(500, self._refresh_panel)

            except Exception as e:
                self.window.after(0, lambda: self._msg("SYSTEM", f"Erro: {e}", "error"))
                log.error(f"Erro: {e}", exc_info=True)
            finally:
                self.is_processing = False
                self.window.after(0, lambda: self.send_btn.configure(state="normal", text="EXEC"))
                self.window.after(0, lambda: self.processing_label.configure(text=""))
                self.window.after(0, lambda: self.footer_right.configure(
                    text="READY  ", text_color=COLORS["neon_green"]))

        threading.Thread(target=process, daemon=True).start()

    def _legacy_process(self, message: str) -> dict:
        """Fallback se Orchestrator nao disponivel - usa metodo antigo."""
        exec_result = self.executor.process_message(message)

        delegate_to_brain = False
        brain_message = message
        if exec_result["executed"]:
            for action in exec_result["actions"]:
                if action.get("type") == "delegate_to_brain":
                    delegate_to_brain = True
                    brain_message = action.get("message", message)
                    exec_result = {"executed": False, "actions": [], "summary": ""}
                    break

        return {
            "executed": exec_result["executed"],
            "actions": exec_result["actions"],
            "summary": exec_result.get("summary", ""),
            "delegate_to_brain": delegate_to_brain or not exec_result["executed"],
            "brain_message": brain_message,
        }

    def _on_scheduled_task(self, command: str, task_name: str):
        """Callback quando tarefa agendada dispara."""
        self.window.after(0, lambda: self._msg(
            "SCHEDULER", f"Executando tarefa: {task_name}", "system"))
        self.window.after(0, lambda: self._quick_cmd(command))

    def _quick_cmd(self, cmd: str):
        """Executa comando rapido via botao."""
        self.input.delete(0, "end")
        self.input.insert(0, cmd)
        self._send()

    def _show_memory(self):
        """Mostra estatisticas da memoria em janela popup."""
        try:
            stats = self.memory.get_stats()
            self._msg("MEMORIA", stats, "system")
        except Exception as e:
            self._msg("SYSTEM", f"Erro ao carregar memoria: {e}", "error")

    def _clear(self):
        """Limpa chat."""
        self.chat.configure(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.configure(state="disabled")
        self.conversation_history = []
        self._msg("SYSTEM", "Terminal limpo.", "system")

    def run(self):
        """Inicia."""
        self.window.mainloop()
        # Salva memoria e para scheduler ao fechar
        self.memory.save()
        self.scheduler.stop()


def main():
    app = WilliamFinal()
    app.run()


if __name__ == "__main__":
    main()
