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

        # Templates por tipo de nicho
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

        estrategia = f"""[ESTRATEGIA DE NEGOCIO] - {nicho.upper()}

MODELO DE NEGOCIO:
  Tipo: {template['modelo']}
  Ticket Ideal: {template['ticket']}
  Ciclo de Venda: {template['ciclo']}

OFERTA PRINCIPAL:
  "Ajudo {nicho} a [resultado desejado] em [prazo] sem [principal obstaculo]"

  Exemplo: "Ajudo {nicho} a lotar a agenda e faturar mais em 30 dias
  sem depender de indicações ou gastar fortune em anúncios"

PROPOSTA DE VALOR:
  - Resultado 1: Mais clientes qualificados todo mês
  - Resultado 2: Processo automatizado (menos trabalho manual)
  - Resultado 3: Previsibilidade de receita

FUNIL RECOMENDADO:
  Topo: {template['canal']} → Conteúdo/Prospecção
  Meio: Qualificação → Call de Discovery (30min)
  Fundo: Proposta → Contrato → Onboarding

CANAIS PRINCIPAIS:
  {template['canal']}

METAS PARA 90 DIAS:
  Mês 1: 3-5 clientes piloto (mesmo que reduzido)
  Mês 2: 8-10 clientes pagantes
  Mês 3: 15+ clientes / Receita previsível

PROXIMOS PASSOS:
  1. [William] Gere o script de abordagem → "gere script para {nicho}"
  2. [William] Crie a prospecção → "encontre clientes {nicho}"
  3. [William] Monte o funil n8n → "crie funil para {nicho}"
  4. [William] Crie landing page → "crie landing page para {nicho}"
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
        avatar = f"""[AVATAR / CLIENTE IDEAL] - {nicho.upper()}

PERFIL DEMOGRAFICO:
  Cargo: Dono/Gestor de {nicho}
  Faturamento: R$50k-500k/mês
  Funcionários: 1-20
  Cidade: Capitais e cidades grandes

DORES PRINCIPAIS:
  - Falta de clientes novos todo mês
  - Dependência de indicações (imprevisível)
  - Muito trabalho manual e repetitivo
  - Concorrência acirrada com preço baixo

DESEJOS:
  - Agenda lotada / carteira cheia
  - Processos automáticos rodando sozinhos
  - Faturamento previsível e crescente
  - Mais tempo para focar no que sabe fazer

OBJEÇÕES COMUNS:
  - "Já tentei e não funcionou"
  - "Não tenho tempo para isso agora"
  - "Está caro" / "Preciso pensar"
  - "Deixa eu falar com meu sócio"

ONDE ENCONTRAR:
  - Grupos de WhatsApp do setor
  - Associações comerciais
  - Google Maps (busca local)
  - Instagram/LinkedIn com hashtags do nicho
"""
        return SkillResult(success=True, message=avatar)

    def _gerar_funil(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        funil = f"""[FUNIL DE VENDAS] - {nicho.upper()}

TOPO (Consciência):
  Canal: Instagram / Google / Indicações
  Conteúdo: Dores do {nicho} + Resultados
  Meta: 100 pessoas/semana vendo seu conteúdo

MEIO (Consideração):
  Canal: WhatsApp / Direct / Email
  Ação: Conversa → Qualificação → Call 30min
  Meta: 20 leads qualificados/semana

FUNDO (Decisão):
  Canal: Reunião / Proposta / Contrato
  Ação: Apresentar solução → Fechar → Onboarding
  Meta: 3-5 novos clientes/mês

METRICAS:
  Taxa Topo→Meio: 20% (100 → 20 leads)
  Taxa Meio→Fundo: 25% (20 → 5 calls)
  Taxa Fechamento: 60% (5 → 3 clientes)

  Com ticket R$2.000/mês → R$6.000/mês recorrente
  Em 6 meses → R$36.000/mês em recorrência
"""
        return SkillResult(success=True, message=funil)

    def _definir_oferta(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        oferta = f"""[OFERTA IRRESISTIVEL] - {nicho.upper()}

NOME DA OFERTA:
  "Sistema de Crescimento para {nicho.title()}"

O QUE INCLUI:
  + Diagnóstico completo do negócio (R$500 de valor)
  + Estratégia personalizada 90 dias
  + Funil de captação configurado
  + Sequência de follow-up automática
  + Relatório mensal de resultados
  + Suporte via WhatsApp (dias úteis)

GARANTIA:
  "Se em 30 dias não tiver resultados mensuráveis,
  devolvemos 100% do investimento"

PRECOS SUGERIDOS:
  Starter: R$997/mês (1 canal, suporte básico)
  Growth: R$1.997/mês (3 canais, suporte prioritário)
  Pro: R$3.997/mês (tudo + consultoria semanal)

  Setup único: R$2.000 + mensalidade

URGENCIA/ESCASSEZ:
  "Apenas 5 vagas abertas este mês para {nicho}"
"""
        return SkillResult(success=True, message=oferta)

    def _sugerir_canais(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        canais = f"""[CANAIS DE AQUISICAO] - {nicho.upper()}

ORGANICO (Gratuito - começa agora):
  1. WhatsApp: Prospecção direta + Grupos do setor
  2. Instagram: Conteúdo educativo + Reels
  3. Google Meu Negócio: Aparecer nas buscas locais
  4. LinkedIn: Para B2B e perfil profissional
  5. Indicações: Programa de referência (comissão)

PAGO (Quando tiver capital):
  1. Google Ads: Busca por intenção (maior conversão)
  2. Meta Ads: Instagram/Facebook (maior alcance)
  3. YouTube Ads: Para conteúdo mais longo

RECOMENDACAO PARA COMECAR:
  Fase 1 (0-30 dias): WhatsApp + Prospecção ativa
  Fase 2 (30-60 dias): Instagram + Conteúdo
  Fase 3 (60-90 dias): Google Ads (com capital do Fase 1)

ROI ESPERADO:
  WhatsApp ativo: 5-10 leads/semana (R$0)
  Instagram orgânico: 10-20 leads/mês (R$0)
  Google Ads: 30-50 leads/mês (R$1.500 investido)
"""
        return SkillResult(success=True, message=canais)
