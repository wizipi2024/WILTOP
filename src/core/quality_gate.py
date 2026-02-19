"""
Quality Gate - Equipe Avaliadora Interna do William v5.

Valida resultados ANTES de entregar ao usuário.
Só libera quando a qualidade está boa o suficiente.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, List, Optional
from src.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class EvaluationResult:
    approved: bool
    score: float          # 0.0 a 10.0
    feedback: List[str]   # Lista de problemas encontrados
    result_type: str


class BaseEvaluator:
    """Avaliador base."""

    applies_to = []  # Tipos de resultado que este avaliador cobre

    def applies(self, result_type: str) -> bool:
        return result_type in self.applies_to or "all" in self.applies_to

    def score(self, content: str) -> float:
        return 8.0

    def feedback(self, content: str) -> List[str]:
        return []


class CopyEvaluator(BaseEvaluator):
    """Avalia qualidade de copy e mensagens de vendas."""

    applies_to = ["copy", "mensagem", "script", "proposta", "sequencia"]

    def score(self, content: str) -> float:
        score = 10.0
        issues = []

        # Verificações básicas
        if len(content) < 50:
            score -= 3.0
            issues.append("Muito curto")
        if not any(w in content.lower() for w in ["voce", "você", "seu", "sua"]):
            score -= 1.0  # Falta personalização
        if not any(w in content.lower() for w in ["clique", "responda", "entre", "acesse", "saiba", "agende", "ligue"]):
            score -= 1.5  # Falta CTA
        if len(content) > 2000:
            score -= 1.0  # Muito longo para mensagem

        return max(0.0, score)

    def feedback(self, content: str) -> List[str]:
        issues = []
        if len(content) < 50:
            issues.append("Copy muito curto - adicionar mais contexto")
        if not any(w in content.lower() for w in ["clique", "responda", "entre", "acesse", "saiba", "agende"]):
            issues.append("Falta CTA (call-to-action) claro")
        return issues


class StrategyEvaluator(BaseEvaluator):
    """Avalia qualidade de estratégias de negócio."""

    applies_to = ["estrategia", "modelo_negocio", "funil", "oferta"]

    def score(self, content: str) -> float:
        score = 10.0
        content_lower = content.lower()

        if len(content) < 100:
            score -= 3.0
        if not any(w in content_lower for w in ["nicho", "publico", "cliente", "segmento"]):
            score -= 1.5
        if not any(w in content_lower for w in ["r$", "ticket", "preco", "valor", "mensalidade"]):
            score -= 1.5
        if not any(w in content_lower for w in ["canal", "whatsapp", "instagram", "linkedin", "google"]):
            score -= 1.0

        return max(0.0, score)

    def feedback(self, content: str) -> List[str]:
        issues = []
        content_lower = content.lower()
        if not any(w in content_lower for w in ["nicho", "publico", "cliente"]):
            issues.append("Falta definição clara do público-alvo")
        if not any(w in content_lower for w in ["r$", "ticket", "preco", "valor"]):
            issues.append("Falta definição de ticket/preço")
        return issues


class N8nEvaluator(BaseEvaluator):
    """Avalia se JSON de workflow n8n é estruturalmente válido."""

    applies_to = ["n8n", "workflow", "automacao"]

    def score(self, content: str) -> float:
        try:
            # Tenta parsear como JSON
            if isinstance(content, str):
                data = json.loads(content)
            else:
                data = content

            score = 10.0
            if "nodes" not in data:
                score -= 4.0
            if "connections" not in data:
                score -= 2.0
            if not data.get("nodes"):
                score -= 4.0

            return max(0.0, score)
        except Exception:
            # Se não é JSON, avalia como texto descritivo
            if "webhook" in str(content).lower() or "node" in str(content).lower():
                return 7.0
            return 5.0

    def feedback(self, content: str) -> List[str]:
        try:
            data = json.loads(content) if isinstance(content, str) else content
            issues = []
            if "nodes" not in data:
                issues.append("Workflow sem nodes definidos")
            if "connections" not in data:
                issues.append("Workflow sem connections definidas")
            return issues
        except Exception:
            return []


class CodeEvaluator(BaseEvaluator):
    """Avalia qualidade básica de código gerado."""

    applies_to = ["code", "app", "script", "programa"]

    def score(self, content: str) -> float:
        score = 10.0
        content_lower = content.lower()

        if len(content) < 50:
            score -= 5.0
        # Sinais de código incompleto
        if "..." in content and len(content) < 200:
            score -= 3.0
        if "TODO" in content or "FIXME" in content:
            score -= 1.0
        # Sinais positivos
        if "def " in content or "class " in content or "<html" in content_lower:
            score = min(10.0, score + 0.5)

        return max(0.0, score)

    def feedback(self, content: str) -> List[str]:
        issues = []
        if len(content) < 50:
            issues.append("Código muito curto ou incompleto")
        if "TODO" in content:
            issues.append("Código com TODOs não implementados")
        return issues


class SecurityEvaluator(BaseEvaluator):
    """Garante que dados sensíveis não vazam."""

    applies_to = ["all"]

    SENSITIVE_PATTERNS = [
        r'password\s*=\s*["\'][^"\']{3,}',
        r'api_key\s*=\s*["\'][^"\']{10,}',
        r'secret\s*=\s*["\'][^"\']{10,}',
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # cartão
        r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b',  # CPF
    ]

    def score(self, content: str) -> float:
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, str(content), re.IGNORECASE):
                return 0.0  # Falha total se dado sensível exposto
        return 10.0

    def feedback(self, content: str) -> List[str]:
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, str(content), re.IGNORECASE):
                return ["ALERTA: Dado sensível detectado no resultado!"]
        return []


class QualityGate:
    """
    Equipe Avaliadora Interna do William.

    Valida resultados ANTES de entregar ao usuário.
    Cada avaliador tem critérios específicos por tipo de resultado.
    Só libera quando score >= 7.5 (ou após melhorias automáticas).
    """

    MIN_SCORE = 7.5
    MAX_RETRIES = 3

    def __init__(self):
        self.evaluators = [
            CopyEvaluator(),
            StrategyEvaluator(),
            N8nEvaluator(),
            CodeEvaluator(),
            SecurityEvaluator(),
        ]
        log.info("QualityGate inicializado com 5 avaliadores")

    def evaluate(self, result_type: str, content: Any) -> EvaluationResult:
        """
        Avalia um resultado antes de entregar ao usuário.

        Args:
            result_type: Tipo do resultado (copy, estrategia, n8n, code, etc)
            content: Conteúdo a avaliar

        Returns:
            EvaluationResult com approved, score e feedback
        """
        content_str = str(content)
        applicable = [e for e in self.evaluators if e.applies(result_type)]

        if not applicable:
            # Sem avaliadores específicos → aprovado automaticamente
            return EvaluationResult(
                approved=True, score=8.0, feedback=[], result_type=result_type
            )

        scores = [e.score(content_str) for e in applicable]
        feedbacks = []
        for e in applicable:
            feedbacks.extend(e.feedback(content_str))

        avg_score = sum(scores) / len(scores)
        approved = avg_score >= self.MIN_SCORE and not any("ALERTA" in f for f in feedbacks)

        log.info(f"QualityGate [{result_type}]: score={avg_score:.1f}/10, approved={approved}")

        return EvaluationResult(
            approved=approved,
            score=round(avg_score, 1),
            feedback=feedbacks,
            result_type=result_type,
        )

    def format_badge(self, result: EvaluationResult) -> str:
        """Formata badge de avaliação para exibir no chat."""
        if result.approved:
            return f"[Validado pela Equipe Avaliadora: {result.score}/10]"
        else:
            issues = " | ".join(result.feedback[:2]) if result.feedback else "Qualidade insuficiente"
            return f"[Em revisao: {result.score}/10 - {issues}]"


# Singleton
_quality_gate = None


def get_quality_gate() -> QualityGate:
    global _quality_gate
    if _quality_gate is None:
        _quality_gate = QualityGate()
    return _quality_gate
