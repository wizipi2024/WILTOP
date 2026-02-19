"""
Configurações centralizadas do Assistente IA William.

Este módulo carrega e valida todas as configurações do sistema
a partir de variáveis de ambiente e arquivos de configuração.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (override=True garante que sempre usa o .env atual)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


class Settings:
    """Classe central de configurações do sistema."""

    # ===== CAMINHOS =====
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / "data"
    MEMORY_DIR = DATA_DIR / "memory"
    LOGS_DIR = DATA_DIR / "logs"
    CACHE_DIR = DATA_DIR / "cache"
    EXPORTS_DIR = DATA_DIR / "exports"
    CONFIG_DIR = BASE_DIR / "config"

    # ===== API KEYS =====
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # ===== PROVEDOR IA PADRÃO =====
    DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "groq").lower()
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")

    # ===== CONFIGURAÇÕES DE PROVEDORES =====
    AI_PROVIDERS = {
        "groq": {
            "api_key": GROQ_API_KEY,
            "base_url": "https://api.groq.com/openai/v1",
            "models": [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "default_model": "llama-3.3-70b-versatile",
            "max_tokens": 8000,
            "timeout": 30
        },
        "anthropic": {
            "api_key": ANTHROPIC_API_KEY,
            "base_url": "https://api.anthropic.com",
            "models": [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "default_model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "timeout": 60
        },
        "openai": {
            "api_key": OPENAI_API_KEY,
            "base_url": "https://api.openai.com/v1",
            "models": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-4o"
            ],
            "default_model": "gpt-4-turbo-preview",
            "max_tokens": 4096,
            "timeout": 60
        }
    }

    # ===== MEMÓRIA =====
    MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", str(MEMORY_DIR / "memory.db"))
    MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
    MAX_MEMORY_ITEMS = int(os.getenv("MAX_MEMORY_ITEMS", "100"))
    ENABLE_SEMANTIC_SEARCH = os.getenv("ENABLE_SEMANTIC_SEARCH", "true").lower() == "true"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Modelo para embeddings

    # ===== LOGGING =====
    LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "william.log"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_ROTATION = "10 MB"
    LOG_RETENTION = "1 week"

    # ===== API REST SERVER =====
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "change_this_secret_key_in_production")
    API_CORS_ORIGINS = os.getenv("API_CORS_ORIGINS", "http://localhost:3000").split(",")

    # ===== TELEGRAM BOT =====
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ADMIN_IDS = [
        int(id.strip())
        for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")
        if id.strip()
    ]

    # ===== WHATSAPP BOT =====
    WHATSAPP_ENABLED = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"

    # ===== FUNCIONALIDADES =====
    ENABLE_WEB_SCRAPING = os.getenv("ENABLE_WEB_SCRAPING", "true").lower() == "true"
    ENABLE_FILE_OPERATIONS = os.getenv("ENABLE_FILE_OPERATIONS", "true").lower() == "true"
    ENABLE_SYSTEM_OPERATIONS = os.getenv("ENABLE_SYSTEM_OPERATIONS", "true").lower() == "true"
    ENABLE_AUTOMATION = os.getenv("ENABLE_AUTOMATION", "true").lower() == "true"
    ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "true").lower() == "true"

    # ===== LIMITES E SEGURANÇA =====
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))

    # ===== SEGURANCA v4 (Overhaul Arquitetural) =====
    SECURITY_MODE = os.getenv("SECURITY_MODE", "safe")  # "safe" ou "free"
    SANDBOX_BASE_DIRS = [
        str(Path.home() / "Desktop"),
        str(Path.home() / "Documents"),
        str(Path.home() / "Downloads"),
        str(Path.home() / "Pictures"),
        str(Path.home() / "Videos"),
        str(Path.home() / "Music"),
        str(Path.home() / ".william"),
    ]

    # ===== MULTI-PROVIDER v4 =====
    OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    PROVIDER_FALLBACK_ORDER = os.getenv(
        "PROVIDER_FALLBACK_ORDER", "groq,ollama,openai,anthropic"
    ).split(",")

    # ===== MODO MESCLADO v6 =====
    # false = so Groq (padrao, mais rapido)
    # true  = Groq + Ollama local (mais inteligente, economiza cota)
    MIXED_MODE = os.getenv("MIXED_MODE", "false").lower() == "true"

    # ===== OBSERVABILITY v4 =====
    EVENTS_LOG_DIR = str(DATA_DIR / "logs" / "events")
    EVENTS_RETENTION_DAYS = int(os.getenv("EVENTS_RETENTION_DAYS", "30"))

    # ===== TASKS v4 =====
    TASKS_DIR = str(DATA_DIR / "tasks")
    TASK_QUEUE_FILE = str(DATA_DIR / "tasks" / "task_queue.json")

    # ===== SKILLS v4 =====
    SKILLS_DIR = str(BASE_DIR / "src" / "skills")
    SKILL_CATALOG_FILE = str(BASE_DIR / "config" / "skill_catalog.json")

    # ===== BUSINESS v4 =====
    BUSINESS_DATA_DIR = str(DATA_DIR / "business")

    # ===== WEB SCRAPING =====
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    # ===== ANÁLISE DE DADOS =====
    DEFAULT_CHART_FORMAT = os.getenv("DEFAULT_CHART_FORMAT", "png")
    CHART_DPI = int(os.getenv("CHART_DPI", "300"))
    CHART_THEME = os.getenv("CHART_THEME", "darkgrid")

    # ===== AMBIENTE =====
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

    # ===== MÓDULOS HABILITADOS =====
    ENABLED_MODULES = [
        "documents",
        "system",
        "internet",
        "automation",
        "analysis"
    ]

    # ===== PROMPTS DO SISTEMA =====
    SYSTEM_PROMPT = """Você é William, um assistente IA avançado e profissional.

