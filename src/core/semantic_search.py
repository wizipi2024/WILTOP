"""
Semantic Search - Busca hibrida keyword + embeddings.
Fallback para keyword se sentence-transformers nao instalado.
Item 5 do plano arquitetural.
"""

import re
import math
from typing import Dict, List, Optional, Tuple
from collections import Counter
from src.utils.logger import get_logger

log = get_logger(__name__)

# Tenta importar sentence-transformers (OPCIONAL)
_embeddings_available = False
_model = None

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _embeddings_available = True
    log.info("sentence-transformers disponivel - busca semantica ativada")
except ImportError:
    log.info("sentence-transformers nao instalado - usando busca por keyword")


# Stop words PT-BR para busca keyword
STOP_WORDS_PTBR = {
    "a", "o", "e", "de", "do", "da", "em", "um", "uma", "para", "com",
    "nao", "que", "se", "na", "no", "os", "as", "dos", "das", "por",
    "mais", "como", "mas", "foi", "ao", "ele", "ela", "ou", "ser",
    "quando", "muito", "ha", "nos", "ja", "eu", "tambem", "so",
    "pelo", "pela", "ate", "isso", "entre", "era", "depois", "sem",
    "mesmo", "aos", "ter", "seus", "sua", "seu", "nas", "esse",
    "esta", "este", "essa", "isso", "aqui", "eles", "elas",
    "voce", "me", "meu", "minha", "te", "tu", "nos", "vos",
    "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need",
    "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "an", "it", "its", "this", "that", "and", "or", "not",
}


def _tokenize(text: str) -> List[str]:
    """Tokeniza texto removendo stop words e pontuacao."""
    words = re.findall(r'\b[a-zA-Z\u00C0-\u00FF]{2,}\b', text.lower())
    return [w for w in words if w not in STOP_WORDS_PTBR]


def _keyword_score(query_tokens: List[str], doc_tokens: List[str]) -> float:
    """
    Calcula score BM25-like entre query e documento.
    Simplificado para performance.
    """
    if not query_tokens or not doc_tokens:
        return 0.0

    doc_counter = Counter(doc_tokens)
    doc_len = len(doc_tokens)
    avg_dl = 50.0  # Estimativa de tamanho medio

    k1 = 1.5
    b = 0.75
    score = 0.0

    for term in query_tokens:
        tf = doc_counter.get(term, 0)
        if tf == 0:
            continue

        # IDF simplificado (assume que termos da query sao importantes)
        idf = 1.0

        # BM25 formula simplificada
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * (doc_len / avg_dl))
        score += idf * (numerator / denominator)

    return score


def _exact_match_bonus(query: str, text: str) -> float:
    """Bonus para match exato da query."""
    query_lower = query.lower()
    text_lower = text.lower()

    if query_lower in text_lower:
        return 3.0
    return 0.0


class SemanticSearch:
    """
    Busca hibrida: keyword + embeddings (se disponivel).
    Funciona sem sentence-transformers (fallback keyword puro).
    """

    def __init__(self, use_embeddings: bool = True):
        """
        Args:
            use_embeddings: Se True, tenta usar embeddings.
                          Se False ou indisponivel, usa keyword.
        """
        self.use_embeddings = use_embeddings and _embeddings_available
        self._model = None
        self._embeddings_cache: Dict[str, list] = {}

        if self.use_embeddings:
            try:
                self._load_model()
            except Exception as e:
                log.warning(f"Falha ao carregar modelo de embeddings: {e}")
                self.use_embeddings = False

    def _load_model(self):
        """Carrega modelo de embeddings (lazy load)."""
        global _model
        if _model is None:
            log.info("Carregando modelo de embeddings...")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            log.info("Modelo de embeddings carregado")
        self._model = _model

    def _get_embedding(self, text: str) -> Optional[list]:
        """Gera embedding para texto."""
        if not self.use_embeddings or not self._model:
            return None

        if text in self._embeddings_cache:
            return self._embeddings_cache[text]

        try:
            embedding = self._model.encode(text).tolist()
            # Cache limitado
            if len(self._embeddings_cache) > 1000:
                # Remove metade do cache (FIFO simples)
                keys = list(self._embeddings_cache.keys())
                for k in keys[:500]:
                    del self._embeddings_cache[k]
            self._embeddings_cache[text] = embedding
            return embedding
        except Exception as e:
            log.debug(f"Erro ao gerar embedding: {e}")
            return None

    def _cosine_similarity(self, a: list, b: list) -> float:
        """Calcula similaridade coseno entre dois vetores."""
        if not a or not b or len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def search(self, query: str, documents: List[Dict],
               text_field: str = "content", limit: int = 10,
               min_score: float = 0.1) -> List[Tuple[Dict, float]]:
        """
        Busca hibrida nos documentos.

        Args:
            query: Texto de busca
            documents: Lista de dicts com campo texto
            text_field: Nome do campo de texto nos documentos
            limit: Maximo de resultados
            min_score: Score minimo para incluir

        Returns:
            Lista de (documento, score) ordenada por relevancia
        """
        if not query or not documents:
            return []

        query_tokens = _tokenize(query)
        results = []

        # Gera embedding da query (se disponivel)
        query_embedding = self._get_embedding(query) if self.use_embeddings else None

        for doc in documents:
            text = doc.get(text_field, "")
            if not text:
                continue

            # Score keyword (BM25-like)
            doc_tokens = _tokenize(text)
            kw_score = _keyword_score(query_tokens, doc_tokens)

            # Bonus match exato
            exact_bonus = _exact_match_bonus(query, text)

            # Score semantico (embeddings)
            sem_score = 0.0
            if query_embedding:
                doc_embedding = self._get_embedding(text[:500])  # Limita texto
                if doc_embedding:
                    sem_score = self._cosine_similarity(query_embedding, doc_embedding)

            # Score final: combina keyword + semantico + exact
            if self.use_embeddings and query_embedding:
                # 40% keyword + 40% semantico + 20% exact
                final_score = (kw_score * 0.4) + (sem_score * 5.0 * 0.4) + (exact_bonus * 0.2)
            else:
                # 70% keyword + 30% exact
                final_score = (kw_score * 0.7) + (exact_bonus * 0.3)

            if final_score >= min_score:
                results.append((doc, final_score))

        # Ordena por score
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def find_similar(self, text: str, documents: List[Dict],
                     text_field: str = "content", limit: int = 5) -> List[Tuple[Dict, float]]:
        """
        Encontra documentos similares a um texto dado.
        Util para "mais como este".

        Args:
            text: Texto de referencia
            documents: Lista de documentos
            text_field: Campo de texto
            limit: Maximo de resultados

        Returns:
            Lista de (documento, similaridade)
        """
        return self.search(text, documents, text_field, limit, min_score=0.05)

    def get_status(self) -> Dict:
        """Status do motor de busca."""
        return {
            "embeddings_available": _embeddings_available,
            "embeddings_active": self.use_embeddings,
            "model": "all-MiniLM-L6-v2" if self.use_embeddings else "keyword-only",
            "cache_size": len(self._embeddings_cache),
        }


# Singleton
_search_engine = None


def get_semantic_search() -> SemanticSearch:
    """Retorna singleton do SemanticSearch."""
    global _search_engine
    if _search_engine is None:
        _search_engine = SemanticSearch()
    return _search_engine
