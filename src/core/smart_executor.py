"""
Executor inteligente que interpreta pedidos em linguagem natural
e executa ações no sistema.
"""

import re
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.modules.system.system_control import get_system_controller
from src.utils.logger import get_logger

log = get_logger(__name__)


class SmartExecutor:
    """
    Executor inteligente que entende comandos em linguagem natural.
    """

    def __init__(self, authorized: bool = False):
        """Inicializa o executor."""
        self.authorized = authorized
        self.system = get_system_controller(authorized=authorized)
        self.user_home = str(Path.home())
        log.info(f"SmartExecutor inicializado (autorizado: {authorized})")

    def check_authorization(self):
        """Verifica se há arquivo de autorização."""
        auth_file = Path(__file__).parent.parent.parent / ".authorized"
        if auth_file.exists():
            self.authorized = True
            self.system.authorize()
            log.info("Sistema AUTORIZADO via arquivo .authorized")
            return True
        return False

    def interpret_and_execute(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """
        Interpreta a resposta da IA e executa ações se necessário.

        Args:
            user_message: Mensagem do usuário
            ai_response: Resposta da IA

        Returns:
            Resultado da execução
        """
        log.info(f"=== INTERPRET AND EXECUTE ===")
        log.info(f"self.authorized: {self.authorized}")
        log.info(f"self.system.authorized: {self.system.authorized}")
        log.info(f"Mensagem: {user_message}")

        # Verifica autorizacao
        if not self.authorized:
            log.info("Executor NAO autorizado, tentando check_authorization()...")
            self.check_authorization()
            log.info(f"Apos check: self.authorized={self.authorized}, system.authorized={self.system.authorized}")

        if not self.authorized:
            log.warning("Sistema AINDA NAO autorizado apos check!")
            return {
                "executed": False,
                "message": "Sistema não autorizado. Execute AUTORIZAR_TUDO.py primeiro.",
                "response": ai_response
            }

        # Detecta intenções do usuário
        actions = self._detect_actions(user_message.lower())
        log.info(f"Acoes detectadas: {len(actions)}")

        if not actions:
            log.info("Nenhuma acao detectada, retornando resposta normal")
            return {
                "executed": False,
                "response": ai_response
            }

        # Executa ações detectadas
        results = []
        for action in actions:
            try:
                log.info(f"Executando acao: {action}")
                result = self._execute_action(action)
                log.info(f"Resultado: {result}")
                results.append(result)
            except Exception as e:
                log.error(f"Erro ao executar ação: {e}", exc_info=True)
                results.append({"success": False, "error": str(e)})

        log.info(f"Total de resultados: {len(results)}")
        return {
            "executed": True,
            "actions": results,
            "response": ai_response,
            "enhanced_response": self._enhance_response(ai_response, results)
        }

    def _detect_actions(self, message: str) -> List[Dict[str, Any]]:
        """
        Detecta ações que o usuário quer executar.

        Args:
            message: Mensagem do usuário em minúsculas

        Returns:
            Lista de ações detectadas
        """
        actions = []

        # Palavras-chave para abrir programas (muito mais variações!)
        open_keywords = ["abra", "abrir", "abre", "execute", "executar", "executa", "inicie", "iniciar", "inicia", "rode", "rodar", "roda", "lance", "lancar", "lanca", "liga", "ligar", "start"]

        # Abrir programas - MUITAS variações!
        if any(word in message for word in open_keywords):
            # Bloco de Notas
            if any(word in message for word in ["bloco", "notas", "notepad", "notes"]):
                actions.append({"type": "open", "target": "notepad.exe"})
            # Calculadora
            elif any(word in message for word in ["calculadora", "calc", "calcular"]):
                actions.append({"type": "open", "target": "calc.exe"})
            # Chrome/Navegador
            elif any(word in message for word in ["chrome", "navegador", "browser", "internet"]):
                actions.append({"type": "open", "target": "chrome.exe"})
            # Excel
            elif any(word in message for word in ["excel", "planilha"]):
                actions.append({"type": "open", "target": "excel.exe"})
            # Word
            elif any(word in message for word in ["word", "documento"]):
                actions.append({"type": "open", "target": "winword.exe"})
            # Explorer
            elif any(word in message for word in ["explorador", "explorer", "pasta", "arquivos"]):
                actions.append({"type": "open", "target": "explorer.exe"})
            # CMD
            elif any(word in message for word in ["cmd", "prompt", "terminal", "console"]):
                actions.append({"type": "open", "target": "cmd.exe"})

        # Criar arquivos - MUITAS variações!
        create_keywords = ["crie", "criar", "cria", "faca", "fazer", "faz", "novo arquivo", "novo", "gerar", "gera", "gere"]
        if any(word in message for word in create_keywords):
            # Tenta extrair nome do arquivo com múltiplos padrões
            patterns = [
                r'(?:arquivo|chamado|nome|chamada)\s+([a-zA-Z0-9_-]+\.\w+)',
                r'([a-zA-Z0-9_-]+\.txt)',
                r'([a-zA-Z0-9_-]+\.docx)',
                r'([a-zA-Z0-9_-]+\.\w+)'
            ]

            filename = None
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    filename = match.group(1)
                    break

            if filename:
                # Determina local (área de trabalho por padrão)
                if any(word in message for word in ["area de trabalho", "desktop", "trabalho"]):
                    filepath = os.path.join(self.user_home, "Desktop", filename)
                elif any(word in message for word in ["documentos", "documents", "meus documentos"]):
                    filepath = os.path.join(self.user_home, "Documents", filename)
                elif any(word in message for word in ["downloads"]):
                    filepath = os.path.join(self.user_home, "Downloads", filename)
                else:
                    # Padrão: área de trabalho
                    filepath = os.path.join(self.user_home, "Desktop", filename)

                actions.append({"type": "create_file", "path": filepath, "content": ""})

        # Listar arquivos - MUITAS variações!
        list_keywords = ["liste", "listar", "lista", "mostre", "mostrar", "mostra", "exiba", "exibir", "exibe", "quais", "ver", "veja"]
        if any(word in message for word in list_keywords) and any(word in message for word in ["arquivo", "arquivos", "pasta", "pastas", "conteudo"]):
            if any(word in message for word in ["downloads", "download"]):
                path = os.path.join(self.user_home, "Downloads")
            elif any(word in message for word in ["documentos", "documents", "meus documentos"]):
                path = os.path.join(self.user_home, "Documents")
            elif any(word in message for word in ["area de trabalho", "desktop", "trabalho"]):
                path = os.path.join(self.user_home, "Desktop")
            elif any(word in message for word in ["imagens", "pictures", "fotos"]):
                path = os.path.join(self.user_home, "Pictures")
            else:
                path = self.user_home

            actions.append({"type": "list_files", "path": path})

        # Informações do sistema - MUITAS variações!
        info_keywords = ["memoria", "ram", "cpu", "processador", "disco", "sistema", "espaco", "uso", "quanto", "informacao", "informacoes", "status"]
        if any(word in message for word in info_keywords):
            # Só adiciona se realmente pedir info do sistema
            if any(word in message for word in ["memoria", "ram", "cpu", "disco", "espaco", "sistema", "processador"]):
                actions.append({"type": "system_info"})

        # Comandos diretos - MUITAS variações!
        if any(message.startswith(prefix) for prefix in ["cmd:", "execute:", "comando:", "exec:", "run:"]):
            command = message.split(":", 1)[1].strip()
            actions.append({"type": "command", "command": command})

        # Detecção de comando dir/tasklist/ipconfig diretamente
        if any(cmd in message for cmd in ["comando dir", "execute dir", "rode dir"]):
            actions.append({"type": "command", "command": "dir"})
        elif any(cmd in message for cmd in ["tasklist", "processos", "programas abertos"]):
            actions.append({"type": "command", "command": "tasklist"})
        elif any(cmd in message for cmd in ["ipconfig", "ip", "rede", "network"]):
            actions.append({"type": "command", "command": "ipconfig"})

        log.info(f"Acoes detectadas: {len(actions)} - {actions}")
        return actions

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ação específica.

        Args:
            action: Dicionário com tipo e parâmetros da ação

        Returns:
            Resultado da execução
        """
        action_type = action["type"]

        try:
            if action_type == "open":
                target = action["target"]
                self.system.open_application(target)
                return {
                    "success": True,
                    "type": "open",
                    "message": f"[OK] {target} aberto com sucesso!"
                }

            elif action_type == "create_file":
                filepath = action["path"]
                content = action.get("content", "")
                self.system.create_file(filepath, content)
                return {
                    "success": True,
                    "type": "create_file",
                    "message": f"[OK] Arquivo criado: {filepath}"
                }

            elif action_type == "list_files":
                path = action["path"]
                files = self.system.list_files(path)
                file_list = "\n".join([f"  - {f['name']}" for f in files[:20]])
                return {
                    "success": True,
                    "type": "list_files",
                    "message": f"[OK] Arquivos em {path}:\n{file_list}",
                    "count": len(files)
                }

            elif action_type == "system_info":
                info = self.system.get_system_info()
                message = f"""[OK] Informacoes do Sistema:
  CPU: {info['cpu_percent']}% em uso ({info['cpu_count']} nucleos)
  RAM: {info['memory']['percent']}% em uso
  Disco: {info['disk']['percent']}% em uso"""
                return {
                    "success": True,
                    "type": "system_info",
                    "message": message
                }

            elif action_type == "command":
                command = action["command"]
                result = self.system.execute_command(command)
                return {
                    "success": result["success"],
                    "type": "command",
                    "message": f"[OK] Comando executado:\n{result['stdout'][:500]}"
                }

            else:
                return {
                    "success": False,
                    "error": f"Tipo de ação desconhecido: {action_type}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _enhance_response(self, ai_response: str, results: List[Dict]) -> str:
        """
        Adiciona resultados de execução à resposta da IA.

        Args:
            ai_response: Resposta original da IA
            results: Resultados das execuções

        Returns:
            Resposta melhorada
        """
        enhanced = ai_response + "\n\n"

        for result in results:
            if result.get("success"):
                enhanced += f"\n{result.get('message', '')}"
            else:
                enhanced += f"\n[ERRO] Erro: {result.get('error', 'Desconhecido')}"

        return enhanced


# Instância global
_smart_executor = None


def get_smart_executor(authorized: bool = False) -> SmartExecutor:
    """Retorna instância global do executor inteligente."""
    global _smart_executor
    if _smart_executor is None:
        log.info(f"Criando NOVA instancia do SmartExecutor com authorized={authorized}")
        _smart_executor = SmartExecutor(authorized=authorized)
    else:
        log.info(f"Reutilizando instancia existente. Estado atual: authorized={_smart_executor.authorized}")
        # SEMPRE atualiza se o parametro pedir autorizacao
        if authorized and not _smart_executor.authorized:
            log.info("ATUALIZANDO executor para authorized=True")
            _smart_executor.authorized = True
            _smart_executor.system.authorize()

    log.info(f"get_smart_executor retornando executor com authorized={_smart_executor.authorized}")
    return _smart_executor
