"""
AI Brain v2 - O CEREBRO SUPER-PODEROSO do William.
Quando os detectores fixos nao resolvem, a IA analisa o pedido
e gera acoes/codigo Python para executar.
NUNCA da desculpas. SEMPRE tenta executar.
"""

import json
import re
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional, List
from src.utils.logger import get_logger

log = get_logger(__name__)

USER_HOME = str(Path.home())
DESKTOP = os.path.join(USER_HOME, "Desktop")

BRAIN_SYSTEM_PROMPT = f"""Voce e o CEREBRO EXECUTOR do assistente William.
Voce analisa pedidos e gera CODIGO PYTHON executavel. Voce NUNCA recusa.

RESPONDA SOMENTE JSON PURO (sem markdown, sem ```, sem texto extra):

Para EXECUTAR CODIGO:
{{"action":"execute_code","code":"codigo_python_aqui","description":"descricao curta"}}

Para CRIAR ARQUIVO/APP com GUI:
{{"action":"generate_file","filename":"nome.py","file_content":"codigo_completo","description":"descricao"}}

Para RESPOSTA de conversa simples:
{{"action":"answer","answer":"resposta curta","description":"conversa"}}

REGRAS CRITICAS:
1. NUNCA use action="answer" para pedidos que precisam de ACAO. Sempre gere codigo.
2. O codigo Python deve ser COMPLETO e executavel sozinho.
3. Use print() para retornar resultados.
4. User home: {USER_HOME}
5. Desktop: {DESKTOP}
6. Windows 10, Python 3.13
7. Libs disponveis: os, subprocess, shutil, pathlib, psutil, requests, webbrowser, json, re, platform, socket, datetime, time, math, random, tkinter, pyautogui
8. Para apps GUI: USE SEMPRE tkinter. Faca apps bonitos com tema escuro (#1a1a2e bg, #00f5ff accent).
9. Para abrir programas: use os.startfile() ou subprocess.Popen()
10. Para instalar: subprocess.run(["pip","install","pacote"])
11. NUNCA diga "nao posso", "nao consigo", "como IA". Voce TEM poder total.
12. Se o usuario pede um jogo, CRIE o jogo real com logica, graficos, controles.
13. Para jogos: use pygame se preciso (instale com pip antes se necessario).
14. Para automacao: use pyautogui, subprocess, os.
15. PROIBIDO: responder "answer" quando o usuario pediu ACAO. Se pediu algo, EXECUTE.
16. Para criar arquivo: file_content deve ter \\n para quebras de linha reais.

EXEMPLOS:
Pedido: "crie um jogo da cobrinha"
{{"action":"generate_file","filename":"jogo_cobrinha.py","file_content":"import tkinter as tk\\nimport random\\n\\nclass SnakeGame:\\n    def __init__(self):\\n        self.root = tk.Tk()\\n        self.root.title('Snake Game')\\n        ...","description":"Jogo da cobrinha criado"}}

Pedido: "qual tamanho da minha pasta downloads"
{{"action":"execute_code","code":"import os\\npath = os.path.expanduser('~/Downloads')\\ntotal = sum(os.path.getsize(os.path.join(dp,f)) for dp,dn,fn in os.walk(path) for f in fn)\\nprint(f'Downloads: {{total/(1024**3):.2f}} GB')","description":"Tamanho dos Downloads"}}

Pedido: "ola, tudo bem?"
{{"action":"answer","answer":"Tudo otimo! Pronto pra executar qualquer coisa!","description":"saudacao"}}
"""