Suas capacidades incluem:
- Criar e editar documentos profissionais (Word, Excel, PDF, PowerPoint)
- Gerenciar arquivos e operações de sistema
- Pesquisar e extrair informações da web
- Automatizar tarefas repetitivas e complexas
- Analisar dados e gerar insights visuais

Diretrizes:
- Seja sempre útil, preciso e proativo
- Forneça respostas claras e bem estruturadas
- Quando executar ações, confirme o resultado
- Se encontrar problemas, explique e sugira alternativas
- Mantenha contexto de conversas anteriores
"""

    @classmethod
    def validate(cls) -> List[str]:
        """
        Valida configurações e retorna lista de erros/avisos.

        Returns:
            Lista de mensagens de validação
        """
        issues = []

        # Verifica API keys
        if not cls.GROQ_API_KEY and not cls.ANTHROPIC_API_KEY and not cls.OPENAI_API_KEY:
            issues.append("⚠️  NENHUMA API KEY configurada! Configure ao menos uma em .env")

        if cls.DEFAULT_AI_PROVIDER not in cls.AI_PROVIDERS:
            issues.append(f"❌ Provider padrão inválido: {cls.DEFAULT_AI_PROVIDER}")

        provider_config = cls.AI_PROVIDERS.get(cls.DEFAULT_AI_PROVIDER, {})
        if not provider_config.get("api_key"):
            issues.append(f"⚠️  API key não configurada para provider: {cls.DEFAULT_AI_PROVIDER}")

        # Verifica diretórios
        for dir_name in ["DATA_DIR", "MEMORY_DIR", "LOGS_DIR", "CACHE_DIR", "EXPORTS_DIR"]:
            dir_path = getattr(cls, dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                issues.append(f"✓ Diretório criado: {dir_path}")

        # Verifica configurações de segurança
        if cls.API_SECRET_KEY == "change_this_secret_key_in_production" and cls.ENVIRONMENT == "production":
            issues.append("❌ API_SECRET_KEY deve ser alterada em produção!")

        return issues

    @classmethod
    def get_provider_config(cls, provider_name: Optional[str] = None) -> Dict:
        """
        Retorna configuração de um provider específico.

        Args:
            provider_name: Nome do provider (se None, usa o padrão)

        Returns:
            Dicionário de configuração do provider
        """
        if provider_name is None:
            provider_name = cls.DEFAULT_AI_PROVIDER

        return cls.AI_PROVIDERS.get(provider_name.lower(), {})

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Retorna lista de providers com API keys configuradas.

        Returns:
            Lista de nomes de providers disponíveis
        """
        return [
            name
            for name, config in cls.AI_PROVIDERS.items()
            if config.get("api_key")
        ]

    @classmethod
    def is_module_enabled(cls, module_name: str) -> bool:
        """
        Verifica se um módulo está habilitado.

        Args:
            module_name: Nome do módulo

        Returns:
            True se habilitado
        """
        return module_name.lower() in [m.lower() for m in cls.ENABLED_MODULES]

    @classmethod
    def get_info(cls) -> Dict:
        """
        Retorna informações sobre configurações atuais.

        Returns:
            Dicionário com informações do sistema
        """
        return {
            "environment": cls.ENVIRONMENT,
            "default_provider": cls.DEFAULT_AI_PROVIDER,
            "default_model": cls.DEFAULT_MODEL,
            "available_providers": cls.get_available_providers(),
            "enabled_modules": cls.ENABLED_MODULES,
            "memory_enabled": cls.ENABLE_MEMORY,
            "semantic_search": cls.ENABLE_SEMANTIC_SEARCH,
            "log_level": cls.LOG_LEVEL
        }


# ===== INICIALIZAÇÃO =====

def init_settings() -> Settings:
    """
    Inicializa e valida configurações.

    Returns:
        Instância de Settings validada
    """
    settings = Settings()

    # Valida configurações
    issues = settings.validate()

    if issues:
        print("\n📋 Validação de Configurações:")
        for issue in issues:
            print(f"   {issue}")
        print()

    return settings


# Instância global de configurações
settings = init_settings()
