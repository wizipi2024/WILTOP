"""
EstrategiaSkill - Agente de Estratégia de Negócios.
Define modelo de negócio, oferta, ticket e funil completo com IA.
"""

import json
from pathlib import Path
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_DIR = Path("data/business")


def _get_ai_response(prompt: str, fallback: str = "") -> str:
    """Chama a IA real (Groq/Ollama) com o prompt. Usa fallback se falhar."""
    try:
        from src.core.ai_engine import get_engine
        engine = get_engine()
        response = engine.chat_with_fallback(prompt)
        if response and len(response) > 20:
            return response
    except Exception as e:
        log.warning(f"IA nao disponivel para estrategia: {e}")
    return fallback


class EstrategiaSkill(BaseSkill):
    """Agente especializado em estratégia de negócios e monetização."""

    name = "estrategia"
    description = "Define estratégia de negócio, oferta, ticket e funil completo"
    keywords = [
        "estrategia", "modelo de negocio", "oferta", "ticket", "nicho",
        "posicionamento", "funil", "avatar", "publico alvo", "mercado",
        "como vender", "quero vender", "preciso vender", "vender mais",
        "montar negocio", "criar negocio", "abrir negocio", "empreender",
        "produto", "servico", "consultoria", "agencia", "infoproduto"
    ]

    def can_handle(self, command: str) -> float:
        cmd = command.lower()
        score = 0.0
        for kw in self.keywords:
            if kw in cmd:
                score += 0.15
        return min(score, 1.0)

    def execute(self, command: str, params: dict = None, context: dict = None) -> SkillResult:
        cmd = command.lower()
        try:
            if any(w in cmd for w in ["avatar", "publico", "cliente ideal", "icp"]):
                return self._gerar_avatar(command)
            elif any(w in cmd for w in ["funil", "etapa", "jornada"]):
                return self._gerar_funil(command)
            elif any(w in cmd for w in ["oferta", "produto", "servico", "o que vender"]):
                return self._definir_oferta(command)
            elif any(w in cmd for w in ["canal", "onde vender", "trafego", "marketing"]):
                return self._sugerir_canais(command)
            else:
                return self._estrategia_completa(command)
        except Exception as e:
            log.error(f"EstrategiaSkill erro: {e}")
            return SkillResult(success=False, message=f"Erro na estratégia: {e}")

    def _extrair_nicho(self, command: str) -> str:
        """Extrai o nicho/segmento do comando."""
        palavras_remover = [
            "quero", "vender", "para", "preciso", "criar", "montar",
            "estrategia", "funil", "modelo", "negocio", "oferta", "ticket",
            "consultoria", "agencia", "servico", "produto", "de", "do", "da",
            "um", "uma", "meu", "minha", "meus", "minhas"
        ]
        palavras = command.lower().split()
        nicho = " ".join(w for w in palavras if w not in palavras_remover)
        return nicho.strip() or "negócio digital"

    def _estrategia_completa(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)

        # Tenta IA real primeiro
        ai_prompt = f"""Voce e um consultor de estrategia de negocios senior especializado no mercado brasileiro.
Crie uma estrategia COMPLETA e DETALHADA para o seguinte nicho: {nicho}

Responda em portugues, de forma estruturada com topicos claros. Inclua:
1. MODELO DE NEGOCIO: Tipo ideal (consultoria, SaaS, infoproduto, servico recorrente), ticket medio realista em reais
2. OFERTA PRINCIPAL: Frase de posicionamento clara ("Ajudo X a Y em Z sem W")
3. AVATAR DO CLIENTE: Perfil demografico, dores especificas, desejos, objecoes
4. FUNIL DE VENDAS: Topo (consciencia), Meio (consideracao), Fundo (decisao) com canais especificos
5. CANAIS DE AQUISICAO: Organico e pago, priorizados para o Brasil
6. METAS 90 DIAS: Numeros realistas para cada mes
7. PROXIMOS PASSOS: 4 acoes concretas para comecar hoje

Seja especifico para o nicho "{nicho}" com dados reais do mercado brasileiro. Nao seja generico."""

        # Template como fallback
        templates = {
            "dentist": {"modelo": "Consultoria de Marketing B2B", "ticket": "R$2.000-5.000/mês", "canal": "WhatsApp + LinkedIn", "ciclo": "30 dias"},
            "restaurante": {"modelo": "Gestão de Presença Digital", "ticket": "R$800-2.000/mês", "canal": "Instagram + Google Meu Negócio", "ciclo": "15 dias"},
            "advogad": {"modelo": "Consultoria Especializada", "ticket": "R$3.000-10.000/projeto", "canal": "LinkedIn + Indicações", "ciclo": "45 dias"},
            "autopeç": {"modelo": "E-commerce + Marketplace", "ticket": "R$1.500-3.000/mês", "canal": "Mercado Livre + WhatsApp", "ciclo": "20 dias"},
            "clinic": {"modelo": "Gestão e Captação de Pacientes", "ticket": "R$2.000-6.000/mês", "canal": "Instagram + Google Ads", "ciclo": "30 dias"},
            "marketing": {"modelo": "Agência de Resultados", "ticket": "R$1.500-5.000/mês", "canal": "LinkedIn + Indicações", "ciclo": "30 dias"},
        }

        template = {"modelo": "Consultoria Especializada", "ticket": "R$1.500-4.000/mês", "canal": "WhatsApp + Redes Sociais", "ciclo": "30 dias"}
        for key, tpl in templates.items():
            if key in nicho.lower():
                template = tpl
                break

        fallback_text = f"""[ESTRATEGIA DE NEGOCIO] - {nicho.upper()}

MODELO DE NEGOCIO:
  Tipo: {template['modelo']}
  Ticket Ideal: {template['ticket']}
  Ciclo de Venda: {template['ciclo']}

OFERTA PRINCIPAL:
  "Ajudo {nicho} a lotar a agenda e faturar mais em 30 dias
  sem depender de indicacoes ou gastar fortune em anuncios"

FUNIL RECOMENDADO:
  Topo: {template['canal']} → Conteudo/Prospeccao
  Meio: Qualificacao → Call de Discovery (30min)
  Fundo: Proposta → Contrato → Onboarding

CANAIS PRINCIPAIS: {template['canal']}

METAS 90 DIAS:
  Mes 1: 3-5 clientes piloto
  Mes 2: 8-10 clientes pagantes
  Mes 3: 15+ clientes / Receita previsivel

PROXIMOS PASSOS:
  1. [William] gere script para {nicho}
  2. [William] encontre clientes {nicho}
  3. [William] crie funil para {nicho}
  4. [William] crie landing page para {nicho}
"""

        # Usa IA real; se falhar, usa fallback
        ai_response = _get_ai_response(ai_prompt, fallback=fallback_text)
        estrategia = ai_response

        # Adiciona proximos passos se a IA nao incluiu
        if "william" not in ai_response.lower():
            estrategia += f"""

PROXIMOS PASSOS COM WILLIAM:
  Digite: "gere script para {nicho}"
  Digite: "encontre clientes {nicho}"
  Digite: "crie funil para {nicho}"
"""

        # Salva estratégia
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        save_path = DATA_DIR / "estrategia_atual.json"
        save_path.write_text(json.dumps({
            "nicho": nicho, "template": template,
            "estrategia": estrategia
        }, ensure_ascii=False), encoding="utf-8")

        return SkillResult(success=True, message=estrategia, data={"nicho": nicho})

    def _gerar_avatar(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        prompt = f"""Crie um avatar detalhado do cliente ideal (ICP) para o nicho: {nicho} no mercado brasileiro.
Inclua: perfil demografico, cargo/renda, dores especificas do setor, desejos, objecoes mais comuns e onde encontra-los online.
Seja especifico para {nicho}, nao generico."""
        fallback = f"""[AVATAR / CLIENTE IDEAL] - {nicho.upper()}
PERFIL: Dono/Gestor de {nicho} | Faturamento R$50k-500k/mes | 1-20 funcionarios
DORES: Falta clientes novos, dependencia de indicacoes, trabalho manual
DESEJOS: Agenda lotada, processos automaticos, faturamento previsivel
OBJECOES: "Ja tentei", "Nao tenho tempo", "Esta caro", "Deixa pensar"
ONDE ACHAR: WhatsApp grupos do setor, Google Maps, Instagram, LinkedIn"""
        return SkillResult(success=True, message=_get_ai_response(prompt, fallback))

    def _gerar_funil(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        prompt = f"""Crie um funil de vendas completo e detalhado para o nicho: {nicho} no Brasil.
Inclua: etapas (topo/meio/fundo), canais especificos, metricas realistas, taxas de conversao esperadas e projecao de receita.
Seja especifico para {nicho}."""
        fallback = f"""[FUNIL DE VENDAS] - {nicho.upper()}
TOPO: Instagram/Google → 100 pessoas/semana
MEIO: WhatsApp/Email → 20 leads qualificados/semana
FUNDO: Reuniao/Proposta → 3-5 clientes/mes
TICKET R$2.000/mes → R$6.000-10.000/mes em 90 dias"""
        return SkillResult(success=True, message=_get_ai_response(prompt, fallback))

    def _definir_oferta(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        prompt = f"""Crie uma oferta irresistivel para o nicho: {nicho} no mercado brasileiro.
Inclua: nome da oferta, o que entrega, precos sugeridos (3 planos), garantia, urgencia/escassez e frase de posicionamento poderosa.
Seja especifico, com valores realistas em reais para {nicho}."""
        fallback = f"""[OFERTA IRRESISTIVEL] - {nicho.upper()}
Nome: "Sistema de Crescimento para {nicho.title()}"
Starter: R$997/mes | Growth: R$1.997/mes | Pro: R$3.997/mes
Garantia: 30 dias ou devolucao total
Escassez: Apenas 5 vagas este mes"""
        return SkillResult(success=True, message=_get_ai_response(prompt, fallback))

    def _sugerir_canais(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        prompt = f"""Quais sao os melhores canais de aquisicao de clientes para o nicho: {nicho} no Brasil?
Liste canais organicos (gratuitos) e pagos, com estrategia especifica para cada um, ROI esperado e por onde comecar.
Priorize o que funciona melhor para {nicho} no mercado brasileiro em 2024."""
        fallback = f"""[CANAIS DE AQUISICAO] - {nicho.upper()}
ORGANICO: WhatsApp prospeccao direta, Instagram conteudo, Google Meu Negocio, LinkedIn B2B
PAGO: Google Ads (maior intencao), Meta Ads (maior alcance)
RECOMENDACAO: Comece com WhatsApp ativo (0 custo), depois Instagram, depois trafego pago

RECOMENDACAO PARA COMECAR:
"""
        return SkillResult(success=True, message=_get_ai_response(prompt, fallback))