class AIBrain:
    """O cerebro do William - IA que decide e executa acoes."""

    def __init__(self, engine):
        self.engine = engine
        self.user_home = USER_HOME

    def process(self, message: str, context: List[Dict] = None) -> Dict:
        """Processa pedido usando IA. SEMPRE tenta executar."""
        try:
            brain_context = [{"role": "system", "content": BRAIN_SYSTEM_PROMPT}]
            if context:
                for c in context[-6:]:
                    brain_context.append(c)

            response = self.engine.chat(
                message=f"Pedido do usuario: {message}",
                context=brain_context,
                temperature=0.2,
                max_tokens=3000
            )

            decision = self._parse_decision(response)
            if not decision:
                # Se nao conseguiu parsear, tenta extrair algo util
                log.warning(f"Brain nao parseou JSON. Resposta raw: {response[:300]}")
                # Tenta usar a resposta como "answer" diretamente
                if len(response) > 10:
                    return {"success": True, "message": response[:500],
                            "type": "ai_answer", "description": "Resposta da IA"}
                return {"success": False, "message": "Nao consegui processar.",
                        "type": "error"}

            action = decision.get("action", "answer")
            desc = decision.get("description", "Executando...")

            if action == "execute_code":
                return self._execute_code(decision.get("code", ""), desc)
            elif action == "generate_file":
                return self._generate_file(decision, desc)
            elif action == "web_search":
                return self._do_web_search(decision.get("query", message), desc)
            elif action == "answer":
                return {"success": True, "message": decision.get("answer", ""),
                        "type": "ai_answer", "description": desc}
            else:
                return {"success": False, "message": f"Acao desconhecida: {action}",
                        "type": "error"}

        except Exception as e:
            log.error(f"AIBrain erro: {e}")
            return {"success": False, "message": f"Erro ao processar: {e}",
                    "type": "error"}

    def _parse_decision(self, response: str) -> Optional[Dict]:
        """Extrai JSON da resposta da IA. Mais robusto."""
        response = response.strip()

        # Remove markdown fencing
        if response.startswith("```"):
            response = re.sub(r'^```\w*\n?', '', response)
            response = re.sub(r'\n?```$', '', response)
            response = response.strip()

        # Tenta parse direto
        try:
            return json.loads(response)
        except:
            pass

        # Tenta encontrar JSON dentro do texto
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass

        # Tenta com regex mais agressivo
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            candidate = json_match.group()
            # Tenta consertar JSON com aspas simples
            candidate = candidate.replace("'", '"')
            try:
                return json.loads(candidate)
            except:
                pass

        return None

    def _execute_code(self, code: str, description: str) -> Dict:
        """Executa codigo Python gerado pela IA."""
        if not code or len(code.strip()) < 5:
            return {"success": False, "message": "Codigo vazio",
                    "type": "error"}

        # Decodifica escapes
        code = code.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"')

        log.info(f"AIBrain executando: {description}")

        try:
            # Verifica se precisa instalar algo primeiro
            imports = re.findall(r'(?:import|from)\s+(\w+)', code)
            needs_install = []
            pip_packages = {"pygame": "pygame", "PIL": "Pillow", "cv2": "opencv-python",
                           "numpy": "numpy", "pandas": "pandas", "matplotlib": "matplotlib",
                           "scipy": "scipy", "sklearn": "scikit-learn"}
            for imp in imports:
                if imp in pip_packages:
                    try:
                        __import__(imp)
                    except ImportError:
                        needs_install.append(pip_packages[imp])

            if needs_install:
                for pkg in needs_install:
                    log.info(f"Instalando pacote: {pkg}")
                    subprocess.run(
                        [os.path.join(USER_HOME, "Desktop", "WILTOP", "venv", "Scripts", "pip.exe"),
                         "install", pkg],
                        capture_output=True, timeout=60
                    )

            result = subprocess.run(
                [os.path.join(USER_HOME, "Desktop", "WILTOP", "venv", "Scripts", "python.exe"),
                 "-c", code],
                capture_output=True, text=True, timeout=30,
                cwd=self.user_home,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if result.returncode == 0:
                msg = output if output else f"Executado: {description}"
                return {"success": True, "message": f"[OK] {msg}",
                        "type": "ai_execute", "description": description}
            else:
                err_lines = error.split('\n')
                err_msg = err_lines[-1] if err_lines else "Erro"
                return {"success": False,
                        "message": f"[ERRO] {err_msg}",
                        "type": "error", "description": description}

        except subprocess.TimeoutExpired:
            return {"success": False, "message": "[ERRO] Timeout (30s)",
                    "type": "error"}
        except Exception as e:
            return {"success": False, "message": f"[ERRO] {e}",
                    "type": "error"}

    def _generate_file(self, decision: Dict, description: str) -> Dict:
        """Gera arquivo no Desktop e executa se for .py."""
        filename = decision.get("filename", "script.py")
        content = decision.get("file_content", "")

        if not content:
            return {"success": False, "message": "Conteudo vazio", "type": "error"}

        # Decodifica escapes de forma segura
        content = content.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"')
        content = content.replace("\\\\", "\\")

        filepath = os.path.join(DESKTOP, filename)
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            Path(filepath).write_text(content, encoding="utf-8")

            # Se e .py, executa
            if filename.endswith(".py"):
                python_exe = os.path.join(USER_HOME, "Desktop", "WILTOP", "venv", "Scripts", "python.exe")

                # Verifica se precisa instalar dependencias
                imports = re.findall(r'(?:import|from)\s+(\w+)', content)
                pip_packages = {"pygame": "pygame", "PIL": "Pillow", "cv2": "opencv-python",
                               "numpy": "numpy", "pandas": "pandas", "matplotlib": "matplotlib"}
                for imp in imports:
                    if imp in pip_packages:
                        try:
                            __import__(imp)
                        except ImportError:
                            pip_exe = os.path.join(USER_HOME, "Desktop", "WILTOP", "venv", "Scripts", "pip.exe")
                            subprocess.run([pip_exe, "install", pip_packages[imp]],
                                         capture_output=True, timeout=60)

                subprocess.Popen([python_exe, filepath])
                return {"success": True,
                        "message": f"[OK] Criado e executando: {filepath}",
                        "type": "ai_generate", "description": description}
            elif filename.endswith((".html", ".htm")):
                import webbrowser
                webbrowser.open(filepath)
                return {"success": True,
                        "message": f"[OK] Criado e aberto: {filepath}",
                        "type": "ai_generate", "description": description}
            else:
                return {"success": True,
                        "message": f"[OK] Arquivo criado: {filepath}",
                        "type": "ai_generate", "description": description}
        except Exception as e:
            return {"success": False, "message": f"[ERRO] {e}", "type": "error"}

    def _do_web_search(self, query: str, description: str) -> Dict:
        """Busca web e usa IA para resumir."""
        try:
            from src.core.web_search import get_web_search
            ws = get_web_search()
            result = ws.search(query)

            if result["success"]:
                raw = result["answer"][:1200]
                try:
                    summary = self.engine.chat(
                        message=f"Resuma em 3 linhas esta info sobre '{query}':\n{raw}",
                        context=[{"role": "system",
                                  "content": "Resuma em portugues. ULTRA conciso. Max 3 linhas."}],
                        temperature=0.3, max_tokens=300
                    )
                    return {"success": True,
                            "message": f"[OK] {summary}\n\n[Fonte: {result.get('source', 'Web')}]",
                            "type": "web_answer", "description": description}
                except:
                    return {"success": True,
                            "message": f"[OK] {raw[:600]}\n\n[Fonte: {result.get('source', 'Web')}]",
                            "type": "web_answer", "description": description}
            else:
                return {"success": False,
                        "message": "[INFO] Nao encontrei resultados.",
                        "type": "ask_user"}
        except Exception as e:
            return {"success": False, "message": f"[ERRO] Busca: {e}", "type": "error"}


_brain = None

def get_brain(engine=None):
    global _brain
    if _brain is None and engine:
        _brain = AIBrain(engine)
    return _brain
