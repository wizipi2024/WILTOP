"""
NLP PT-BR - Processador de linguagem natural para Portugues Brasileiro.
Normaliza abreviacoes, girias, erros comuns e extrai intencoes.
Item 11 do plano arquitetural.
"""

import re
from typing import Dict, List, Optional, Tuple
from src.utils.logger import get_logger

log = get_logger(__name__)


# ============================================================
# Tabela de normalizacao PT-BR (abreviacoes, girias, erros)
# ============================================================
ABBREVIATIONS = {
    # Abreviacoes de internet/chat
    "vc": "voce",
    "vcs": "voces",
    "tb": "tambem",
    "tbm": "tambem",
    "pq": "porque",
    "pqp": "porque",
    "qdo": "quando",
    "qnd": "quando",
    "cmg": "comigo",
    "ctg": "contigo",
    "msg": "mensagem",
    "msgs": "mensagens",
    "msm": "mesmo",
    "mto": "muito",
    "mt": "muito",
    "blz": "beleza",
    "flw": "falou",
    "vlw": "valeu",
    "pfv": "por favor",
    "pfvr": "por favor",
    "pf": "por favor",
    "obg": "obrigado",
    "obgd": "obrigado",
    "obgda": "obrigada",
    "dps": "depois",
    "dpois": "depois",
    "hj": "hoje",
    "td": "tudo",
    "tds": "todos",
    "qm": "quem",
    "nd": "nada",
    "ngm": "ninguem",
    "neh": "nao e",
    "ne": "nao e",
    "sla": "sei la",
    "slk": "sei la",
    "tlgd": "ta ligado",
    "tmj": "estamos juntos",
    "sqn": "so que nao",
    "kd": "cade",
    "ctz": "certeza",
    "agr": "agora",
    "dnv": "de novo",
    "vrdd": "verdade",
    "vdd": "verdade",
    "mlr": "melhor",
    "cmk": "como assim",
    "qse": "quase",
    "bjs": "beijos",
    "abs": "abracos",
    "gnt": "gente",
    "p": "para",
    "pra": "para",
    "pro": "para o",
    "q": "que",
    "c": "com",

    # Girias tech
    "config": "configuracao",
    "configs": "configuracoes",
    "app": "aplicativo",
    "apps": "aplicativos",
    "net": "internet",
    "pc": "computador",
    "hd": "disco rigido",
    "ssd": "disco",

    # Girias de comando
    "deleta": "delete",
    "apaga": "apague",
    "abre": "abra",
    "fecha": "feche",
    "roda": "execute",
    "instala": "instale",
    "desinstala": "desinstale",
    "baixa": "baixe",
    "copia": "copie",
    "cola": "cole",
    "salva": "salve",
    "muda": "mude",
    "troca": "troque",
}

# Correcoes de erros comuns de digitacao PT-BR
COMMON_TYPOS = {
    "nao": "nao",
    "tanbem": "tambem",
    "fascilidade": "facilidade",
    "coneguir": "conseguir",
    "nessecario": "necessario",
    "progama": "programa",
    "progamas": "programas",
    "arqivo": "arquivo",
    "arqivos": "arquivos",
    "exclua": "exclua",
    "ecluir": "excluir",
    "pesqisa": "pesquisa",
    "pesqisar": "pesquisar",
    "compuador": "computador",
    "sisema": "sistema",
    "calculadra": "calculadora",
    "nagevador": "navegador",
}

# Expressoes informais -> formal
INFORMAL_TO_FORMAL = {
    "faz ai": "faca",
    "manda ai": "envie",
    "bora": "vamos",
    "da uma olhada": "verifique",
    "da um check": "verifique",
    "to precisando": "preciso",
    "to querendo": "quero",
    "ce pode": "voce pode",
    "pode me": "pode me",
    "tem como": "e possivel",
    "da pra": "e possivel",
    "se liga": "preste atencao",
}


