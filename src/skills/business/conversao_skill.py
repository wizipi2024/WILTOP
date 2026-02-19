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

        sequencia = f"""[SEQUENCIA DE FOLLOW-UP] - 7 DIAS para {nicho.upper()}

DIA 1 - Primeiro Contato:
"Ola [Nome]! Vi seu trabalho com {nicho} e tenho algo que pode te interessar.
Posso te mandar um resumo? So 2 minutos!"

DIA 2 - Valor Gratuito:
"[Nome], separei este conteudo para voce:
[Link/dica relevante sobre {nicho}]
Acredito que vai ajudar bastante!"

DIA 3 - Prova Social:
"[Nome], aqui um resultado de um cliente meu do setor de {nicho}:
'[Depoimento ou resultado especifico]'
Voce ja passou por esse desafio tambem?"

DIA 4 - Pergunta Estrategica:
"[Nome], so uma pergunta rapida:
Qual e o seu maior desafio hoje para crescer seu negocio de {nicho}?"

DIA 5 - Oferta Direta:
"[Nome], acredito que posso ajudar especificamente no que voce mencionou.
Posso te mostrar em 15 minutos como? Sem compromisso!"

DIA 7 - Ultimo Follow-up:
"[Nome], nao quero ser insistente, mas gostaria de saber:
faz sentido conversarmos sobre crescimento para {nicho}?
Se nao for o momento, sem problema. So me avisa!"

REGRAS:
  - Nunca envie mais de 1 mensagem por dia
  - Sempre personalize com o nome do lead
  - Pare se receber um "nao" claro
  - Use o mesmo canal que o lead usa (WhatsApp / Email / LinkedIn)
"""
        return SkillResult(success=True, message=sequencia)

    def _tratar_objecoes(self, command: str) -> SkillResult:
        objecoes = """[TRATAMENTO DE OBJECOES] - Scripts Validados

OBJECAO 1: "Esta muito caro"
Script: "Entendo! Posso te perguntar: caro comparado a que?
Se voce pudesse ter [resultado X] em 30 dias, quanto isso valeria para o seu negocio?
Geralmente meus clientes recuperam o investimento ja no primeiro mes."

OBJECAO 2: "Preciso pensar"
Script: "Claro, faz sentido! Mas me conta: o que especificamente
voce precisa pensar? Assim posso te ajudar a tomar a melhor decisao."

OBJECAO 3: "Ja tentei e nao funcionou"
Script: "Sinto muito que isso aconteceu! Me conta o que voce tentou?
O que eu faco e diferente porque [diferenciacal]. Posso te mostrar
exatamente por que funciona para {nicho}?"

OBJECAO 4: "Nao tenho tempo agora"
Script: "Entendo! Justamente por isso isso faz sentido: o objetivo
e justamente voce ganhar tempo, nao perder mais.
Quanto tempo voce perde hoje com [tarefa repetitiva]?"

OBJECAO 5: "Vou falar com meu socio"
Script: "Otimo! Para facilitar, posso preparar um material resumido
para voces avaliarem juntos? Assim fica mais facil apresentar.
Quando voces se reúnem?"

OBJECAO 6: "Nao preciso disso"
Script: "Totalmente valido! Me permite uma pergunta: como voce esta
resolvendo [problema X] hoje? Curiosidade mesmo."

REGRA DE OURO:
Nunca discuta. Sempre valide a objecao e redirecione com pergunta.
"""
        return SkillResult(success=True, message=objecoes)

    def _gerar_proposta(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)

        proposta = f"""[PROPOSTA COMERCIAL] para {nicho.upper()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROPOSTA COMERCIAL - [SEU NOME/EMPRESA]
Para: [Nome do Cliente]
Data: [Data]
Validade: 7 dias
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OBJETIVO:
Ajudar [empresa do cliente] a crescer faturamento
e automatizar processos de {nicho}.

O QUE SERA ENTREGUE:

FASE 1 - Diagnostico e Estrategia (Semana 1):
  ✓ Analise completa do negocio atual
  ✓ Mapeamento de oportunidades
  ✓ Estrategia personalizada 90 dias
  ✓ Plano de acao detalhado

FASE 2 - Implementacao (Semanas 2-3):
  ✓ Configuracao dos funis de captacao
  ✓ Automacoes de follow-up
  ✓ Integracao com ferramentas atuais
  ✓ Treinamento da equipe

FASE 3 - Otimizacao e Resultados (Semana 4+):
  ✓ Acompanhamento das metricas
  ✓ Ajustes baseados em dados
  ✓ Relatorio mensal detalhado
  ✓ Suporte continuo

INVESTIMENTO:
  Opcao 1 - Setup: R$2.000 + R$1.500/mes
  Opcao 2 - 3 meses: R$5.500 (economia de R$1.000)
  Opcao 3 - 6 meses: R$9.000 (melhor custo-beneficio)

GARANTIA:
  Se em 30 dias nao houver resultados mensuráveis,
  devolvemos 100% do investimento.

PROXIMOS PASSOS:
  1. Aceite esta proposta respondendo "ACEITO"
  2. Enviaremos o contrato por email
  3. Iniciaremos em 24h apos assinatura
  4. Primeiro resultado esperado em 15-30 dias

[ASSINE AQUI: link_contrato]
[PAGUE AQUI: link_pagamento]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        # Salva proposta
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "ultima_proposta.txt").write_text(proposta, encoding="utf-8")

        return SkillResult(success=True, message=proposta, data={"arquivo": "data/business/ultima_proposta.txt"})

    def _gerar_copy_email(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        email = f"""[EMAIL DE PROSPECAO] para {nicho.upper()}

ASSUNTO: Ideia para crescer seu negocio de {nicho} (2 min de leitura)

---

Ola [Nome],

Vi que voce atua com {nicho} em [Cidade] e queria compartilhar algo
que tem gerado resultados expressivos para profissionais do seu setor.

Empresas como a sua geralmente enfrentam 3 desafios principais:
1. Falta de clientes novos de forma previsivel
2. Muito trabalho manual e repetitivo
3. Dificuldade em se destacar da concorrencia

Desenvolvemos uma metodologia que resolve exatamente isso — e os
resultados sao comprovados:

[RESULTADO CLIENTE 1]: Aumentou faturamento em 40% em 60 dias
[RESULTADO CLIENTE 2]: Reduziu 70% do trabalho manual
[RESULTADO CLIENTE 3]: Triplicou a carteira de clientes em 3 meses

Posso te mostrar como em uma call de 20 minutos?

[AGENDAR AGORA - link_calendly]

Ou responda este email com o melhor horario.

Abraco,
[Seu Nome]
[Cargo] | [Empresa]
[WhatsApp] | [Site]

P.S.: So trabalho com 5 novos clientes por mes para garantir
dedicacao total. Se tiver interesse, sugiro agendamento rapido!
"""
        return SkillResult(success=True, message=email)
