"""
ConversaoSkill - Agente de Conversão e Copy.
Gera copy, scripts de abordagem, tratamento de objeções e propostas.
"""

import json
from pathlib import Path
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_DIR = Path("data/business")


def _get_ai_response(prompt: str, fallback: str = "") -> str:
    """Chama a IA real com o prompt. Usa fallback se falhar."""
    try:
        from src.core.ai_engine import get_engine
        engine = get_engine()
        response = engine.chat_with_fallback(prompt)
        if response and len(response) > 20:
            return response
    except Exception as e:
        log.warning(f"IA nao disponivel para conversao: {e}")
    return fallback


class ConversaoSkill(BaseSkill):
    """Agente especializado em copy, scripts e fechamento de vendas."""

    name = "conversao"
    description = "Gera copy, scripts de abordagem, mensagens e propostas de vendas"
    keywords = [
        "copy", "mensagem", "script", "abordagem", "objecao", "proposta",
        "fechamento", "sequencia", "follow-up", "followup", "follow up",
        "texto para vender", "como abordar", "o que falar", "mensagem de venda",
        "mensagem para whatsapp", "email de venda", "roteiro", "argumento",
        "como convencer", "tratamento", "rejeicao", "nao quero", "sem interesse"
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
            if any(w in cmd for w in ["objecao", "rejeicao", "nao quero", "sem interesse", "nao tenho", "esta caro"]):
                return self._tratar_objecoes(command)
            elif any(w in cmd for w in ["proposta", "contrato", "orcamento", "valor"]):
                return self._gerar_proposta(command)
            elif any(w in cmd for w in ["sequencia", "follow-up", "followup", "follow up", "7 dias", "10 dias"]):
                return self._gerar_sequencia(command)
            elif any(w in cmd for w in ["email", "e-mail"]):
                return self._gerar_copy_email(command)
            else:
                return self._gerar_script_abordagem(command)
        except Exception as e:
            log.error(f"ConversaoSkill erro: {e}")
            return SkillResult(success=False, message=f"Erro na conversão: {e}")

    def _extrair_nicho(self, command: str) -> str:
        palavras_remover = [
            "copy", "script", "mensagem", "para", "gere", "crie", "faca",
            "abordagem", "de", "do", "da", "um", "uma", "o", "a", "whatsapp",
            "email", "proposta", "sequencia", "follow", "up"
        ]
        palavras = command.lower().split()
        nicho = " ".join(w for w in palavras if w not in palavras_remover)
        return nicho.strip() or "cliente"

    def _gerar_script_abordagem(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)

        prompt = f"""Voce e um especialista em vendas e copywriting no mercado brasileiro.
Crie scripts de abordagem de alta conversao para o nicho: {nicho}

Inclua (em portugues, coloquial brasileiro):
1. MENSAGEM 1 - Primeiro contato pelo WhatsApp (curta, curiosidade, sem revelar tudo)
2. MENSAGEM 2 - Follow-up se nao respondeu em 24h (mais direta, proposta de valor)
3. MENSAGEM 3 - Apos demonstrar interesse (explica processo, CTA para call)
4. ABORDAGEM FRIA - Para Google Maps / LinkedIn (formal mas acolhedora)
5. TRATAMENTO - "Nao tenho tempo" (reframe + CTA rapido)
6. CTA FINAL - Fechamento com urgencia

Seja especifico para {nicho}: use a linguagem que esse publico usa, mencione dores especificas do setor."""

        fallback = f"""[SCRIPT DE ABORDAGEM] - {nicho.upper()}
MSG 1: "Ola [Nome]! Vi que voce atua com {nicho}. Tenho uma ideia que tem dado resultados incriveis no seu setor. Posso compartilhar rapidinho?"
MSG 2: "Nao quero tomar seu tempo - so 15 minutos para mostrar como ajudo {nicho} a crescer sem complicacao."
MSG 3: "Perfeito! Funciona assim: 30min para entender seu negocio → estrategia personalizada → resultado em 30 dias. Qual horario esta semana?"
OBJECAO TEMPO: "Exatamente por isso faz sentido! A ideia e automatizar para VOCE ganhar tempo. 10 minutinhos?"
CTA: wa.me/[SEU_NUMERO]"""

        script = _get_ai_response(prompt, fallback)

        # Salva copy
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "ultimo_script.txt").write_text(script, encoding="utf-8")

        return SkillResult(success=True, message=script, data={"nicho": nicho, "arquivo": "data/business/ultimo_script.txt"})

    def _gerar_sequencia(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)

        prompt = f"""Voce e um especialista em vendas e follow-up no mercado brasileiro.
Crie uma sequencia de follow-up de 7 dias para o nicho: {nicho}

Inclua exatamente:
- DIA 1: Primeiro contato (curto, gera curiosidade)
- DIA 2: Entrega valor gratuito (dica ou conteudo relevante para {nicho})
- DIA 3: Prova social (resultado real ou case do setor de {nicho})
- DIA 4: Pergunta estrategica (descobre a dor principal)
- DIA 5: Oferta direta com beneficio claro
- DIA 7: Ultimo follow-up respeitoso com saida digna

Cada mensagem deve ser curta (max 3 linhas), coloquial, sem parecer spam.
Use linguagem especifica do setor de {nicho}."""

        fallback = f"""[SEQUENCIA DE FOLLOW-UP] - 7 DIAS para {nicho.upper()}

DIA 1: "Ola [Nome]! Vi seu trabalho com {nicho} e tenho algo que pode te interessar. Posso te mandar um resumo? So 2 minutos!"
DIA 2: "[Nome], separei uma dica que tem ajudado muito no setor de {nicho}: [dica]. Espero que seja util!"
DIA 3: "[Nome], um cliente meu de {nicho} obteve [resultado] em 30 dias. Voce ja passou por esse desafio?"
DIA 4: "[Nome], so uma pergunta: qual e seu maior desafio hoje para crescer em {nicho}?"
DIA 5: "[Nome], acredito que posso ajudar exatamente com isso. 15 minutos para te mostrar como? Sem compromisso!"
DIA 7: "[Nome], nao quero ser insistente. Faz sentido conversarmos? Se nao for o momento, sem problema!"

REGRAS: max 1 msg/dia | personalize com o nome | pare se receber "nao" claro"""

        resposta = _get_ai_response(prompt, fallback)
        return SkillResult(success=True, message=resposta)

    def _tratar_objecoes(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)

        prompt = f"""Voce e um especialista em vendas consultivas no Brasil.
Crie scripts detalhados para tratar as 6 principais objecoes de vendas no nicho: {nicho}

Para cada objecao forneca: a frase exata do cliente, o script de resposta (coloquial, natural) e a pergunta de redirecionamento.

Objecoes:
1. "Esta muito caro" - reframe de valor especifico para {nicho}
2. "Preciso pensar" - descobrir o bloqueio real
3. "Ja tentei e nao funcionou" - diferenciar da experiencia anterior
4. "Nao tenho tempo agora" - ironia: o produto economiza tempo em {nicho}
5. "Vou falar com meu socio" - envolver o decisor
6. "Nao preciso disso" - descobrir como resolve o problema hoje

Use linguagem coloquial brasileira, especifica para o setor de {nicho}."""

        fallback = """[TRATAMENTO DE OBJECOES] - Scripts Validados

1. "Esta caro" → "Caro comparado a que? Se voce resolver [dor] em 30 dias, quanto vale isso?"
2. "Preciso pensar" → "Claro! O que especificamente trava a decisao? Posso ajudar a clarear."
3. "Ja tentei" → "Me conta o que tentou? O que faco e diferente porque [diferencial unico]."
4. "Sem tempo" → "Justamente - o objetivo e voce GANHAR tempo, nao perder mais."
5. "Vou falar com socio" → "Otimo! Preparo um resumo para facilitar a conversa de voces?"
6. "Nao preciso" → "Como voce esta resolvendo [problema X] hoje? Curiosidade mesmo."

REGRA DE OURO: Valide sempre + redirecione com pergunta. Nunca discuta."""

        resposta = _get_ai_response(prompt, fallback)
        return SkillResult(success=True, message=resposta)

    def _gerar_proposta(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)

        prompt = f"""Voce e um consultor de negocios senior no Brasil.
Crie uma proposta comercial COMPLETA e PROFISSIONAL para o nicho: {nicho}

Inclua:
1. OBJETIVO - o que sera resolvido para o cliente de {nicho}
2. DIAGNOSTICO - as 3 principais dores do setor de {nicho}
3. SOLUCAO - o que sera entregue (fase 1, 2, 3 com prazos realistas)
4. RESULTADOS ESPERADOS - metricas e KPIs especificos para {nicho}
5. INVESTIMENTO - 3 opcoes de preco adequadas para o mercado brasileiro de {nicho}
6. GARANTIA - politica de garantia que gera confianca
7. PROXIMOS PASSOS - CTA claro para fechar

Seja especifico para {nicho}: use terminologia do setor, mencione dores reais, sugira valores realistas para o mercado brasileiro."""

        fallback = f"""[PROPOSTA COMERCIAL] para {nicho.upper()}

OBJETIVO: Ajudar [cliente] a crescer faturamento e otimizar processos de {nicho}.

FASES:
  Fase 1 (Semana 1): Diagnostico + Estrategia 90 dias
  Fase 2 (Semanas 2-3): Implementacao + Automacoes
  Fase 3 (Mes 2+): Otimizacao + Acompanhamento mensal

INVESTIMENTO:
  Opcao 1: R$2.000 + R$1.500/mes
  Opcao 2: R$5.500 (3 meses)
  Opcao 3: R$9.000 (6 meses - melhor custo-beneficio)

GARANTIA: 30 dias com resultado ou devolucao total.

PROXIMOS PASSOS: Responda "ACEITO" para receber o contrato em 24h."""

        proposta = _get_ai_response(prompt, fallback)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "ultima_proposta.txt").write_text(proposta, encoding="utf-8")

        return SkillResult(success=True, message=proposta, data={"arquivo": "data/business/ultima_proposta.txt"})

    def _gerar_copy_email(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)

        prompt = f"""Voce e um copywriter especialista em email marketing B2B no Brasil.
Crie um email de prospecao fria de ALTA CONVERSAO para o nicho: {nicho}

O email deve ter:
- ASSUNTO: curto, curioso, especifico para {nicho} (max 60 chars)
- ABERTURA: personalizada, menciona algo especifico de {nicho}
- DOR: 2-3 dores reais e especificas que empresas de {nicho} enfrentam
- SOLUCAO: o que voce oferece, sem revelar tudo
- PROVA: resultado especifico (pode ser hipotetico mas realista para {nicho})
- CTA: simples, uma acao so (agendar 20min call)
- P.S.: reforca urgencia ou escassez

Tom: profissional mas humano. Tamanho: maximo 150 palavras no corpo.
Especifico para {nicho} - use a linguagem que esse publico usa."""

        fallback = f"""[EMAIL DE PROSPECAO] para {nicho.upper()}

ASSUNTO: Ideia rapida para {nicho} (2 min)

Ola [Nome],

Vi que voce atua com {nicho} e queria compartilhar algo que tem gerado resultados no setor.

Profissionais de {nicho} geralmente enfrentam:
- Falta de clientes novos de forma previsivel
- Muito trabalho manual
- Dificuldade em se destacar

Tenho uma metodologia que resolve exatamente isso.

Posso te mostrar em 20 minutos? [link_agenda]

Abraco, [Nome] | [WhatsApp]

P.S.: Trabalho com poucos clientes por mes para garantir resultados. Se fizer sentido, sugiro agendar logo!"""

        email = _get_ai_response(prompt, fallback)
        return SkillResult(success=True, message=email)
