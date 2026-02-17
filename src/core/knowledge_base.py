"""
Knowledge Base - Base de conhecimento verificada.
Fatos verificados vs hipoteses, com busca inteligente.
Item 22 do plano arquitetural.
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from src.utils.logger import get_logger

log = get_logger(__name__)

KB_FILE = os.path.join(
    str(Path.home()), "Desktop", "WILTOP", "data", "memory", "knowledge.json"
)


@dataclass
class KnowledgeFact:
    """Representa um fato na base de conhecimento."""

    id: str
    content: str                    # O fato em si
    category: str = "general"       # Categoria: general, tech, user, business, system
    source: str = "user"            # Fonte: user, web, ai, system, observation
    confidence: float = 1.0         # 0.0 (hipotese) a 1.0 (fato verificado)
    tags: List[str] = field(default_factory=list)
    related_facts: List[str] = field(default_factory=list)  # IDs de fatos relacionados
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0           # Quantas vezes foi acessado
    verified: bool = False          # Se foi verificado pelo usuario

    def to_dict(self) -> Dict:
        """Serializa para dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'KnowledgeFact':
        """Cria de dict."""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        # Garante que tags e related_facts sao listas
        if 'tags' in filtered and not isinstance(filtered['tags'], list):
            filtered['tags'] = []
        if 'related_facts' in filtered and not isinstance(filtered['related_facts'], list):
            filtered['related_facts'] = []
        return cls(**filtered)

    @property
    def is_verified(self) -> bool:
        """Se e fato verificado (confidence >= 0.8)."""
        return self.confidence >= 0.8 or self.verified

    @property
    def is_hypothesis(self) -> bool:
        """Se e hipotese (confidence < 0.5)."""
        return self.confidence < 0.5


