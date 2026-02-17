"""
Smart Executor V2 - EXECUTA TUDO!
Detecta intencoes e executa ANTES da IA responder.
Versao COMPLETA com 20+ tipos de acao.
"""

import re
import os
import subprocess
import psutil
import webbrowser
import platform
import socket
import time
import threading
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from src.utils.logger import get_logger

log = get_logger(__name__)


class SmartExecutorV2:
    """Executor inteligente V2 - detecta e executa TUDO."""

    APPS = {
        "bloco de notas": "notepad.exe", "notepad": "notepad.exe", "notas": "notepad.exe",
        "calculadora": "calc.exe", "calc": "calc.exe",
        "chrome": "chrome", "google chrome": "chrome", "navegador": "chrome",
        "browser": "chrome", "internet": "chrome",
        "edge": "msedge", "firefox": "firefox", "opera": "opera", "brave": "brave",
        "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
        "ppt": "powerpnt", "outlook": "outlook",
        "explorador": "explorer", "explorer": "explorer",
        "cmd": "cmd", "terminal": "cmd", "prompt": "cmd", "powershell": "powershell",
        "paint": "mspaint", "configuracoes": "ms-settings:", "config": "ms-settings:",
        "painel de controle": "control", "gerenciador de tarefas": "taskmgr",
        "task manager": "taskmgr", "gerenciador": "taskmgr",
        "spotify": "spotify", "musica": "spotify", "vlc": "vlc",
        "media player": "wmplayer",
        "discord": "discord", "telegram": "telegram", "whatsapp": "whatsapp",
        "teams": "teams", "skype": "skype", "zoom": "zoom",
        "vscode": "code", "visual studio code": "code", "vs code": "code",
        "steam": "steam", "epic": "EpicGamesLauncher",
        "obs": "obs64", "obs studio": "obs64",
        "fotos": "ms-photos:", "photos": "ms-photos:",
        "loja": "ms-windows-store:", "store": "ms-windows-store:",
        "relogio": "ms-clock:", "alarmes": "ms-clock:",
        "camera": "microsoft.windows.camera:",
        "mapas": "bingmaps:",
        "gravador": "soundrecorder:",
        "lixeira": "shell:RecycleBinFolder",
    }

    FOLDERS = {
        "area de trabalho": "Desktop", "desktop": "Desktop", "trabalho": "Desktop",
        "documentos": "Documents", "documents": "Documents", "meus documentos": "Documents",
        "downloads": "Downloads", "download": "Downloads",
        "imagens": "Pictures", "pictures": "Pictures", "fotos": "Pictures",
        "videos": "Videos", "musicas": "Music", "music": "Music",
    }

    # NOTA: usar nomes EXATOS e longos para evitar falsos positivos
    SITES = {
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "twitter": "https://www.twitter.com",
        "tiktok": "https://www.tiktok.com",
        "whatsapp web": "https://web.whatsapp.com",
        "github": "https://www.github.com",
        "reddit": "https://www.reddit.com",
        "amazon": "https://www.amazon.com.br",
        "mercado livre": "https://www.mercadolivre.com.br",
        "netflix": "https://www.netflix.com",
        "twitch": "https://www.twitch.tv",
        "linkedin": "https://www.linkedin.com",
        "chatgpt": "https://chat.openai.com",
        "spotify web": "https://open.spotify.com",
        "google drive": "https://drive.google.com",
        "google maps": "https://maps.google.com",
        "tradutor": "https://translate.google.com",
        "google translate": "https://translate.google.com",
        "notion": "https://www.notion.so",
        "canva": "https://www.canva.com",
        "figma": "https://www.figma.com",
        "stackoverflow": "https://stackoverflow.com",
    }

    def __init__(self):
        self.user_home = str(Path.home())
        self.timers = []
        self._pending_search_query = None  # Guarda query pendente para "abrir no google"
        log.info("SmartExecutorV2 inicializado")

    def process_message(self, message: str) -> Dict[str, Any]:
        """Processa mensagem - executa PRIMEIRO detector que match e PARA."""
        msg = message.lower().strip()
        results = []

        # ORDEM IMPORTA! Primeiro match ganha (evita conflitos)
        detectors = [
            self._try_confirm_open_browser,  # "sim" / "abra" -> abre busca pendente
            self._try_date_time,           # "que horas" -> rapido, sem efeito colateral
            self._try_process_list,        # "programas abertos" -> ANTES de system_info!
            self._try_search_local_file,   # "procure no meu pc" -> busca LOCAL
            self._try_create_folder,       # "crie uma pasta" -> pasta (ANTES de create_file!)
            self._try_organize_folder,     # "organize minha pasta" -> organizar
            self._try_create_script,       # "crie um script/app/codigo" -> codigo
            self._try_open_folder,         # "abra a pasta X" -> ANTES de open_app!
            self._try_open_app,            # "abra o chrome" -> programa
            self._try_close_app,           # "feche o chrome" -> fechar
            self._try_open_site,           # "abra youtube" -> site
            self._try_screenshot,          # "tire print" -> antes de knowledge!
            self._try_volume,              # "aumente volume" -> antes de knowledge!
            self._try_wifi_info,           # "senha wifi" -> antes de knowledge!
            self._try_system_info,         # "quanta ram" -> antes de knowledge!
            self._try_disk_space,          # "espaco disco" -> antes de knowledge!
            self._try_battery,             # "bateria" -> antes de knowledge!
            self._try_network_info,        # "meu ip" -> antes de knowledge!
            self._try_knowledge_question,  # "como esta o tempo", "noticias" -> web answer
            self._try_search_web,          # "pesquise X" -> google
            self._try_create_file_with_content,
            self._try_create_file,
            self._try_delete_file,
            self._try_read_file,
            self._try_rename_file,
            self._try_move_copy_file,
            self._try_list_files,
            self._try_clipboard,
            self._try_timer,
            self._try_cleanup,
            self._try_startup_apps,
            self._try_installed_programs,
            self._try_open_file_smart,      # "abra este arquivo" -> abre com programa adequado
            self._try_install_program,      # "instale X" -> baixa e instala
            self._try_schedule_task,        # "agende", "lembre-me" -> scheduler
            self._try_list_scheduled,       # "minhas tarefas agendadas"
            self._try_direct_command,
            self._try_power_action,
        ]

        for detector in detectors:
            try:
                result = detector(msg)
                if result:
                    results.append(result)
                    break  # PARA no primeiro match! Evita conflitos
            except Exception as e:
                log.error(f"Erro em {detector.__name__}: {e}")

        if results:
            return {
                "executed": True,
                "actions": results,
                "summary": "\n".join(
                    r.get("message", "") for r in results if r.get("success")
                )
            }
        return {"executed": False, "actions": [], "summary": ""}

    # =====================================================================
    # CONFIRMACAO PARA ABRIR NAVEGADOR (resposta a ask_user)
    # =====================================================================
    def _try_confirm_open_browser(self, msg: str) -> Optional[Dict]:
        """Quando usuario responde 'sim' a pergunta de abrir navegador."""
        if not self._pending_search_query:
            return None

        confirm_words = ["sim", "abra", "abre", "pode abrir", "abrir", "yes",
                         "ok", "vai", "pode", "manda", "manda ver"]
        deny_words = ["nao", "no", "cancela", "cancele", "deixa", "esquece",
                      "esqueca", "nope", "nah"]

        # So responde a mensagens curtas (confirmacao)
        if len(msg) > 30:
            return None

        if any(w == msg or msg.startswith(w) for w in confirm_words):
            query = self._pending_search_query
            self._pending_search_query = None  # Limpa
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return {"success": True, "type": "search",
                    "message": f"[OK] Pesquisa aberta no Google: '{query}'"}

        if any(w == msg or msg.startswith(w) for w in deny_words):
            self._pending_search_query = None  # Limpa
            return {"success": True, "type": "info",
                    "message": "[OK] Tudo bem, cancelado!"}

        return None

    # =====================================================================
    # BUSCAR ARQUIVO LOCAL NO PC
    # =====================================================================
    def _try_search_local_file(self, msg: str) -> Optional[Dict]:
        """Busca arquivo no PC local. Prioridade sobre pesquisa web."""
        local_words = ["procure no meu pc", "procure no pc", "procure no computador",
                       "procurar no pc", "buscar no pc", "busque no pc",
                       "encontre no pc", "encontrar no pc", "achar no pc",
                       "onde esta o arquivo", "onde esta", "localizar",
                       "localizar arquivo", "buscar arquivo", "encontrar arquivo",
                       "procure o arquivo", "procurar arquivo", "ache o arquivo",
                       "procure no meu computador", "existe o arquivo",
                       "tem o arquivo", "cadê o arquivo", "cade"]

        if not any(w in msg for w in local_words):
            return None

        # Extrai nome do arquivo
        patterns = [
            r'(?:arquivo|chamado|nome)\s+([a-zA-Z0-9_. -]+\.\w+)',
            r'([a-zA-Z0-9_.-]+\.txt)',
            r'([a-zA-Z0-9_.-]+\.pdf)',
            r'([a-zA-Z0-9_.-]+\.docx?)',
            r'([a-zA-Z0-9_.-]+\.xlsx?)',
            r'([a-zA-Z0-9_.-]+\.py)',
            r'([a-zA-Z0-9_.-]+\.jpg)',
            r'([a-zA-Z0-9_.-]+\.png)',
            r'([a-zA-Z0-9_.-]+\.mp[34])',
            r'([a-zA-Z0-9_.-]+\.\w{1,5})',
        ]

        filename = None
        for p in patterns:
            m = re.search(p, msg)
            if m:
                filename = m.group(1)
                break

        if not filename:
            # Tenta extrair qualquer palavra após "arquivo"
            m = re.search(r'(?:arquivo|chamado)\s+([a-zA-Z0-9_. -]+)', msg)
            if m:
                filename = m.group(1).strip()

        if not filename:
            return None

        # Busca em pastas comuns (NAO busca em user_home inteiro - muito lento)
        search_dirs = [
            os.path.join(self.user_home, "Desktop"),
            os.path.join(self.user_home, "Documents"),
            os.path.join(self.user_home, "Downloads"),
            os.path.join(self.user_home, "Pictures"),
            os.path.join(self.user_home, "Videos"),
            os.path.join(self.user_home, "Music"),
        ]

        found = []
        start_time = time.time()
        for dir_path in search_dirs:
            # Timeout de 10 segundos total para busca
            if time.time() - start_time > 10:
                break
            try:
                p = Path(dir_path)
                if not p.exists():
                    continue
                for item in p.rglob(f"*{filename}*"):
                    # Pula pastas de sistema/ocultas
                    if any(part.startswith('.') or part.startswith('__') for part in item.parts):
                        continue
                    found.append(str(item))
                    if len(found) >= 20:
                        break
                    if time.time() - start_time > 10:
                        break
            except (PermissionError, OSError):
                continue
            if len(found) >= 20:
                break

        if found:
            lines = [f"  {f}" for f in found[:15]]
            return {"success": True, "type": "search_local",
                    "message": f"[OK] Encontrei {len(found)} resultado(s) para '{filename}':\n" + "\n".join(lines)}
        else:
            return {"success": True, "type": "search_local",
                    "message": f"[OK] Nenhum arquivo '{filename}' encontrado nas pastas do usuario."}

    # =====================================================================
    # CRIAR PASTA
    # =====================================================================
    def _try_create_folder(self, msg: str) -> Optional[Dict]:
        """Cria uma pasta/diretorio."""
        if not any(w in msg for w in ["crie uma pasta", "criar pasta", "cria pasta",
                                       "crie a pasta", "nova pasta", "criar diretorio",
                                       "faca uma pasta", "faz uma pasta",
                                       "crie pasta", "criar uma pasta"]):
            return None

        # Extrai nome da pasta - aceita pontos NO NOME (ex: AGORAFOI.TUDO)
        m = re.search(r'(?:pasta|diretorio|folder)\s+(?:chamad[ao]\s+)?(?:com\s+(?:o\s+)?nome\s+)?([a-zA-Z0-9_._ -]+)', msg)
        if not m:
            return None

        folder_name = m.group(1).strip()
        # Remove palavras residuais do comando
        for remove in ["no desktop", "no documentos", "no downloads", "na area de trabalho",
                       "com o nome", "chamada", "chamado"]:
            folder_name = folder_name.replace(remove, "").strip()
        if not folder_name or len(folder_name) < 1:
            return None

        # Onde criar? Default = Desktop
        base = os.path.join(self.user_home, "Desktop")
        for name, folder in self.FOLDERS.items():
            if name in msg and name != folder_name.lower():
                base = os.path.join(self.user_home, folder)
                break

        full_path = os.path.join(base, folder_name)
        try:
            Path(full_path).mkdir(parents=True, exist_ok=True)
            return {"success": True, "type": "create_folder",
                    "message": f"[OK] Pasta criada: {full_path}"}
        except Exception as e:
            return {"success": False, "type": "create_folder",
                    "message": f"[ERRO] Nao consegui criar pasta: {e}"}

    # =====================================================================
    # ORGANIZAR PASTA
    # =====================================================================
    def _try_organize_folder(self, msg: str) -> Optional[Dict]:
        """Organiza arquivos de uma pasta por tipo."""
        if not any(w in msg for w in ["organize", "organizar", "organiza",
                                       "arrume", "arrumar", "arruma",
                                       "separe", "separar", "separa"]):
            return None

        if not any(w in msg for w in ["pasta", "arquivos", "downloads", "desktop",
                                       "documentos", "area de trabalho"]):
            return None

        # Qual pasta organizar?
        target = os.path.join(self.user_home, "Downloads")  # default
        for name, folder in self.FOLDERS.items():
            if name in msg:
                target = os.path.join(self.user_home, folder)
                break

        # Categorias de organizacao
        categories = {
            "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
            "Documentos": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".csv", ".rtf", ".odt"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "Musicas": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
            "Programas": [".exe", ".msi", ".deb", ".dmg", ".app"],
            "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Codigo": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json", ".xml"],
        }

        try:
            p = Path(target)
            if not p.exists():
                return {"success": False, "type": "organize",
                        "message": f"[ERRO] Pasta nao existe: {target}"}

            moved = {}
            for item in p.iterdir():
                if item.is_dir():
                    continue
                ext = item.suffix.lower()
                for cat_name, extensions in categories.items():
                    if ext in extensions:
                        cat_path = p / cat_name
                        cat_path.mkdir(exist_ok=True)
                        try:
                            new_path = cat_path / item.name
                            if not new_path.exists():
                                item.rename(new_path)
                                moved[cat_name] = moved.get(cat_name, 0) + 1
                        except:
                            pass
                        break

            if moved:
                details = "\n".join(f"  {k}: {v} arquivo(s)" for k, v in moved.items())
                total = sum(moved.values())
                return {"success": True, "type": "organize",
                        "message": f"[OK] Pasta organizada! {total} arquivos movidos:\n{details}"}
            else:
                return {"success": True, "type": "organize",
                        "message": f"[OK] Pasta ja esta organizada ou sem arquivos para mover."}
        except Exception as e:
            return {"success": False, "type": "organize",
                    "message": f"[ERRO] Erro ao organizar: {e}"}

    # =====================================================================
    # CRIAR SCRIPT / CODIGO / APP
    # =====================================================================
    def _try_create_script(self, msg: str) -> Optional[Dict]:
        """Cria scripts/codigos. Templates basicos ou delega ao AI Brain."""
        if not any(w in msg for w in ["crie um app", "crie um programa", "crie um script",
                                       "crie um codigo", "faca um app", "faca um programa",
                                       "faca um script", "faca um codigo",
                                       "criar um app", "criar um programa",
                                       "cria um app", "cria um programa",
                                       "crie uma calculadora", "crie um jogo",
                                       "faz um app", "faz um programa",
                                       "gere um codigo", "gere um script",
                                       "desenvolva", "programe", "construa"]):
            return None

        # Se e um pedido complexo (mais de 5 palavras alem do comando), delega ao AI Brain
        # Isto garante que pedidos como "jogo de corrida 3d estilo mario kart" vao pro Brain
        simple_keywords = ["calculadora", "calc", "lista de tarefas", "todo", "to-do"]
        is_simple = any(w in msg for w in simple_keywords)

        if not is_simple:
            # DELEGA ao AI Brain - ele gera codigo sob medida
            return {"success": True, "type": "delegate_to_brain",
                    "message": msg}

        # Templates simples (rapidos, sem precisar da IA)
        if any(w in msg for w in ["calculadora", "calc"]):
            code = '''import tkinter as tk

def click(val):
    if val == "=":
        try:
            result = str(eval(entry.get()))
            entry.delete(0, tk.END)
            entry.insert(tk.END, result)
        except:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "Erro")
    elif val == "C":
        entry.delete(0, tk.END)
    else:
        entry.insert(tk.END, val)

root = tk.Tk()
root.title("Calculadora")
root.configure(bg="#1a1a2e")

entry = tk.Entry(root, font=("Consolas", 20), bg="#16213e", fg="white",
                 insertbackground="white", justify="right", bd=0)
entry.grid(row=0, column=0, columnspan=4, sticky="we", padx=5, pady=5, ipady=10)

buttons = [
    "7","8","9","/",
    "4","5","6","*",
    "1","2","3","-",
    "C","0","=","+",
]
for i, b in enumerate(buttons):
    row, col = 1 + i // 4, i % 4
    color = "#0f3460" if b.isdigit() or b == "." else "#e94560"
    tk.Button(root, text=b, font=("Consolas", 16), bg=color, fg="white",
              activebackground="#533483", bd=0, width=5, height=2,
              command=lambda v=b: click(v)).grid(row=row, column=col, padx=2, pady=2)

root.mainloop()
'''
            filename = "calculadora.py"
        elif any(w in msg for w in ["jogo", "game"]):
            code = '''import tkinter as tk
import random

root = tk.Tk()
root.title("Jogo da Adivinhacao")
root.configure(bg="#1a1a2e")

number = random.randint(1, 100)
attempts = 0

def guess():
    global attempts, number
    try:
        n = int(entry.get())
        attempts += 1
        entry.delete(0, tk.END)
        if n < number:
            label.config(text=f"Tentativa {attempts}: Muito baixo! Tente mais alto.")
        elif n > number:
            label.config(text=f"Tentativa {attempts}: Muito alto! Tente mais baixo.")
        else:
            label.config(text=f"Parabens! Acertou em {attempts} tentativas!", fg="#00ff88")
    except:
        label.config(text="Digite um numero valido!")

def reset():
    global number, attempts
    number = random.randint(1, 100)
    attempts = 0
    label.config(text="Adivinhe o numero de 1 a 100!", fg="white")

tk.Label(root, text="Jogo da Adivinhacao", font=("Consolas", 18, "bold"),
         bg="#1a1a2e", fg="#00f5ff").pack(pady=10)

label = tk.Label(root, text="Adivinhe o numero de 1 a 100!",
                 font=("Consolas", 12), bg="#1a1a2e", fg="white")
label.pack(pady=5)

entry = tk.Entry(root, font=("Consolas", 16), bg="#16213e", fg="white",
                 insertbackground="white", justify="center")
entry.pack(pady=5)
entry.bind("<Return>", lambda e: guess())

tk.Button(root, text="Adivinhar", font=("Consolas", 12), bg="#e94560",
          fg="white", command=guess).pack(pady=5)
tk.Button(root, text="Novo Jogo", font=("Consolas", 10), bg="#0f3460",
          fg="white", command=reset).pack(pady=3)

root.mainloop()
'''
            filename = "jogo_adivinhacao.py"
        elif any(w in msg for w in ["lista de tarefas", "todo", "to-do"]):
            code = '''import tkinter as tk

root = tk.Tk()
root.title("Lista de Tarefas")
root.configure(bg="#1a1a2e")

tasks = []

def add_task():
    task = entry.get().strip()
    if task:
        listbox.insert(tk.END, task)
        tasks.append(task)
        entry.delete(0, tk.END)

def remove_task():
    sel = listbox.curselection()
    if sel:
        listbox.delete(sel[0])
        tasks.pop(sel[0])

tk.Label(root, text="Lista de Tarefas", font=("Consolas", 16, "bold"),
         bg="#1a1a2e", fg="#00f5ff").pack(pady=8)

frame = tk.Frame(root, bg="#1a1a2e")
frame.pack(padx=10, fill="x")

entry = tk.Entry(frame, font=("Consolas", 13), bg="#16213e", fg="white",
                 insertbackground="white")
entry.pack(side="left", fill="x", expand=True, padx=(0,5))
entry.bind("<Return>", lambda e: add_task())

tk.Button(frame, text="+", font=("Consolas", 13, "bold"), bg="#00ff88",
          fg="black", command=add_task, width=3).pack(side="right")

listbox = tk.Listbox(root, font=("Consolas", 12), bg="#16213e", fg="white",
                     selectbackground="#e94560", height=12)
listbox.pack(padx=10, pady=5, fill="both", expand=True)

tk.Button(root, text="Remover Selecionado", font=("Consolas", 11),
          bg="#e94560", fg="white", command=remove_task).pack(pady=5)

root.mainloop()
'''
            filename = "todo_list.py"
        else:
            # Se chegou aqui e nao e simples, delega ao Brain
            return {"success": True, "type": "delegate_to_brain",
                    "message": msg}

        filepath = os.path.join(self.user_home, "Desktop", filename)
        try:
            Path(filepath).write_text(code, encoding="utf-8")
            # Abrir o script criado
            subprocess.Popen(f'start python "{filepath}"', shell=True)
            return {"success": True, "type": "create_script",
                    "message": f"[OK] App criado e executado: {filepath}"}
        except Exception as e:
            return {"success": False, "type": "create_script",
                    "message": f"[ERRO] {e}"}

    # =====================================================================
    # PERGUNTAS DE CONHECIMENTO (busca web automatica)
    # =====================================================================
    def _try_knowledge_question(self, msg: str) -> Optional[Dict]:
        """Detecta perguntas de conhecimento geral e busca na web.
        NUNCA abre navegador direto - sempre traz resposta ou pergunta ao usuario."""
        # Padroes de perguntas que PRECISAM de busca web
        question_patterns = [
            r'(?:quais|qual)\s+(?:as|a|o|os)\s+(?:principais?\s+|ultimas?\s+)?(?:noticias|novidades|manchetes)',
            r'(?:noticias|noticia|novidades|manchetes)',  # Qualquer menção a notícias
            r'(?:como\s+esta|qual)\s+o\s+(?:tempo|clima|previsao)',
            r'(?:me\s+)?(?:fale?|diga|conte|explique?)\s+(?:sobre|a respeito)',
            r'(?:o\s+que\s+(?:e|sao|significa)|quem\s+(?:e|foi|sao))',
            r'(?:quando\s+(?:foi|e|sera|aconteceu))',
            r'(?:como\s+funciona|como\s+fazer)',
            r'(?:quanto\s+(?:custa|vale|e))',
            r'(?:onde\s+(?:fica|esta|encontro))\s+(?!.*(?:arquivo|pasta|no\s+pc|no\s+meu))',
            r'(?:por\s+que|porque)\s+(?!.*(?:arquivo|pasta))',
            r'(?:noticias|noticia)\s+(?:de|do|da|sobre)',
            r'(?:cotacao|dolar|euro|bitcoin|bolsa)',
            r'(?:resultado|placar|jogo)\s+(?:de|do|da)',
            r'(?:previsao|temperatura)\s+(?:de|do|da|em|para)',
            r'(?:o\s+que\s+(?:esta|ta)\s+(?:acontecendo|rolando))',
            r'(?:pesquis[ae]|busca?r?|procur[ae])\s+(?:sobre|por|no google)',
        ]

        is_question = any(re.search(p, msg) for p in question_patterns)
        if not is_question:
            return None

        # NAO buscar se e sobre arquivos/pc
        if any(w in msg for w in ["no meu pc", "no pc", "arquivo", "pasta", "programa"]):
            return None

        # Detecta se e busca de NOTICIAS (usa endpoint especifico)
        is_news = any(w in msg for w in ["noticias", "noticia", "novidades", "manchetes",
                                          "acontecendo", "ultimas"])

        # Faz busca web e traz resposta
        try:
            from src.core.web_search import get_web_search
            ws = get_web_search()

            if is_news:
                result = ws.search_news(msg)
            else:
                result = ws.search(msg)

            if result["success"]:
                answer = result["answer"][:800]
                source = result.get("source", "Web")
                return {"success": True, "type": "web_answer",
                        "message": f"[OK] Resultado:\n\n{answer}\n\n[Fonte: {source}]"}
            else:
                # NAO abre navegador! Pergunta ao usuario
                self._pending_search_query = msg
                return {"success": True, "type": "ask_user",
                        "message": f"[INFO] Nao consegui trazer o resumo para esta busca.\n\n"
                                   f"Quer que eu abra no navegador para voce pesquisar?\n"
                                   f"(Digite 'sim' ou 'abra' para abrir o Google)"}
        except Exception as e:
            log.error(f"Erro knowledge question: {e}")
            self._pending_search_query = msg
            return {"success": True, "type": "ask_user",
                    "message": f"[INFO] Erro na busca web. Quer que eu abra no navegador?\n"
                               f"(Digite 'sim' ou 'abra' para pesquisar no Google)"}

    # =====================================================================
    # ABRIR SITES
    # =====================================================================
    def _try_open_site(self, msg: str) -> Optional[Dict]:
        """Abre sites conhecidos ou URLs."""
        open_words = ["abra", "abrir", "abre", "entre", "entrar", "acesse",
                      "acessar", "va para", "vai para", "visite", "visitar",
                      "navegue", "navegar"]

        if not any(w in msg for w in open_words):
            return None

        # NAO abrir site se eh busca local ou comando de sistema
        skip_words = ["no meu pc", "no pc", "arquivo", "pasta", "processo",
                      "programa", "terminal", "cmd", "bloco", "calculadora",
                      "notepad", "explorer", "lixeira"]
        if any(w in msg for w in skip_words):
            return None

        # Sites conhecidos - usa match por palavra inteira
        for name, url in self.SITES.items():
            # Evita match parcial: "x" nao pode dar match em "execute"
            # Usa regex de word boundary
            pattern = r'\b' + re.escape(name) + r'\b'
            if re.search(pattern, msg):
                webbrowser.open(url)
                log.info(f"Site aberto: {url}")
                return {"success": True, "type": "open_site",
                        "message": f"[OK] {name.capitalize()} aberto no navegador!"}

        # URL direta
        url_match = re.search(r'(https?://[^\s]+)', msg)
        if url_match:
            url = url_match.group(1)
            webbrowser.open(url)
            return {"success": True, "type": "open_site",
                    "message": f"[OK] Site aberto: {url}"}

        # Dominio direto (ex: "abra google.com")
        domain_match = re.search(r'([a-zA-Z0-9-]+\.(com|com\.br|net|org|io|dev|tv|gg)(?:\.[a-z]{2})?)', msg)
        if domain_match:
            domain = domain_match.group(1)
            webbrowser.open(f"https://{domain}")
            return {"success": True, "type": "open_site",
                    "message": f"[OK] Site aberto: https://{domain}"}

        return None

    # =====================================================================
    # PESQUISAR NA WEB (TRAZ A RESPOSTA NO CHAT!)
    # =====================================================================
    def _try_search_web(self, msg: str) -> Optional[Dict]:
        """Pesquisa na web - SEMPRE tenta trazer resposta no chat primeiro.
        So abre navegador se o usuario pedir EXPLICITAMENTE 'abra no google'."""
        # Se pede busca LOCAL, nao pesquisa na web
        local_indicators = ["no meu pc", "no pc", "no computador", "no meu computador",
                            "nesta pasta", "neste pc", "local", "arquivo",
                            "onde esta", "localizar"]
        if any(w in msg for w in local_indicators):
            return None

        search_words = ["pesquise", "pesquisar", "pesquisa", "busque", "buscar", "busca",
                        "procure", "procurar", "procura", "google", "googlar",
                        "search", "buscar na web", "pesquisar na internet",
                        "o que e", "o que sao", "quem e", "quem foi",
                        "quando foi", "como funciona", "me explica",
                        "me fala sobre", "me diga sobre"]

        if not any(w in msg for w in search_words):
            return None

        # Indicadores de que quer ABRIR no navegador (explicito)
        open_browser = ["abra no google", "abre no google", "abrir no google",
                        "abra a pagina", "abre a pagina", "abrir a pagina",
                        "abra no navegador", "abre no navegador"]
        wants_browser = any(w in msg for w in open_browser)

        # Remove palavras-chave e pega o restante como query
        query = msg
        for w in search_words + ["no google", "na internet", "na web", "pra mim",
                                  "para mim", "sobre", "por favor", "e traga",
                                  "e me traga", "aqui", "a resposta", "e me diga",
                                  "e me fale", "e me fala"]:
            query = query.replace(w, "")
        query = query.strip()

        if not query or len(query) < 2:
            return None

        if wants_browser:
            # Usuario pediu EXPLICITAMENTE para abrir no navegador
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return {"success": True, "type": "search",
                    "message": f"[OK] Pesquisa aberta no Google: '{query}'"}

        # SEMPRE tenta trazer resposta no chat PRIMEIRO
        try:
            from src.core.web_search import get_web_search
            ws = get_web_search()
            result = ws.search(query)
            if result["success"]:
                answer = result["answer"][:800]
                source = result.get("source", "Web")
                return {"success": True, "type": "web_answer",
                        "message": f"[OK] Resultado para '{query}':\n\n{answer}\n\n[Fonte: {source}]"}
            else:
                # NAO abre automatico - pergunta ao usuario!
                self._pending_search_query = query
                return {"success": True, "type": "ask_user",
                        "message": f"[INFO] Nao encontrei resultado direto para '{query}'.\n\n"
                                   f"Quer que eu abra no Google pra voce pesquisar?\n"
                                   f"(Digite 'sim' ou 'abra no google')"}
        except Exception as e:
            log.error(f"Erro no web search: {e}")
            self._pending_search_query = query
            return {"success": True, "type": "ask_user",
                    "message": f"[INFO] Erro ao pesquisar. Quer que eu abra no Google?\n"
                               f"(Digite 'sim' ou 'abra no google')"}

    # =====================================================================
    # ABRIR PROGRAMAS
    # =====================================================================
    def _try_open_app(self, msg: str) -> Optional[Dict]:
        open_words = ["abra", "abrir", "abre", "execute", "executar", "executa",
                      "inicie", "iniciar", "inicia", "rode", "rodar", "roda",
                      "lance", "lancar", "lanca", "liga", "ligar", "start",
                      "acessar", "acesse"]

        if not any(w in msg for w in open_words):
            return None

        for name, exe in self.APPS.items():
            if name in msg:
                try:
                    os.startfile(exe)
                    log.info(f"App aberto: {exe}")
                    return {"success": True, "type": "open_app",
                            "message": f"[OK] {name.capitalize()} aberto com sucesso!"}
                except Exception:
                    try:
                        subprocess.Popen(f"start {exe}", shell=True)
                        return {"success": True, "type": "open_app",
                                "message": f"[OK] {name.capitalize()} aberto com sucesso!"}
                    except Exception as e:
                        return {"success": False, "type": "open_app",
                                "message": f"[ERRO] Nao consegui abrir {name}: {e}"}

        # Tenta abrir pasta se mencionou
        for name, folder in self.FOLDERS.items():
            if name in msg and any(w in msg for w in ["pasta", "abra", "abre"]):
                path = os.path.join(self.user_home, folder)
                os.startfile(path)
                return {"success": True, "type": "open_folder",
                        "message": f"[OK] Pasta {name} aberta!"}

        return None

    # =====================================================================
    # FECHAR PROGRAMAS
    # =====================================================================
    def _try_close_app(self, msg: str) -> Optional[Dict]:
        close_words = ["feche", "fechar", "fecha", "encerre", "encerrar", "encerra",
                       "mate", "matar", "mata", "pare", "parar", "close", "kill"]

        if not any(w in msg for w in close_words):
            return None

        # Mapeia nomes de apps para lista de possíveis nomes de processo (incluindo UWP)
        UWP_ALIASES = {
            "calculadora": ["calc.exe", "CalculatorApp.exe", "Calculator.exe"],
            "calc": ["calc.exe", "CalculatorApp.exe", "Calculator.exe"],
            "fotos": ["Microsoft.Photos.exe", "Photos.exe"],
            "photos": ["Microsoft.Photos.exe", "Photos.exe"],
            "loja": ["WinStore.App.exe", "WindowsStore.exe"],
            "store": ["WinStore.App.exe", "WindowsStore.exe"],
            "camera": ["WindowsCamera.exe", "Camera.exe"],
            "relogio": ["Time.exe", "Clock.exe"],
            "alarmes": ["Time.exe", "Clock.exe"],
        }

        # Detecta se quer fechar múltiplas instâncias: "as duas", "todas as", "os dois", etc
        wants_multiple = any(w in msg for w in [
            "todas as", "todos os", "as duas", "os dois",
            "as tres", "os tres", "as 2", "os 2", "as 3", "os 3",
            "todas", "todos", "tudo",
        ])

        for name, exe in self.APPS.items():
            if name in msg:
                exe_name = exe if exe.endswith(".exe") else exe + ".exe"
                # Constrói lista de nomes de processo a tentar (padrão + UWP)
                targets = [exe_name]
                if name in UWP_ALIASES:
                    targets = list(set(targets + UWP_ALIASES[name]))

                killed = []

                # Tenta taskkill para cada target
                for target in targets:
                    try:
                        result = subprocess.run(
                            f"taskkill /im {target} /f",
                            shell=True, capture_output=True, timeout=10
                        )
                        if result.returncode == 0:
                            killed.append(target)
                    except Exception:
                        pass

                # Se quer múltiplas instâncias ou é UWP, usa psutil para garantir
                if wants_multiple or name in UWP_ALIASES:
                    for proc in psutil.process_iter(['name']):
                        try:
                            pname = proc.info['name'].lower()
                            for target in targets:
                                if target.lower() == pname:
                                    proc.kill()
                                    if target not in killed:
                                        killed.append(target)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass

                if killed:
                    killed_str = ', '.join(set(killed))
                    return {"success": True, "type": "close_app",
                            "message": f"[OK] {name.capitalize()} fechado(s)! ({killed_str})"}
                else:
                    return {"success": True, "type": "close_app",
                            "message": f"[OK] {name.capitalize()} nao estava aberto."}

        # "feche tudo" / "feche todos os programas"
        if any(w in msg for w in ["tudo", "todos"]):
            apps_closed = []
            closeable = ['chrome.exe', 'firefox.exe', 'notepad.exe', 'calc.exe',
                         'CalculatorApp.exe', 'msedge.exe', 'discord.exe', 'spotify.exe']
            for proc in psutil.process_iter(['name']):
                try:
                    pname = proc.info['name'].lower()
                    if pname in [c.lower() for c in closeable]:
                        proc.kill()
                        apps_closed.append(pname)
                except:
                    pass
            if apps_closed:
                return {"success": True, "type": "close_all",
                        "message": f"[OK] Fechados: {', '.join(set(apps_closed))}"}

        return None

    # =====================================================================
    # CRIAR ARQUIVO COM CONTEUDO
    # =====================================================================
    def _try_create_file_with_content(self, msg: str) -> Optional[Dict]:
        """Cria arquivo COM conteudo especifico."""
        # "escreva X no arquivo Y" / "crie arquivo Y com conteudo X"
        patterns = [
            r'(?:escreva|escrever|escreve|coloque|colocar|coloca|adicione|adicionar)\s+"([^"]+)"\s+(?:no|no arquivo|em)\s+([a-zA-Z0-9_.-]+\.\w+)',
            r'(?:crie|criar|faca)\s+(?:arquivo|um arquivo)\s+([a-zA-Z0-9_.-]+\.\w+)\s+(?:com|contendo|com conteudo|escrito)\s+"([^"]+)"',
        ]

        for p in patterns:
            m = re.search(p, msg)
            if m:
                groups = m.groups()
                if 'escreva' in p or 'coloque' in p or 'adicione' in p:
                    content, filename = groups
                else:
                    filename, content = groups

                folder = "Desktop"
                for name, folder_name in self.FOLDERS.items():
                    if name in msg:
                        folder = folder_name
                        break

                filepath = os.path.join(self.user_home, folder, filename)
                try:
                    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
                    Path(filepath).write_text(content, encoding="utf-8")
                    return {"success": True, "type": "create_file",
                            "message": f"[OK] Arquivo criado com conteudo: {filepath}"}
                except Exception as e:
                    return {"success": False, "type": "create_file",
                            "message": f"[ERRO] {e}"}
        return None

    # =====================================================================
    # CRIAR ARQUIVO
    # =====================================================================
    def _try_create_file(self, msg: str) -> Optional[Dict]:
        create_words = ["crie", "criar", "cria", "faca", "fazer", "faz",
                        "gerar", "gera", "gere", "novo arquivo", "criar arquivo"]

        if not any(w in msg for w in create_words):
            return None

        patterns = [
            r'(?:arquivo|chamado|nome)\s+([a-zA-Z0-9_.-]+\.\w+)',
            r'([a-zA-Z0-9_.-]+\.txt)', r'([a-zA-Z0-9_.-]+\.py)',
            r'([a-zA-Z0-9_.-]+\.html?)', r'([a-zA-Z0-9_.-]+\.css)',
            r'([a-zA-Z0-9_.-]+\.js)', r'([a-zA-Z0-9_.-]+\.json)',
            r'([a-zA-Z0-9_.-]+\.docx?)', r'([a-zA-Z0-9_.-]+\.\w{1,5})',
        ]

        filename = None
        for p in patterns:
            m = re.search(p, msg)
            if m:
                filename = m.group(1)
                break

        if not filename:
            return None

        folder = "Desktop"
        for name, folder_name in self.FOLDERS.items():
            if name in msg:
                folder = folder_name
                break

        filepath = os.path.join(self.user_home, folder, filename)
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            Path(filepath).write_text("", encoding="utf-8")
            return {"success": True, "type": "create_file",
                    "message": f"[OK] Arquivo criado: {filepath}"}
        except Exception as e:
            return {"success": False, "type": "create_file", "message": f"[ERRO] {e}"}

    # =====================================================================
    # DELETAR ARQUIVO
    # =====================================================================
    def _try_delete_file(self, msg: str) -> Optional[Dict]:
        del_words = ["delete", "deletar", "deleta", "apague", "apagar", "apaga",
                     "remova", "remover", "remove", "exclua", "excluir", "exclui"]
        if not any(w in msg for w in del_words):
            return None

        patterns = [r'(?:arquivo|chamado)\s+([a-zA-Z0-9_.-]+\.\w+)',
                    r'([a-zA-Z0-9_.-]+\.txt)', r'([a-zA-Z0-9_.-]+\.\w{1,5})']
        filename = None
        for p in patterns:
            m = re.search(p, msg)
            if m:
                filename = m.group(1)
                break
        if not filename:
            return None

        folder = "Desktop"
        for name, folder_name in self.FOLDERS.items():
            if name in msg:
                folder = folder_name
                break

        filepath = os.path.join(self.user_home, folder, filename)
        try:
            p = Path(filepath)
            if p.exists():
                p.unlink()
                return {"success": True, "type": "delete",
                        "message": f"[OK] Arquivo deletado: {filepath}"}
            return {"success": False, "type": "delete",
                    "message": f"[ERRO] Arquivo nao encontrado: {filepath}"}
        except Exception as e:
            return {"success": False, "type": "delete", "message": f"[ERRO] {e}"}

    # =====================================================================
    # LER ARQUIVO
    # =====================================================================
    def _try_read_file(self, msg: str) -> Optional[Dict]:
        read_words = ["leia", "ler", "le", "mostrar conteudo", "mostra conteudo",
                      "conteudo do arquivo", "o que tem no arquivo"]
        if not any(w in msg for w in read_words):
            return None

        patterns = [r'(?:arquivo|chamado)\s+([a-zA-Z0-9_.-]+\.\w+)',
                    r'([a-zA-Z0-9_.-]+\.txt)', r'([a-zA-Z0-9_.-]+\.\w{1,5})']
        filename = None
        for p in patterns:
            m = re.search(p, msg)
            if m:
                filename = m.group(1)
                break
        if not filename:
            return None

        folder = "Desktop"
        for name, folder_name in self.FOLDERS.items():
            if name in msg:
                folder = folder_name
                break

        filepath = os.path.join(self.user_home, folder, filename)
        try:
            content = Path(filepath).read_text(encoding="utf-8")
            preview = content[:500]
            return {"success": True, "type": "read",
                    "message": f"[OK] Conteudo de {filename}:\n{preview}"}
        except Exception as e:
            return {"success": False, "type": "read", "message": f"[ERRO] {e}"}

    # =====================================================================
    # LISTAR ARQUIVOS
    # =====================================================================
    def _try_list_files(self, msg: str) -> Optional[Dict]:
        list_words = ["liste", "listar", "lista", "mostre", "mostrar", "mostra",
                      "exiba", "exibir", "quais arquivos", "ver arquivos", "conteudo da pasta"]
        has_list = any(w in msg for w in list_words)
        has_ref = any(w in msg for w in ["arquivo", "arquivos", "pasta", "downloads",
                                          "documentos", "desktop", "area de trabalho"])
        if not (has_list and has_ref):
            return None

        folder = self.user_home
        for name, folder_name in self.FOLDERS.items():
            if name in msg:
                folder = os.path.join(self.user_home, folder_name)
                break

        try:
            p = Path(folder)
            if not p.exists():
                return {"success": False, "type": "list", "message": f"[ERRO] Pasta nao existe: {folder}"}
            items = sorted(p.iterdir(), key=lambda x: x.name)[:30]
            lines = []
            for item in items:
                icon = "[DIR]" if item.is_dir() else "[ARQ]"
                size = ""
                if item.is_file():
                    s = item.stat().st_size
                    if s > 1048576: size = f" ({s/1048576:.1f} MB)"
                    elif s > 1024: size = f" ({s/1024:.1f} KB)"
                    else: size = f" ({s} bytes)"
                lines.append(f"  {icon} {item.name}{size}")
            return {"success": True, "type": "list",
                    "message": f"[OK] {len(items)} itens em {folder}:\n" + "\n".join(lines)}
        except Exception as e:
            return {"success": False, "type": "list", "message": f"[ERRO] {e}"}

    # =====================================================================
    # INFO DO SISTEMA
    # =====================================================================
    def _try_system_info(self, msg: str) -> Optional[Dict]:
        # NAO interceptar se e agendamento, busca, ou criacao
        skip_if = ["agende", "agendar", "pesquise", "pesquisar", "crie", "criar",
                    "procure", "busque", "lembre-me", "lembre me"]
        if any(w in msg for w in skip_if):
            return None

        # Usa regex word boundary para "ram" e "cpu" (evita match em "programacao" etc)
        info_patterns = [
            r'\bmemoria\b', r'\bram\b', r'\bcpu\b', r'\bprocessador\b', r'\bhardware\b',
            r'informacoes do sistema', r'info do sistema', r'quanto de ram',
            r'quanto de cpu', r'uso de memoria', r'uso de cpu',
        ]
        if not any(re.search(p, msg) for p in info_patterns):
            return None
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('C:\\')
            uptime_s = time.time() - psutil.boot_time()
            hours = int(uptime_s // 3600)
            mins = int((uptime_s % 3600) // 60)

            text = f"""[OK] Informacoes do Sistema:
  CPU: {cpu}% em uso ({psutil.cpu_count()} nucleos)
  RAM: {mem.percent}% em uso ({mem.used/(1024**3):.1f} GB / {mem.total/(1024**3):.1f} GB)
  RAM Livre: {mem.available/(1024**3):.1f} GB
  Disco C: {disk.percent}% em uso ({disk.used/(1024**3):.0f} GB / {disk.total/(1024**3):.0f} GB)
  Disco C livre: {disk.free/(1024**3):.1f} GB
  Uptime: {hours}h {mins}min
  Sistema: {platform.system()} {platform.release()}
  PC: {platform.node()}"""
            return {"success": True, "type": "system_info", "message": text}
        except Exception as e:
            return {"success": False, "type": "system_info", "message": f"[ERRO] {e}"}

    # =====================================================================
    # SCREENSHOT
    # =====================================================================
    def _try_screenshot(self, msg: str) -> Optional[Dict]:
        ss_words = ["screenshot", "print da tela", "captura de tela", "printscreen",
                    "print screen", "tire um print", "tira print", "capture a tela",
                    "foto da tela"]
        if not any(w in msg for w in ss_words):
            return None
        try:
            import pyautogui
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(self.user_home, "Desktop", f"screenshot_{ts}.png")
            img = pyautogui.screenshot()
            img.save(path)
            return {"success": True, "type": "screenshot",
                    "message": f"[OK] Screenshot salvo: {path}"}
        except ImportError:
            return {"success": False, "type": "screenshot",
                    "message": "[ERRO] Instale pyautogui: pip install pyautogui"}
        except Exception as e:
            return {"success": False, "type": "screenshot", "message": f"[ERRO] {e}"}

    # =====================================================================
    # VOLUME
    # =====================================================================
    def _try_volume(self, msg: str) -> Optional[Dict]:
        up_words = ["aumentar volume", "aumenta volume", "aumenta o volume", "aumente o volume",
                    "volume mais alto", "sobe volume", "subir volume", "mais alto",
                    "volume pra cima", "volume acima", "som mais alto", "mais volume"]
        down_words = ["diminuir volume", "diminui volume", "diminui o volume", "diminua o volume",
                      "volume mais baixo", "abaixa volume", "abaixar volume", "abaixa o volume",
                      "mais baixo", "volume pra baixo", "volume abaixo", "menos volume",
                      "som mais baixo"]
        mute_words = ["mutar", "mute", "silenciar", "silencio", "sem som", "tirar som",
                      "desmutar", "tirar o som", "mudo"]

        if any(w in msg for w in up_words):
            for _ in range(5):  # Aumenta 5 niveis
                subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"',
                              shell=True, capture_output=True)
            return {"success": True, "type": "volume", "message": "[OK] Volume aumentado!"}

        if any(w in msg for w in down_words):
            for _ in range(5):
                subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"',
                              shell=True, capture_output=True)
            return {"success": True, "type": "volume", "message": "[OK] Volume diminuido!"}

        if any(w in msg for w in mute_words):
            subprocess.run('powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"',
                          shell=True, capture_output=True)
            return {"success": True, "type": "volume", "message": "[OK] Som mutado/desmutado!"}

        return None

    # =====================================================================
    # WIFI / REDE
    # =====================================================================
    def _try_wifi_info(self, msg: str) -> Optional[Dict]:
        wifi_words = ["wifi", "wi-fi", "rede wifi", "senha do wifi", "redes disponiveis",
                      "qual wifi", "conectado em qual rede", "ssid"]
        if not any(w in msg for w in wifi_words):
            return None

        if any(w in msg for w in ["senha", "password"]):
            try:
                result = subprocess.run(
                    'netsh wlan show profile', shell=True,
                    capture_output=True, text=True, timeout=10
                )
                profiles = re.findall(r'Perfil de Todos os Usu.*:\s*(.*)', result.stdout)
                if not profiles:
                    profiles = re.findall(r'All User Profile\s*:\s*(.*)', result.stdout)

                info_parts = []
                for profile in profiles[:5]:
                    profile = profile.strip()
                    pwd_result = subprocess.run(
                        f'netsh wlan show profile name="{profile}" key=clear',
                        shell=True, capture_output=True, text=True, timeout=10
                    )
                    pwd_match = re.search(r'Conte.*Chave\s*:\s*(.*)', pwd_result.stdout)
                    if not pwd_match:
                        pwd_match = re.search(r'Key Content\s*:\s*(.*)', pwd_result.stdout)
                    pwd = pwd_match.group(1).strip() if pwd_match else "N/A"
                    info_parts.append(f"  {profile}: {pwd}")

                return {"success": True, "type": "wifi",
                        "message": f"[OK] Senhas WiFi salvas:\n" + "\n".join(info_parts)}
            except Exception as e:
                return {"success": False, "type": "wifi", "message": f"[ERRO] {e}"}
        else:
            try:
                result = subprocess.run(
                    'netsh wlan show interfaces', shell=True,
                    capture_output=True, text=True, timeout=10
                )
                return {"success": True, "type": "wifi",
                        "message": f"[OK] Info WiFi:\n{result.stdout[:600]}"}
            except Exception as e:
                return {"success": False, "type": "wifi", "message": f"[ERRO] {e}"}

    # =====================================================================
    # CLIPBOARD
    # =====================================================================
    def _try_clipboard(self, msg: str) -> Optional[Dict]:
        if any(w in msg for w in ["copiar", "copie", "copia", "clipboard", "area de transferencia"]):
            # "copie X" / "copiar o texto X"
            match = re.search(r'(?:copie|copiar|copia)\s+"([^"]+)"', msg)
            if match:
                text = match.group(1)
                subprocess.run(f'echo {text}| clip', shell=True)
                return {"success": True, "type": "clipboard",
                        "message": f"[OK] Texto copiado para clipboard: '{text}'"}

            # Mostrar clipboard atual
            if any(w in msg for w in ["mostrar", "ver", "o que tem", "conteudo"]):
                try:
                    result = subprocess.run(
                        'powershell -c "Get-Clipboard"', shell=True,
                        capture_output=True, text=True, timeout=5
                    )
                    return {"success": True, "type": "clipboard",
                            "message": f"[OK] Clipboard atual:\n{result.stdout[:300]}"}
                except:
                    pass
        return None

    # =====================================================================
    # TIMER / ALARME
    # =====================================================================
    def _try_timer(self, msg: str) -> Optional[Dict]:
        timer_words = ["timer", "temporizador", "alarme", "avise", "avisar",
                       "lembre", "lembrar", "lembrete", "daqui a", "em minutos",
                       "em segundos", "cronometro"]
        if not any(w in msg for w in timer_words):
            return None

        # Extrair tempo
        minutes = 0
        seconds = 0

        min_match = re.search(r'(\d+)\s*(?:minuto|min|m(?!\w))', msg)
        sec_match = re.search(r'(\d+)\s*(?:segundo|seg|s(?!\w))', msg)

        if min_match:
            minutes = int(min_match.group(1))
        if sec_match:
            seconds = int(sec_match.group(1))

        total_seconds = minutes * 60 + seconds
        if total_seconds <= 0:
            return None

        def timer_alarm():
            time.sleep(total_seconds)
            # Toca alarme
            import winsound
            for _ in range(5):
                winsound.Beep(1000, 500)
                time.sleep(0.3)

        thread = threading.Thread(target=timer_alarm, daemon=True)
        thread.start()

        time_str = ""
        if minutes: time_str += f"{minutes} minuto(s) "
        if seconds: time_str += f"{seconds} segundo(s)"

        return {"success": True, "type": "timer",
                "message": f"[OK] Timer configurado: {time_str.strip()}. Vai tocar alarme!"}

    # =====================================================================
    # LIMPEZA DO SISTEMA
    # =====================================================================
    def _try_cleanup(self, msg: str) -> Optional[Dict]:
        clean_words = ["limpar", "limpeza", "limpe", "limpa", "liberar espaco",
                       "liberar memoria", "liberar ram", "clean", "cleanup",
                       "temporarios", "arquivos temporarios", "limpar temp"]
        # NAO usar "temp" sozinho - confunde com "tempo"
        # NAO usar "lixo" sozinho - confunde com "lixeira"
        if not any(w in msg for w in clean_words):
            return None

        cleaned = []
        freed = 0

        # Limpa temp
        temp = Path(os.environ.get('TEMP', ''))
        if temp.exists():
            count = 0
            for f in temp.iterdir():
                try:
                    if f.is_file():
                        size = f.stat().st_size
                        f.unlink()
                        freed += size
                        count += 1
                    elif f.is_dir():
                        shutil.rmtree(f, ignore_errors=True)
                        count += 1
                except:
                    pass
            cleaned.append(f"Temp: {count} itens removidos")

        # Limpa cache do navegador (thumbnails etc)
        prefetch = Path('C:/Windows/Prefetch')
        if prefetch.exists():
            try:
                count = 0
                for f in prefetch.glob('*.pf'):
                    try:
                        f.unlink()
                        count += 1
                    except:
                        pass
                if count > 0:
                    cleaned.append(f"Prefetch: {count} itens")
            except:
                pass

        freed_mb = freed / (1024 * 1024)
        return {"success": True, "type": "cleanup",
                "message": f"[OK] Limpeza realizada! {freed_mb:.1f} MB liberados\n  " + "\n  ".join(cleaned)}

    # =====================================================================
    # ESPACO EM DISCO
    # =====================================================================
    def _try_disk_space(self, msg: str) -> Optional[Dict]:
        disk_words = ["disco", "espaco", "espaco em disco", "armazenamento",
                      "quanto espaco", "espaco livre", "hd", "ssd"]
        if not any(w in msg for w in disk_words):
            return None

        try:
            partitions = psutil.disk_partitions()
            lines = []
            for p in partitions:
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    lines.append(
                        f"  {p.device}: {usage.percent}% usado "
                        f"({usage.used/(1024**3):.1f} GB / {usage.total/(1024**3):.1f} GB) "
                        f"- Livre: {usage.free/(1024**3):.1f} GB"
                    )
                except:
                    pass
            return {"success": True, "type": "disk",
                    "message": "[OK] Espaco em disco:\n" + "\n".join(lines)}
        except Exception as e:
            return {"success": False, "type": "disk", "message": f"[ERRO] {e}"}

    # =====================================================================
    # INFORMACOES DE REDE
    # =====================================================================
    def _try_network_info(self, msg: str) -> Optional[Dict]:
        net_words = ["meu ip", "ip local", "ip publico", "ip externo",
                     "endereco ip", "rede", "conexao"]
        if not any(w in msg for w in net_words):
            return None

        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            # Tenta IP publico
            public_ip = "N/A"
            try:
                import urllib.request
                public_ip = urllib.request.urlopen('https://api.ipify.org', timeout=3).read().decode()
            except:
                pass

            text = f"""[OK] Informacoes de Rede:
  Nome do PC: {hostname}
  IP Local: {local_ip}
  IP Publico: {public_ip}"""
            return {"success": True, "type": "network", "message": text}
        except Exception as e:
            return {"success": False, "type": "network", "message": f"[ERRO] {e}"}

    # =====================================================================
    # BATERIA
    # =====================================================================
    def _try_battery(self, msg: str) -> Optional[Dict]:
        bat_words = ["bateria", "battery", "energia", "carregando", "carga"]
        if not any(w in msg for w in bat_words):
            return None
        try:
            bat = psutil.sensors_battery()
            if bat:
                status = "Carregando" if bat.power_plugged else "Na bateria"
                time_left = ""
                if bat.secsleft > 0 and not bat.power_plugged:
                    h = bat.secsleft // 3600
                    m = (bat.secsleft % 3600) // 60
                    time_left = f"\n  Tempo restante: {h}h {m}min"
                return {"success": True, "type": "battery",
                        "message": f"[OK] Bateria: {bat.percent}% - {status}{time_left}"}
            return {"success": True, "type": "battery",
                    "message": "[OK] Sem bateria detectada (PC desktop)"}
        except Exception as e:
            return {"success": False, "type": "battery", "message": f"[ERRO] {e}"}

    # =====================================================================
    # PROGRAMAS NA INICIALIZACAO
    # =====================================================================
    def _try_startup_apps(self, msg: str) -> Optional[Dict]:
        if not any(w in msg for w in ["inicializacao", "startup", "inicializam",
                                       "abrem sozinhos", "auto iniciar"]):
            return None
        try:
            result = subprocess.run(
                'powershell -c "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command | Format-Table -AutoSize"',
                shell=True, capture_output=True, text=True, timeout=15
            )
            return {"success": True, "type": "startup",
                    "message": f"[OK] Programas na inicializacao:\n{result.stdout[:800]}"}
        except Exception as e:
            return {"success": False, "type": "startup", "message": f"[ERRO] {e}"}

    # =====================================================================
    # PROGRAMAS INSTALADOS
    # =====================================================================
    def _try_installed_programs(self, msg: str) -> Optional[Dict]:
        if not any(w in msg for w in ["programas instalados", "softwares instalados",
                                       "aplicativos instalados", "o que esta instalado"]):
            return None
        try:
            result = subprocess.run(
                'powershell -c "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Sort-Object DisplayName | Format-Table -AutoSize"',
                shell=True, capture_output=True, text=True, timeout=15
            )
            output = result.stdout[:1500]
            return {"success": True, "type": "installed",
                    "message": f"[OK] Programas instalados:\n{output}"}
        except Exception as e:
            return {"success": False, "type": "installed", "message": f"[ERRO] {e}"}

    # =====================================================================
    # COMANDO DIRETO
    # =====================================================================
    def _try_direct_command(self, msg: str) -> Optional[Dict]:
        prefixes = ["cmd:", "execute:", "comando:", "exec:", "run:", "rodar:"]
        for prefix in prefixes:
            if msg.startswith(prefix):
                cmd = msg.split(":", 1)[1].strip()
                return self._run_command(cmd)

        cmd_patterns = [
            ("ipconfig", ["ipconfig", "meu ip", "minha rede"]),
            ("tasklist", ["tasklist", "processos ativos"]),
            ("systeminfo", ["systeminfo", "info completa"]),
            ("dir", ["comando dir", "execute dir"]),
            ("whoami", ["whoami", "meu usuario"]),
            ("hostname", ["hostname", "nome do pc", "nome do computador"]),
        ]
        for cmd, triggers in cmd_patterns:
            if any(t in msg for t in triggers):
                return self._run_command(cmd)
        return None

    def _run_command(self, cmd: str) -> Dict:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout[:1000] if result.stdout else result.stderr[:500]
            return {"success": result.returncode == 0, "type": "command",
                    "message": f"[OK] Comando '{cmd}':\n{output}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "type": "command", "message": f"[ERRO] Timeout: '{cmd}'"}
        except Exception as e:
            return {"success": False, "type": "command", "message": f"[ERRO] {e}"}

    # =====================================================================
    # RENOMEAR ARQUIVO
    # =====================================================================
    def _try_rename_file(self, msg: str) -> Optional[Dict]:
        """Renomeia arquivo ou pasta."""
        if not any(w in msg for w in ["renomeie", "renomear", "renomeia", "rename",
                                       "mude o nome", "mudar o nome"]):
            return None

        m = re.search(r'(?:renomeie?|rename|mude?\s+o\s+nome\s+d[eoa])\s+([a-zA-Z0-9_.-]+)\s+(?:para|pra|to)\s+([a-zA-Z0-9_.-]+)', msg)
        if not m:
            return None

        old_name, new_name = m.group(1), m.group(2)
        base = os.path.join(self.user_home, "Desktop")
        for name, folder in self.FOLDERS.items():
            if name in msg:
                base = os.path.join(self.user_home, folder)
                break

        old_path = os.path.join(base, old_name)
        new_path = os.path.join(base, new_name)
        try:
            if Path(old_path).exists():
                Path(old_path).rename(new_path)
                return {"success": True, "type": "rename",
                        "message": f"[OK] Renomeado: {old_name} -> {new_name}"}
            return {"success": False, "type": "rename",
                    "message": f"[ERRO] Arquivo nao encontrado: {old_name}"}
        except Exception as e:
            return {"success": False, "type": "rename", "message": f"[ERRO] {e}"}

    # =====================================================================
    # MOVER / COPIAR ARQUIVO
    # =====================================================================
    def _try_move_copy_file(self, msg: str) -> Optional[Dict]:
        """Move ou copia arquivo."""
        is_copy = any(w in msg for w in ["copie", "copiar", "copia", "copy"])
        is_move = any(w in msg for w in ["mova", "mover", "move", "transferir", "transfira"])

        if not is_copy and not is_move:
            return None

        m = re.search(r'(?:copie?|mova?|move|transferir?a?)\s+([a-zA-Z0-9_.-]+\.\w+)\s+(?:para|pra)\s+(.+?)(?:\s*$|\.)', msg)
        if not m:
            return None

        filename = m.group(1)
        dest_name = m.group(2).strip()

        # Resolve destino
        dest_folder = self.user_home
        for name, folder in self.FOLDERS.items():
            if name in dest_name:
                dest_folder = os.path.join(self.user_home, folder)
                break

        src = os.path.join(self.user_home, "Desktop", filename)
        # Tenta achar o arquivo em outras pastas
        if not Path(src).exists():
            for name, folder in self.FOLDERS.items():
                test = os.path.join(self.user_home, folder, filename)
                if Path(test).exists():
                    src = test
                    break

        dest = os.path.join(dest_folder, filename)
        try:
            if not Path(src).exists():
                return {"success": False, "type": "file_op",
                        "message": f"[ERRO] Arquivo nao encontrado: {filename}"}
            if is_copy:
                shutil.copy2(src, dest)
                return {"success": True, "type": "file_op",
                        "message": f"[OK] Copiado: {filename} -> {dest_folder}"}
            else:
                shutil.move(src, dest)
                return {"success": True, "type": "file_op",
                        "message": f"[OK] Movido: {filename} -> {dest_folder}"}
        except Exception as e:
            return {"success": False, "type": "file_op", "message": f"[ERRO] {e}"}

    # =====================================================================
    # ABRIR PASTA DIRETAMENTE
    # =====================================================================
    def _try_open_folder(self, msg: str) -> Optional[Dict]:
        """Abre uma pasta especifica."""
        if not any(w in msg for w in ["abra a pasta", "abrir pasta", "abre a pasta",
                                       "abra pasta", "abrir a pasta"]):
            return None

        for name, folder in self.FOLDERS.items():
            if name in msg:
                path = os.path.join(self.user_home, folder)
                os.startfile(path)
                return {"success": True, "type": "open_folder",
                        "message": f"[OK] Pasta {name} aberta!"}

        # Tenta extrair nome da pasta
        m = re.search(r'pasta\s+([a-zA-Z0-9_ -]+)', msg)
        if m:
            folder_name = m.group(1).strip()
            path = os.path.join(self.user_home, "Desktop", folder_name)
            if Path(path).exists():
                os.startfile(path)
                return {"success": True, "type": "open_folder",
                        "message": f"[OK] Pasta {folder_name} aberta!"}
            return {"success": False, "type": "open_folder",
                    "message": f"[ERRO] Pasta nao encontrada: {folder_name}"}
        return None

    # =====================================================================
    # LISTA DE PROCESSOS EM EXECUCAO
    # =====================================================================
    def _try_process_list(self, msg: str) -> Optional[Dict]:
        """Mostra processos em execucao."""
        if not any(w in msg for w in ["processos", "processos rodando", "processos ativos",
                                       "o que esta rodando", "o que esta aberto",
                                       "programas abertos", "apps abertos",
                                       "quais programas", "quais apps"]):
            return None

        try:
            procs = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                try:
                    info = proc.info
                    if info['memory_percent'] and info['memory_percent'] > 0.1:
                        procs.append(info)
                except:
                    pass

            # Ordena por uso de memoria
            procs.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            lines = []
            for p in procs[:20]:
                mem = p.get('memory_percent', 0)
                lines.append(f"  {p['name']}: {mem:.1f}% RAM")

            return {"success": True, "type": "process_list",
                    "message": f"[OK] Top {len(lines)} processos (por RAM):\n" + "\n".join(lines)}
        except Exception as e:
            return {"success": False, "type": "process_list", "message": f"[ERRO] {e}"}

    # =====================================================================
    # DATA E HORA
    # =====================================================================
    def _try_date_time(self, msg: str) -> Optional[Dict]:
        """Mostra data e hora atual."""
        if not any(w in msg for w in ["que horas", "que hora", "hora atual", "data de hoje",
                                       "data atual", "qual a data", "qual a hora",
                                       "que dia e hoje", "dia da semana"]):
            return None

        now = datetime.now()
        dias = ["Segunda-feira", "Terca-feira", "Quarta-feira", "Quinta-feira",
                "Sexta-feira", "Sabado", "Domingo"]
        meses = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        dia_semana = dias[now.weekday()]
        mes = meses[now.month - 1]

        return {"success": True, "type": "datetime",
                "message": f"[OK] {dia_semana}, {now.day} de {mes} de {now.year} - {now.strftime('%H:%M:%S')}"}

    # =====================================================================
    # ABRIR QUALQUER ARQUIVO (com busca automatica de programa)
    # =====================================================================
    def _try_open_file_smart(self, msg: str) -> Optional[Dict]:
        """Abre qualquer arquivo. Se nao tiver programa, busca na internet."""
        # Detecta pedido de abrir arquivo especifico
        open_match = re.search(r'(?:abr[aie]|abrir|open|execute?|executa)\s+(?:o\s+)?(?:arquivo\s+)?(.+\.\w{1,5})', msg)
        if not open_match:
            return None

        filename = open_match.group(1).strip().strip('"').strip("'")

        # Procura o arquivo
        filepath = None
        search_paths = [
            self.user_home,
            os.path.join(self.user_home, "Desktop"),
            os.path.join(self.user_home, "Downloads"),
            os.path.join(self.user_home, "Documents"),
        ]

        for base in search_paths:
            candidate = os.path.join(base, filename)
            if os.path.exists(candidate):
                filepath = candidate
                break

        if not filepath:
            # Busca recursiva no Desktop e Downloads
            for base in search_paths[1:3]:
                for root_dir, dirs, files in os.walk(base):
                    for f in files:
                        if f.lower() == filename.lower():
                            filepath = os.path.join(root_dir, f)
                            break
                    if filepath:
                        break
                if filepath:
                    break

        if not filepath:
            return {"success": False, "type": "open_file",
                    "message": f"[ERRO] Arquivo '{filename}' nao encontrado."}

        # Tenta abrir com o programa padrao
        try:
            os.startfile(filepath)
            return {"success": True, "type": "open_file",
                    "message": f"[OK] Arquivo aberto: {filepath}"}
        except OSError:
            # Sem programa associado - busca extensao
            ext = os.path.splitext(filename)[1].lower()
            programs = {
                ".py": "python",
                ".js": "node",
                ".html": "chrome",
                ".htm": "chrome",
                ".pdf": "chrome",
                ".md": "notepad",
                ".json": "notepad",
                ".xml": "notepad",
                ".csv": "notepad",
                ".log": "notepad",
                ".txt": "notepad",
                ".sql": "notepad",
            }

            if ext in programs:
                prog = programs[ext]
                try:
                    subprocess.Popen(f'start {prog} "{filepath}"', shell=True)
                    return {"success": True, "type": "open_file",
                            "message": f"[OK] Abrindo {filename} com {prog}"}
                except:
                    pass

            # Ultimo recurso: sugere programa
            return {"success": True, "type": "ask_user",
                    "message": f"[INFO] Nao encontrei programa para abrir '{ext}'.\n"
                               f"Quer que eu pesquise um programa gratuito para abrir este tipo de arquivo?\n"
                               f"(Digite 'sim' para pesquisar)"}
        except Exception as e:
            return {"success": False, "type": "open_file",
                    "message": f"[ERRO] {e}"}

    # =====================================================================
    # INSTALAR PROGRAMA
    # =====================================================================
    def _try_install_program(self, msg: str) -> Optional[Dict]:
        """Instala programas via winget ou chocolatey."""
        if not any(w in msg for w in ["instale", "instalar", "instala", "install",
                                       "baixe", "baixar", "baixa", "download"]):
            return None

        # NAO instalar se e sobre arquivo/pasta
        if any(w in msg for w in ["arquivo", "pasta", "extensao"]):
            return None

        # Extrai nome do programa
        prog = msg
        for w in ["instale", "instalar", "instala", "install", "baixe", "baixar",
                   "baixa", "download", "o", "a", "programa", "app", "aplicativo",
                   "pra mim", "para mim", "por favor", "no meu pc", "no pc"]:
            prog = prog.replace(w, "")
        prog = prog.strip()

        if not prog or len(prog) < 2:
            return None

        # Tenta instalar via winget
        try:
            result = subprocess.run(
                ["winget", "search", prog],
                capture_output=True, text=True, timeout=15,
                encoding="utf-8", errors="replace"
            )
            if result.returncode == 0 and prog.lower() in result.stdout.lower():
                # Encontrou! Mostra e pergunta
                lines = result.stdout.strip().split('\n')
                matches = [l for l in lines if prog.lower() in l.lower()][:5]
                if matches:
                    info = "\n".join(f"  {m.strip()}" for m in matches)
                    return {"success": True, "type": "ask_user",
                            "message": f"[INFO] Encontrei no winget:\n{info}\n\n"
                                       f"Quer que eu instale? (Digite 'sim winget {prog}' para confirmar)"}
        except:
            pass

        # Se nao encontrou no winget, delega ao Brain
        return {"success": True, "type": "delegate_to_brain",
                "message": f"instale o programa {prog}"}

    # =====================================================================
    # AGENDAR TAREFA
    # =====================================================================
    def _try_schedule_task(self, msg: str) -> Optional[Dict]:
        """Agenda tarefa para execucao futura."""
        # Precisa ter PELO MENOS uma keyword de agendamento forte
        strong_schedule = ["agende", "agendar", "agenda", "lembre-me", "lembre me",
                           "me lembre", "lembrete", "me avise", "me notifique"]
        # Keywords fracas so ativam se acompanhadas de numero + tempo
        weak_schedule = re.search(r'(?:daqui a|todo dia|a cada)\s+\d+', msg)

        if not any(w in msg for w in strong_schedule) and not weak_schedule:
            return None

        try:
            from src.core.scheduler import get_scheduler
            scheduler = get_scheduler()

            # Extrai intervalo em minutos
            interval = 0
            min_match = re.search(r'(?:a cada|cada|daqui a|em)\s+(\d+)\s*(?:minuto|min)', msg)
            hour_match = re.search(r'(?:a cada|cada|daqui a|em)\s+(\d+)\s*(?:hora|h\b)', msg)
            at_match = re.search(r'(?:as|todo dia as?|diariamente as?)\s+(\d{1,2}):?(\d{2})?', msg)

            if min_match:
                interval = int(min_match.group(1))
            elif hour_match:
                interval = int(hour_match.group(1)) * 60

            run_at = None
            if at_match:
                h = at_match.group(1)
                m = at_match.group(2) or "00"
                run_at = f"{int(h):02d}:{int(m):02d}"

            # Extrai o comando/acao
            command = msg
            for w in ["agende", "agendar", "me lembre de", "lembre-me de",
                       "lembre me de", "lembrete", "me avise para",
                       "me notifique para", "todo dia", "a cada",
                       f"{interval} minutos", f"{interval} horas",
                       "daqui a", "diariamente"]:
                command = command.replace(w, "")
            if at_match:
                command = re.sub(r'(?:as|todo dia as?|diariamente as?)\s+\d{1,2}:?\d{0,2}', '', command)
            command = command.strip()

            if not command or len(command) < 3:
                return {"success": True, "type": "ask_user",
                        "message": "[INFO] O que voce quer que eu agende?"}

            name = command[:50]
            one_shot = interval == 0 and run_at is None

            if one_shot and not run_at:
                # Se nao tem intervalo nem horario, agenda pra daqui 1 min
                interval = 1
                one_shot = True

            task = scheduler.add_task(
                name=name, command=command,
                interval_minutes=interval, run_at=run_at,
                one_shot=one_shot
            )

            time_desc = ""
            if run_at:
                time_desc = f"todo dia as {run_at}"
            elif interval > 0:
                if one_shot:
                    time_desc = f"em {interval} minuto(s)"
                else:
                    time_desc = f"a cada {interval} minuto(s)"

            return {"success": True, "type": "schedule",
                    "message": f"[OK] Tarefa agendada: '{name}' {time_desc}"}
        except Exception as e:
            return {"success": False, "type": "schedule",
                    "message": f"[ERRO] {e}"}

    # =====================================================================
    # LISTAR TAREFAS AGENDADAS
    # =====================================================================
    def _try_list_scheduled(self, msg: str) -> Optional[Dict]:
        """Lista tarefas agendadas."""
        if not any(w in msg for w in ["tarefas agendadas", "tarefas programadas",
                                       "meus agendamentos", "meus lembretes",
                                       "o que esta agendado", "lista de tarefas"]):
            return None

        try:
            from src.core.scheduler import get_scheduler
            scheduler = get_scheduler()
            tasks = scheduler.list_tasks()

            if not tasks:
                return {"success": True, "type": "schedule_list",
                        "message": "[OK] Nenhuma tarefa agendada."}

            lines = []
            for t in tasks:
                status = "Ativa" if t.get("enabled") else "Desativada"
                next_run = t.get("next_run", "N/A")
                if next_run and next_run != "N/A":
                    next_run = next_run[:16].replace("T", " ")
                lines.append(f"  [{status}] {t['name']} | Proximo: {next_run} | Execucoes: {t.get('run_count', 0)}")

            return {"success": True, "type": "schedule_list",
                    "message": f"[OK] {len(tasks)} tarefa(s) agendada(s):\n" + "\n".join(lines)}
        except Exception as e:
            return {"success": False, "type": "schedule_list",
                    "message": f"[ERRO] {e}"}

    # =====================================================================
    # DESLIGAR/REINICIAR
    # =====================================================================
    def _try_power_action(self, msg: str) -> Optional[Dict]:
        if any(w in msg for w in ["desligar", "desliga", "shutdown"]):
            return {"success": True, "type": "power",
                    "message": "[!] Para desligar, confirme: cmd: shutdown /s /t 60"}
        if any(w in msg for w in ["reiniciar", "reinicia", "restart", "reboot"]):
            return {"success": True, "type": "power",
                    "message": "[!] Para reiniciar, confirme: cmd: shutdown /r /t 60"}
        if any(w in msg for w in ["suspender", "hibernar", "dormir", "sleep"]):
            return {"success": True, "type": "power",
                    "message": "[!] Para suspender, confirme: cmd: rundll32.exe powrprof.dll,SetSuspendState 0,1,0"}
        return None
