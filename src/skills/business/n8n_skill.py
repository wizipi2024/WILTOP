"""
N8nSkill - Criador Automático de Workflows n8n.
Gera funis, automações e sequências direto no n8n via API.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_DIR = Path("data/n8n")


class N8nSkill(BaseSkill):
    """Cria workflows n8n automaticamente com IA."""

    name = "n8n"
    description = "Cria fluxos de automação no n8n: funis, follow-up, CRM, webhooks"
    keywords = [
        "n8n", "funil", "fluxo", "automacao", "workflow", "automatizar",
        "sequencia automatica", "follow-up automatico", "disparar mensagens",
        "webhook", "integracao", "captura de leads", "crm automatico",
        "pipeline automatico", "bot de vendas", "disparo automatico"
    ]

    def can_handle(self, command: str) -> float:
        cmd = command.lower()
        score = 0.0
        for kw in self.keywords:
            if kw in cmd:
                score += 0.18
        return min(score, 1.0)

    def _get_n8n_config(self):
        """Pega configuração do n8n do .env."""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return {
            "base_url": os.getenv("N8N_BASE_URL", "http://localhost:5678"),
            "api_key": os.getenv("N8N_API_KEY", ""),
        }

    def _n8n_disponivel(self) -> bool:
        """Verifica se n8n está rodando."""
        try:
            import requests
            cfg = self._get_n8n_config()
            r = requests.get(f"{cfg['base_url']}/healthz", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def _postar_workflow(self, workflow_json: dict) -> dict:
        """Posta workflow na API do n8n."""
        try:
            import requests
            cfg = self._get_n8n_config()
            headers = {"Content-Type": "application/json"}
            if cfg["api_key"]:
                headers["X-N8N-API-KEY"] = cfg["api_key"]

            r = requests.post(
                f"{cfg['base_url']}/api/v1/workflows",
                json=workflow_json,
                headers=headers,
                timeout=10
            )
            if r.status_code in (200, 201):
                data = r.json()
                # Ativa o workflow
                wf_id = data.get("id")
                if wf_id:
                    requests.post(
                        f"{cfg['base_url']}/api/v1/workflows/{wf_id}/activate",
                        headers=headers,
                        timeout=5
                    )
                return {"success": True, "id": wf_id, "data": data}
            return {"success": False, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute(self, command: str, params: dict = None, context: dict = None) -> SkillResult:
        cmd = command.lower()
        try:
            if any(w in cmd for w in ["follow-up", "followup", "sequencia", "7 dias"]):
                return self._criar_followup(command)
            elif any(w in cmd for w in ["qualificacao", "qualificar", "scoring"]):
                return self._criar_qualificacao(command)
            elif any(w in cmd for w in ["listar", "ver", "meus workflows", "meus fluxos"]):
                return self._listar_workflows()
            else:
                return self._criar_funil_captura(command)
        except Exception as e:
            log.error(f"N8nSkill erro: {e}")
            return SkillResult(success=False, message=f"Erro ao criar workflow: {e}")

    def _extrair_nicho(self, command: str) -> str:
        palavras_remover = [
            "crie", "criar", "monte", "montar", "funil", "fluxo", "automacao",
            "workflow", "para", "de", "do", "da", "um", "uma", "n8n",
            "sequencia", "follow", "up", "disparo", "mensagem"
        ]
        palavras = command.lower().split()
        nicho = " ".join(w for w in palavras if w not in palavras_remover)
        return nicho.strip() or "negocio"

    def _gerar_json_funil(self, nicho: str, webhook_id: str) -> dict:
        """Gera JSON completo do workflow n8n para funil de captura."""
        return {
            "name": f"Funil - {nicho.title()} [{datetime.now().strftime('%d/%m/%Y')}]",
            "nodes": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Webhook - Captura Lead",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300],
                    "parameters": {
                        "path": webhook_id,
                        "responseMode": "onReceived",
                        "responseData": "allEntries"
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Qualifica Lead",
                    "type": "n8n-nodes-base.if",
                    "typeVersion": 1,
                    "position": [500, 300],
                    "parameters": {
                        "conditions": {
                            "string": [{
                                "value1": "={{$json['telefone']}}",
                                "operation": "isNotEmpty"
                            }]
                        }
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Envia Mensagem Boas-Vindas",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 1,
                    "position": [750, 200],
                    "parameters": {
                        "url": "https://api.whatsapp.com/send",
                        "method": "POST",
                        "bodyParametersUi": {
                            "parameter": [
                                {"name": "phone", "value": "={{$json['telefone']}}"},
                                {"name": "message", "value": f"Ola! Obrigado pelo interesse em {nicho}. Entrarei em contato em breve!"}
                            ]
                        }
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Salva no CRM",
                    "type": "n8n-nodes-base.set",
                    "typeVersion": 1,
                    "position": [750, 400],
                    "parameters": {
                        "values": {
                            "string": [
                                {"name": "status", "value": "novo_lead"},
                                {"name": "nicho", "value": nicho},
                                {"name": "data_captacao", "value": "={{new Date().toISOString()}}"}
                            ]
                        }
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Aguarda 24h",
                    "type": "n8n-nodes-base.wait",
                    "typeVersion": 1,
                    "position": [1000, 200],
                    "parameters": {
                        "resume": "timeInterval",
                        "amount": 24,
                        "unit": "hours"
                    }
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Follow-up Dia 2",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 1,
                    "position": [1250, 200],
                    "parameters": {
                        "url": "https://api.whatsapp.com/send",
                        "method": "POST",
                        "bodyParametersUi": {
                            "parameter": [
                                {"name": "phone", "value": "={{$json['telefone']}}"},
                                {"name": "message", "value": f"Ola! Separei um conteudo especial sobre {nicho} para voce. Tem 2 minutos?"}
                            ]
                        }
                    }
                }
            ],
            "connections": {
                "Webhook - Captura Lead": {
                    "main": [[{"node": "Qualifica Lead", "type": "main", "index": 0}]]
                },
                "Qualifica Lead": {
                    "main": [
                        [{"node": "Envia Mensagem Boas-Vindas", "type": "main", "index": 0}],
                        [{"node": "Salva no CRM", "type": "main", "index": 0}]
                    ]
                },
                "Envia Mensagem Boas-Vindas": {
                    "main": [[{"node": "Aguarda 24h", "type": "main", "index": 0}]]
                },
                "Aguarda 24h": {
                    "main": [[{"node": "Follow-up Dia 2", "type": "main", "index": 0}]]
                }
            },
            "active": True,
            "settings": {}
        }

    def _criar_funil_captura(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        webhook_id = f"funil-{nicho.replace(' ', '-').lower()}-{uuid.uuid4().hex[:6]}"

        workflow_json = self._gerar_json_funil(nicho, webhook_id)

        # Salva JSON localmente sempre
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        json_path = DATA_DIR / f"funil_{nicho.replace(' ', '_')}.json"
        json_path.write_text(json.dumps(workflow_json, ensure_ascii=False, indent=2), encoding="utf-8")

        # Tenta postar no n8n
        n8n_ok = self._n8n_disponivel()
        resultado_post = {}

        if n8n_ok:
            resultado_post = self._postar_workflow(workflow_json)

        cfg = self._get_n8n_config()
        webhook_url = f"{cfg['base_url']}/webhook/{webhook_id}"

        if n8n_ok and resultado_post.get("success"):
            mensagem = f"""[N8N] WORKFLOW CRIADO E ATIVADO