class KnowledgeBase:
    """
    Base de conhecimento com fatos verificados e hipoteses.
    Persiste em JSON. Busca por keyword e categoria.
    """

    def __init__(self, kb_file: str = None):
        self.kb_file = kb_file or KB_FILE
        self.facts: Dict[str, KnowledgeFact] = {}
        self._load()

    def _load(self):
        """Carrega KB do arquivo."""
        try:
            if os.path.exists(self.kb_file):
                with open(self.kb_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for fact_data in data:
                    fact = KnowledgeFact.from_dict(fact_data)
                    self.facts[fact.id] = fact
                log.info(f"KnowledgeBase: {len(self.facts)} fatos carregados")
        except Exception as e:
            log.error(f"Erro ao carregar KB: {e}")
            self.facts = {}

    def _save(self):
        """Salva KB no arquivo."""
        try:
            os.makedirs(os.path.dirname(self.kb_file), exist_ok=True)
            data = [fact.to_dict() for fact in self.facts.values()]
            with open(self.kb_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f"Erro ao salvar KB: {e}")

    def add_fact(self, content: str, category: str = "general",
                 source: str = "user", confidence: float = 1.0,
                 tags: List[str] = None, verified: bool = False) -> KnowledgeFact:
        """
        Adiciona fato a base de conhecimento.

        Args:
            content: O fato/informacao
            category: general, tech, user, business, system
            source: user, web, ai, system, observation
            confidence: 0.0 a 1.0
            tags: Tags para busca
            verified: Se foi verificado pelo usuario

        Returns:
            KnowledgeFact criado
        """
        fact_id = f"kb_{int(time.time())}_{len(self.facts)}"
        fact = KnowledgeFact(
            id=fact_id,
            content=content,
            category=category,
            source=source,
            confidence=confidence,
            tags=tags or [],
            verified=verified,
        )
        self.facts[fact_id] = fact
        self._save()
        log.info(f"Fato adicionado: {fact_id} - {content[:60]}")
        return fact

    def add_hypothesis(self, content: str, category: str = "general",
                       source: str = "ai", tags: List[str] = None) -> KnowledgeFact:
        """Atalho para adicionar hipotese (confidence baixa)."""
        return self.add_fact(
            content=content,
            category=category,
            source=source,
            confidence=0.3,
            tags=tags,
            verified=False,
        )

    def verify_fact(self, fact_id: str, confidence: float = 1.0) -> bool:
        """Marca fato como verificado."""
        fact = self.facts.get(fact_id)
        if not fact:
            return False
        fact.verified = True
        fact.confidence = confidence
        fact.updated_at = datetime.now().isoformat()
        self._save()
        return True

    def update_fact(self, fact_id: str, content: str = None,
                    confidence: float = None, tags: List[str] = None) -> bool:
        """Atualiza um fato existente."""
        fact = self.facts.get(fact_id)
        if not fact:
            return False
        if content is not None:
            fact.content = content
        if confidence is not None:
            fact.confidence = confidence
        if tags is not None:
            fact.tags = tags
        fact.updated_at = datetime.now().isoformat()
        self._save()
        return True

    def remove_fact(self, fact_id: str) -> bool:
        """Remove fato da KB."""
        if fact_id in self.facts:
            del self.facts[fact_id]
            self._save()
            return True
        return False

    def query(self, query: str, category: str = None,
              min_confidence: float = 0.0, limit: int = 10) -> List[KnowledgeFact]:
        """
        Busca fatos na KB por keyword.

        Args:
            query: Texto de busca
            category: Filtrar por categoria (opcional)
            min_confidence: Confidence minima
            limit: Maximo de resultados

        Returns:
            Lista de fatos relevantes, ordenados por relevancia
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        results = []

        for fact in self.facts.values():
            # Filtro de categoria
            if category and fact.category != category:
                continue

            # Filtro de confidence
            if fact.confidence < min_confidence:
                continue

            # Calcula score de relevancia
            score = self._calculate_relevance(fact, query_lower, query_words)

            if score > 0:
                results.append((fact, score))

        # Ordena por score (maior primeiro)
        results.sort(key=lambda x: x[1], reverse=True)

        # Incrementa access_count dos resultados
        top_facts = []
        for fact, score in results[:limit]:
            fact.access_count += 1
            top_facts.append(fact)

        if top_facts:
            self._save()

        return top_facts

    def _calculate_relevance(self, fact: KnowledgeFact,
                             query_lower: str, query_words: set) -> float:
        """Calcula score de relevancia de um fato para uma query."""
        score = 0.0
        content_lower = fact.content.lower()

        # Match exato da query no conteudo
        if query_lower in content_lower:
            score += 5.0

        # Match de palavras individuais
        content_words = set(content_lower.split())
        common_words = query_words & content_words
        if common_words:
            score += len(common_words) * 1.5

        # Match em tags
        for tag in fact.tags:
            tag_lower = tag.lower()
            if tag_lower in query_lower or query_lower in tag_lower:
                score += 3.0
            elif any(w in tag_lower for w in query_words):
                score += 1.5

        # Bonus por confidence alta
        score *= (0.5 + fact.confidence * 0.5)

        # Bonus por verificado
        if fact.verified:
            score *= 1.2

        # Bonus por acesso frequente (popular)
        if fact.access_count > 5:
            score *= 1.1

        return score

    def get_by_category(self, category: str) -> List[KnowledgeFact]:
        """Retorna todos os fatos de uma categoria."""
        return [f for f in self.facts.values() if f.category == category]

    def get_verified_facts(self) -> List[KnowledgeFact]:
        """Retorna apenas fatos verificados."""
        return [f for f in self.facts.values() if f.is_verified]

    def get_hypotheses(self) -> List[KnowledgeFact]:
        """Retorna hipoteses nao verificadas."""
        return [f for f in self.facts.values() if f.is_hypothesis]

    def get_stats(self) -> Dict:
        """Estatisticas da KB."""
        total = len(self.facts)
        verified = sum(1 for f in self.facts.values() if f.is_verified)
        hypotheses = sum(1 for f in self.facts.values() if f.is_hypothesis)

        categories = {}
        sources = {}
        for fact in self.facts.values():
            categories[fact.category] = categories.get(fact.category, 0) + 1
            sources[fact.source] = sources.get(fact.source, 0) + 1

        return {
            "total": total,
            "verified": verified,
            "hypotheses": hypotheses,
            "categories": categories,
            "sources": sources,
        }

    def export_markdown(self) -> str:
        """Exporta KB em formato Markdown."""
        lines = ["# Knowledge Base - William AI\n"]
        lines.append(f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

        stats = self.get_stats()
        lines.append(f"**Total:** {stats['total']} fatos | "
                     f"**Verificados:** {stats['verified']} | "
                     f"**Hipoteses:** {stats['hypotheses']}\n")

        # Agrupa por categoria
        by_category = {}
        for fact in self.facts.values():
            by_category.setdefault(fact.category, []).append(fact)

        for category, facts in sorted(by_category.items()):
            lines.append(f"\n## {category.title()}\n")
            for fact in sorted(facts, key=lambda f: -f.confidence):
                status = "V" if fact.is_verified else ("?" if fact.is_hypothesis else "~")
                tags_str = f" [{', '.join(fact.tags)}]" if fact.tags else ""
                lines.append(f"- [{status}] {fact.content}{tags_str} "
                           f"(conf: {fact.confidence:.0%}, fonte: {fact.source})")

        return "\n".join(lines)


# Singleton
_knowledge_base = None


def get_knowledge_base() -> KnowledgeBase:
    """Retorna singleton da KnowledgeBase."""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base
