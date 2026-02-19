"""
Módulo de controle total do sistema.
Permite executar QUALQUER operação no PC (quando autorizado).
"""

import os
import subprocess
import psutil
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import winreg  # Windows only
    WINDOWS = True
except ImportError:
    WINDOWS = False

from src.utils.logger import get_logger
from src.utils.exceptions import SystemOperationError

log = get_logger(__name__)


class SystemController:
    """
    Controlador completo do sistema.

    ATENÇÃO: Este módulo tem acesso total ao sistema!
    Use apenas quando autorizado pelo usuário.
    """

    def __init__(self):
        """Inicializa o controlador de sistema."""
        self.authorized = False
        log.info("SystemController inicializado (não autorizado)")

    def authorize(self):
        """Autoriza execução de comandos do sistema."""
        self.authorized = True
        log.warning("SystemController AUTORIZADO - acesso total ao sistema")

    def execute_command(self, command: str, shell: bool = True) -> Dict[str, Any]:
        """
        Executa comando do Windows.

        Args:
            command: Comando a executar
            shell: Se True, executa via shell

        Returns:
            Dicionário com resultado (stdout, stderr, returncode)

        Raises:
            SystemOperationError: Se não autorizado ou erro na execução
        """
        if not self.authorized:
            raise SystemOperationError("Operação não autorizada. Use .authorize() primeiro.")

        try:
            log.info(f"Executando comando: {command}")

            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }

        except subprocess.TimeoutExpired:
            raise SystemOperationError("Comando expirou (timeout)")
        except Exception as e:
            raise SystemOperationError(f"Erro ao executar comando: {str(e)}")

    def list_files(self, directory: str, pattern: str = "*") -> List[Dict[str, Any]]:
        """
        Lista arquivos em um diretório.

        Args:
            directory: Caminho do diretório
            pattern: Padrão de busca (ex: *.txt)

        Returns:
            Lista de dicionários com informações dos arquivos
        """
        try:
            path = Path(directory)
            if not path.exists():
                return []

            files = []
            for item in path.glob(pattern):
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "size": stat.st_size,
                    "is_dir": item.is_dir(),
                    "modified": stat.st_mtime
                })

            log.info(f"Listados {len(files)} arquivos em {directory}")
            return files

        except Exception as e:
            raise SystemOperationError(f"Erro ao listar arquivos: {str(e)}")

    def create_file(self, filepath: str, content: str = "") -> bool:
        """
        Cria um arquivo.

        Args:
            filepath: Caminho do arquivo
            content: Conteúdo do arquivo

        Returns:
            True se criado com sucesso
        """
        if not self.authorized:
            raise SystemOperationError("Operação não autorizada")

        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            log.info(f"Arquivo criado: {filepath}")
            return True
        except Exception as e:
            raise SystemOperationError(f"Erro ao criar arquivo: {str(e)}")

    def delete_file(self, filepath: str) -> bool:
        """
        Deleta um arquivo.

        Args:
            filepath: Caminho do arquivo

        Returns:
            True se deletado com sucesso
        """
        if not self.authorized:
            raise SystemOperationError("Operação não autorizada")

        try:
            path = Path(filepath)
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                log.info(f"Arquivo/diretório deletado: {filepath}")
                return True
            return False
        except Exception as e:
            raise SystemOperationError(f"Erro ao deletar: {str(e)}")

    def move_file(self, source: str, destination: str) -> bool:
        """
        Move ou renomeia arquivo.

        Args:
            source: Caminho origem
            destination: Caminho destino

        Returns:
            True se movido com sucesso
        """
        if not self.authorized:
            raise SystemOperationError("Operação não autorizada")

        try:
            shutil.move(source, destination)
            log.info(f"Arquivo movido: {source} -> {destination}")
            return True
        except Exception as e:
            raise SystemOperationError(f"Erro ao mover arquivo: {str(e)}")

    def copy_file(self, source: str, destination: str) -> bool:
        """
        Copia arquivo.

        Args:
            source: Caminho origem
            destination: Caminho destino

        Returns:
            True se copiado com sucesso
        """
        try:
            if Path(source).is_file():
                shutil.copy2(source, destination)
            else:
                shutil.copytree(source, destination)
            log.info(f"Arquivo copiado: {source} -> {destination}")
            return True
        except Exception as e:
            raise SystemOperationError(f"Erro ao copiar: {str(e)}")

    def list_processes(self) -> List[Dict[str, Any]]:
        """
        Lista processos em execução.

        Returns:
            Lista de processos
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    info = proc.info
                    processes.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "cpu": info['cpu_percent'],
                        "memory": info['memory_info'].rss if info['memory_info'] else 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return processes
        except Exception as e:
            raise SystemOperationError(f"Erro ao listar processos: {str(e)}")

    def kill_process(self, pid: int) -> bool:
        """
        Encerra um processo.

        Args:
            pid: ID do processo

        Returns:
            True se encerrado com sucesso
        """
        if not self.authorized:
            raise SystemOperationError("Operação não autorizada")

        try:
            proc = psutil.Process(pid)
            proc.kill()
            log.warning(f"Processo {pid} encerrado")
            return True
        except psutil.NoSuchProcess:
            return False
        except Exception as e:
            raise SystemOperationError(f"Erro ao encerrar processo: {str(e)}")

    def open_application(self, app_path: str) -> bool:
        """
        Abre uma aplicação.

        Args:
            app_path: Caminho ou nome da aplicação

        Returns:
            True se aberto com sucesso
        """
        if not self.authorized:
            raise SystemOperationError("Operação não autorizada")

        try:
            os.startfile(app_path)
            log.info(f"Aplicação aberta: {app_path}")
            return True
        except Exception as e:
            raise SystemOperationError(f"Erro ao abrir aplicação: {str(e)}")

    def get_system_info(self) -> Dict[str, Any]:
        """
        Retorna informações do sistema.

        Returns:
            Dicionário com informações do sistema
        """
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "cpu_count": psutil.cpu_count(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "boot_time": psutil.boot_time()
            }
        except Exception as e:
            raise SystemOperationError(f"Erro ao obter info do sistema: {str(e)}")

    def create_directory(self, path: str) -> bool:
        """
        Cria um diretório.

        Args:
            path: Caminho do diretório

        Returns:
            True se criado com sucesso
        """
        if not self.authorized:
            raise SystemOperationError("Operação não autorizada")

        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            log.info(f"Diretório criado: {path}")
            return True
        except Exception as e:
            raise SystemOperationError(f"Erro ao criar diretório: {str(e)}")

    def search_files(self, directory: str, filename: str) -> List[str]:
        """
        Busca arquivos por nome.

        Args:
            directory: Diretório para buscar
            filename: Nome do arquivo (pode usar wildcards)

        Returns:
            Lista de caminhos encontrados
        """
        try:
            path = Path(directory)
            found = []
            for item in path.rglob(filename):
                found.append(str(item))

            log.info(f"Encontrados {len(found)} arquivos com padrão {filename}")
            return found
        except Exception as e:
            raise SystemOperationError(f"Erro na busca: {str(e)}")

    def read_file(self, filepath: str) -> str:
        """
        Lê conteúdo de um arquivo.

        Args:
            filepath: Caminho do arquivo

        Returns:
            Conteúdo do arquivo
        """
        try:
            return Path(filepath).read_text(encoding='utf-8')
        except Exception as e:
            raise SystemOperationError(f"Erro ao ler arquivo: {str(e)}")

    def write_file(self, filepath: str, content: str) -> bool:
        """
        Escreve em um arquivo (sobrescreve).

        Args:
            filepath: Caminho do arquivo
            content: Conteúdo a escrever

        Returns:
            True se escrito com sucesso
        """
        if not self.authorized:
            raise SystemOperationError("Operação não autorizada")

        try:
            Path(filepath).write_text(content, encoding='utf-8')
            log.info(f"Arquivo escrito: {filepath}")
            return True
        except Exception as e:
            raise SystemOperationError(f"Erro ao escrever arquivo: {str(e)}")


# Instância global
_controller = None


def get_system_controller(authorized: bool = False) -> SystemController:
    """
    Retorna instância global do controlador de sistema.

    Args:
        authorized: Se True, autoriza operações do sistema

    Returns:
        Instância do SystemController
    """
    global _controller
    if _controller is None:
        _controller = SystemController()

    if authorized and not _controller.authorized:
        _controller.authorize()

    return _controller