FUNIL: {nicho.title()}
Status: ATIVO
Webhook URL: {webhook_url}

FLUXO:
  1. Lead preenche formulario → Webhook recebe
  2. Qualificacao automatica (tem telefone?)
  3. Mensagem de boas-vindas (WhatsApp)
  4. Aguarda 24h
  5. Follow-up automatico Dia 2
  + Continua por 7 dias automaticamente

COMO USAR:
  Cole esta URL no seu formulario/landing page:
  {webhook_url}

  Quando alguem preencher → automacao dispara sozinha!

ARQUIVO: {json_path}
"""
        else:
            mensagem = f"""[N8N] WORKFLOW GERADO (n8n offline - importe manualmente)

FUNIL: {nicho.title()}
Webhook configurado: /webhook/{webhook_id}

FLUXO DO WORKFLOW:
  1. Webhook (captura lead)
  2. If (qualificacao: tem telefone?)
  3. HTTP Request (envia WhatsApp boas-vindas)
  4. Wait (aguarda 24h)
  5. HTTP Request (follow-up Dia 2)

PARA ATIVAR:
  1. Instale n8n: npm install -g n8n
  2. Rode: n8n start
  3. Importe: {json_path}
  4. Ou configure N8N_BASE_URL no .env e rode novamente

ARQUIVO JSON SALVO: {json_path}
"""

        return SkillResult(success=True, message=mensagem,
                           data={"workflow": workflow_json, "webhook_id": webhook_id, "arquivo": str(json_path)})

    def _criar_followup(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        webhook_id = f"followup-{uuid.uuid4().hex[:6]}"

        dias = [
            ("Dia 1", "Primeiro contato - boas-vindas"),
            ("Dia 2", "Conteudo de valor gratuito"),
            ("Dia 3", "Prova social - caso de sucesso"),
            ("Dia 5", "Pergunta estrategica sobre dor"),
            ("Dia 7", "Oferta direta com CTA"),
            ("Dia 10", "Ultimo follow-up - sem pressao"),
        ]

        linhas = [f"[N8N] SEQUENCIA DE FOLLOW-UP - {nicho.upper()}", ""]
        linhas.append("WORKFLOW GERADO COM:")
        for dia, desc in dias:
            linhas.append(f"  {dia}: {desc}")

        linhas += ["", f"Webhook: /webhook/{webhook_id}",
                   f"JSON salvo em: data/n8n/followup_{nicho.replace(' ', '_')}.json",
                   "", "Para ativar: importe o JSON no n8n ou configure N8N_BASE_URL no .env"]

        # Salva JSON simplificado
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        json_path = DATA_DIR / f"followup_{nicho.replace(' ', '_')}.json"
        json_path.write_text(json.dumps({"name": f"Follow-up {nicho}", "webhook": webhook_id,
                                          "dias": [{"dia": d, "desc": desc} for d, desc in dias]},
                                         ensure_ascii=False, indent=2), encoding="utf-8")

        return SkillResult(success=True, message="\n".join(linhas))

    def _criar_qualificacao(self, command: str) -> SkillResult:
        nicho = self._extrair_nicho(command)
        mensagem = f"""[N8N] FLUXO DE QUALIFICACAO - {nicho.upper()}