class NLPProcessor:
    """
    Processador NLP para PT-BR.
    Normaliza texto e extrai intencoes.
    """

    def __init__(self):
        self._abbreviations = dict(ABBREVIATIONS)
        self._typos = dict(COMMON_TYPOS)
        self._informal = dict(INFORMAL_TO_FORMAL)

    def normalize(self, text: str) -> str:
        """
        Normaliza texto PT-BR.
        Expande abreviacoes, corrige girias, mantem significado.

        Args:
            text: Texto do usuario

        Returns:
            Texto normalizado
        """
        if not text or len(text) < 2:
            return text

        original = text
        result = text

        # 1. Expressoes informais (multi-palavra primeiro)
        result_lower = result.lower()
        for informal, formal in self._informal.items():
            if informal in result_lower:
                # Substitui case-insensitive
                pattern = re.compile(re.escape(informal), re.IGNORECASE)
                result = pattern.sub(formal, result)
                result_lower = result.lower()

        # 2. Abreviacoes (palavra por palavra)
        words = result.split()
        normalized_words = []
        for word in words:
            word_lower = word.lower().strip(".,!?;:")
            punctuation = ""
            for ch in ".,!?;:":
                if word.endswith(ch):
                    punctuation = ch
                    break

            if word_lower in self._abbreviations:
                replacement = self._abbreviations[word_lower]
                normalized_words.append(replacement + punctuation)
            elif word_lower in self._typos:
                replacement = self._typos[word_lower]
                normalized_words.append(replacement + punctuation)
            else:
                normalized_words.append(word)

        result = " ".join(normalized_words)

        # 3. Limpa espacos extras
        result = re.sub(r'\s+', ' ', result).strip()

        if result != original:
            log.debug(f"NLP normalize: '{original[:80]}' -> '{result[:80]}'")

        return result

    def extract_intent(self, text: str) -> Dict:
        """
        Extrai intencao do texto.
        Retorna: acao, alvo, modificadores.

        Args:
            text: Texto normalizado

        Returns:
            Dict com action, target, modifiers
        """
        text_lower = text.lower()

        intent = {
            "action": None,
            "target": None,
            "modifiers": [],
            "confidence": 0.0,
        }

        # Detecta acao principal
        action_map = {
            "criar": ["crie", "criar", "cria", "faca", "gere", "gerar", "monte"],
            "abrir": ["abra", "abrir", "abre", "abri", "execute", "rode", "inicie"],
            "fechar": ["feche", "fechar", "fecha", "encerre", "pare", "mate"],
            "deletar": ["delete", "deletar", "apague", "apagar", "remova", "remover", "exclua"],
            "pesquisar": ["pesquise", "pesquisar", "busque", "buscar", "procure", "procurar"],
            "listar": ["liste", "listar", "mostre", "mostrar", "exiba", "exibir"],
            "mover": ["mova", "mover", "transfira", "transferir"],
            "copiar": ["copie", "copiar", "duplique"],
            "renomear": ["renomeie", "renomear", "mude o nome"],
            "instalar": ["instale", "instalar", "baixe", "baixar"],
            "desinstalar": ["desinstale", "desinstalar", "remova o programa"],
            "configurar": ["configure", "configurar", "ajuste", "ajustar"],
            "consultar": ["consulte", "consultar", "verifique", "verificar", "cheque"],
            "comparar": ["compare", "comparar"],
            "organizar": ["organize", "organizar", "arrume", "arrumar"],
            "agendar": ["agende", "agendar", "lembre", "lembrar", "alarme"],
        }

        for action, keywords in action_map.items():
            for kw in keywords:
                if kw in text_lower:
                    intent["action"] = action
                    intent["confidence"] = 0.8

                    # Extrai alvo (o que vem depois da acao)
                    idx = text_lower.find(kw)
                    rest = text[idx + len(kw):].strip()
                    if rest:
                        # Remove preposicoes iniciais
                        rest = re.sub(r'^(o|a|os|as|um|uma|uns|umas|de|do|da|no|na|para|em)\s+',
                                     '', rest, count=1, flags=re.IGNORECASE)
                        intent["target"] = rest.strip()

                    break
            if intent["action"]:
                break

        # Detecta modificadores
        if "rapido" in text_lower or "urgente" in text_lower:
            intent["modifiers"].append("urgente")
        if "silencio" in text_lower or "discreto" in text_lower:
            intent["modifiers"].append("silencioso")
        if "todos" in text_lower or "tudo" in text_lower:
            intent["modifiers"].append("batch")
        if "desktop" in text_lower:
            intent["modifiers"].append("desktop")
        if "downloads" in text_lower:
            intent["modifiers"].append("downloads")

        return intent

    def detect_business_intent(self, text: str) -> Optional[Dict]:
        """
        Detecta intencoes de negocio (autopecas).
        Item 26 do plano.

        Returns:
            Dict com tipo de intencao de negocio ou None
        """
        text_lower = text.lower()

        business_patterns = {
            "consultar_peca": [
                r"(?:tem|tenho|existe|tem a|vende)\s+(?:a\s+)?(?:peca|peça)\s+(.+)",
                r"(?:alternador|motor de arranque|bomba|filtro|pastilha|disco|amortecedor|correia|vela|bobina|radiador|compressor)\s+(?:do|da|de|para|pro|pra)\s+(.+)",
            ],
            "verificar_compatibilidade": [
                r"(?:serve|funciona|encaixa|compativel|compatível)\s+(?:no|na|pro|pra|para|com)\s+(.+)",
                r"(.+)\s+(?:serve|funciona|encaixa)\s+(?:no|na|pro|pra|para)\s+(.+)",
            ],
            "consultar_preco": [
                r"(?:preco|preço|valor|quanto custa|quanto e|quanto sai)\s+(?:do|da|de)\s+(.+)",
                r"(.+)\s+(?:preco|preço|valor|quanto custa)",
            ],
            "relatorio_estoque": [
                r"(?:estoque|inventario|relatorio|relatório)\s+(?:de\s+)?(?:pecas|peças)",
                r"(?:quantas?\s+)?(?:pecas|peças)\s+(?:tenho|temos|tem)\s*(?:em\s+estoque)?",
            ],
        }

        for intent_type, patterns in business_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    return {
                        "type": intent_type,
                        "match": match.group(0),
                        "groups": match.groups(),
                        "confidence": 0.8,
                    }

        return None

    def add_abbreviation(self, abbrev: str, expansion: str):
        """Adiciona abreviacao customizada."""
        self._abbreviations[abbrev.lower()] = expansion.lower()

    def get_stats(self) -> Dict:
        """Estatisticas do NLP."""
        return {
            "abbreviations": len(self._abbreviations),
            "typos": len(self._typos),
            "informal_expressions": len(self._informal),
        }


# Singleton
_nlp_processor = None


def get_nlp_processor() -> NLPProcessor:
    """Retorna singleton do NLPProcessor."""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = NLPProcessor()
    return _nlp_processor