CRITERIOS DE SCORE:
  +30 pts: Tem telefone valido
  +20 pts: Email corporativo (nao gmail/hotmail)
  +25 pts: Respondeu mensagem de boas-vindas
  +15 pts: Abriu email de followup
  +10 pts: Visitou pagina de preco

CLASSIFICACAO:
  80-100: HOT LEAD → Contato imediato da equipe
  50-79:  WARM LEAD → Sequencia automatica
  0-49:   COLD LEAD → Nurturing de longo prazo

WORKFLOW N8N:
  Webhook → Calcula Score → If (>80?) → Notifica Vendedor
                                      → Entra na Sequencia

JSON salvo em: data/n8n/qualificacao_{nicho.replace(' ', '_')}.json
"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / f"qualificacao_{nicho.replace(' ', '_')}.json").write_text(
            json.dumps({"name": f"Qualificacao {nicho}", "criterios": ["telefone", "email", "resposta"]},
                       ensure_ascii=False), encoding="utf-8")

        return SkillResult(success=True, message=mensagem)

    def _listar_workflows(self) -> SkillResult:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        arquivos = list(DATA_DIR.glob("*.json"))

        if not arquivos:
            return SkillResult(success=True, message="[N8N] Nenhum workflow criado ainda. Use 'crie um funil para [nicho]'!")

        linhas = ["[N8N] WORKFLOWS CRIADOS", ""]
        for arq in arquivos:
            try:
                data = json.loads(arq.read_text(encoding="utf-8"))
                nome = data.get("name", arq.stem)
                linhas.append(f"  {nome}")
                linhas.append(f"    Arquivo: {arq}")
            except Exception:
                linhas.append(f"  {arq.name}")

        # Verifica n8n online
        if self._n8n_disponivel():
            linhas.append("\n[n8n ONLINE] Workflows sendo executados!")
        else:
            linhas.append("\n[n8n OFFLINE] Configure N8N_BASE_URL no .env para ativar")

        return SkillResult(success=True, message="\n".join(linhas))
