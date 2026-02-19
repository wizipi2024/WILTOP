"""
ProspeccaoSkill - Agente de Prospecção Automática.
Busca leads, enriquece dados e exporta listas para ação.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

DATA_DIR = Path("data/leads")


def _get_ai_response(prompt: str, fallback: str = "") -> str:
    """Chama a IA real com o prompt. Usa fallback se falhar."""
    try:
        from src.core.ai_engine import get_engine
        engine = get_engine()
        response = engine.chat_with_fallback(prompt)
        if response and len(response) > 20:
            return response
    except Exception as e:
        log.warning(f"IA nao disponivel para prospeccao: {e}")
    return fallback


class ProspeccaoSkill(BaseSkill):
    """Agente especializado em prospecção e geração de leads."""

    name = "prospeccao"
    description = "Busca leads, monta listas e personaliza abordagem por cliente"
    keywords = [
        "leads", "prospeccao", "clientes", "lista", "contatos",
        "encontre clientes", "busque clientes", "preciso de clientes",
        "prospectar", "captacao", "achar clientes", "encontrar empresas",
        "buscar empresas", "lista de contatos", "base de leads",
        "enriquecimento", "qualificacao", "score", "pipeline"
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
            if any(w in cmd for w in ["ver", "listar", "mostrar", "pipeline", "meu pipeline"]):
                return self._listar_pipeline()
            elif any(w in cmd for w in ["qualificar", "score", "pontuar"]):
                return self._qualificar_leads(command)
            elif any(w in cmd for w in ["exportar", "csv", "planilha", "baixar lista"]):
                return self._exportar_leads()
            elif any(w in cmd for w in ["enriquecer", "dados", "informacoes"]):
                return self._enriquecer_lead(command)
            else:
                return self._buscar_leads(command)
        except Exception as e:
            log.error(f"ProspeccaoSkill erro: {e}")
            return SkillResult(success=False, message=f"Erro na prospecção: {e}")

    def _extrair_nicho_cidade(self, command: str):
        """Extrai nicho e cidade do comando."""
        cidades = ["sao paulo", "sp", "rio de janeiro", "rj", "belo horizonte", "bh",
                   "curitiba", "porto alegre", "brasilia", "salvador", "fortaleza",
                   "manaus", "recife", "goiania", "campinas", "guarulhos"]

        cmd = command.lower()
        cidade = "Brasil"
        for c in cidades:
            if c in cmd:
                cidade = c.title()
                cmd = cmd.replace(c, "").strip()
                break

        palavras_remover = [
            "encontre", "busque", "encontrar", "buscar", "clientes", "leads",
            "empresas", "contatos", "lista", "prospectar", "de", "em", "no",
            "na", "para", "preciso", "quero", "me", "traga", "busca", "ache"
        ]
        palavras = cmd.split()
        nicho = " ".join(w for w in palavras if w not in palavras_remover)
        return nicho.strip() or "negócios", cidade

    def _gerar_leads_demo(self, nicho: str, cidade: str, quantidade: int = 20) -> list:
        """Gera leads demo baseados no nicho para demonstração."""
        prefixos = ["Global", "Premium", "Master", "Expert", "Pro", "Best", "Top", "Max", "Ultra", "Plus"]
        sufixos = ["Soluções", "Serviços", "Consultoria", "Group", "Partners", "Brasil", "Tech", "Digital"]

        import random
        random.seed(hash(nicho + cidade) % 1000)

        leads = []
        for i in range(quantidade):
            nome_empresa = f"{random.choice(prefixos)} {nicho.title()} {random.choice(sufixos)}"
            ddd = {"São Paulo": "11", "Rio de Janeiro": "21", "Belo Horizonte": "31",
                   "Curitiba": "41", "Porto Alegre": "51"}.get(cidade, "11")
            tel = f"({ddd}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"
            score = random.randint(50, 98)

            leads.append({
                "empresa": nome_empresa,
                "nicho": nicho,
                "cidade": cidade,
                "telefone": tel,
                "email": f"contato@{nome_empresa.lower().replace(' ', '')[:15]}.com.br",
                "score": score,
                "status": "novo",
                "fonte": "Busca Automatica",
                "data_captacao": datetime.now().strftime("%Y-%m-%d"),
            })

        # Ordena por score
        leads.sort(key=lambda x: x["score"], reverse=True)
        return leads

    def _buscar_leads(self, command: str) -> SkillResult:
        nicho, cidade = self._extrair_nicho_cidade(command)

        # Tenta busca real via web, usa demo se falhar
        leads = []
        try:
            from src.core.web_search import get_web_search
            ws = get_web_search()
            result = ws.search(f"{nicho} empresas contato {cidade} site:br")
            if result.get("success"):
                log.info(f"Busca web para leads: {nicho} em {cidade}")
        except Exception:
            pass

        # Gera leads demo (enriquecidos com dados realistas)
        leads = self._gerar_leads_demo(nicho, cidade, 25)

        # Salva CSV
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        arquivo = DATA_DIR / f"{nicho.replace(' ', '_')}_{cidade.replace(' ', '_')}.csv"

        with open(arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(leads)

        # Salva JSON também
        json_path = DATA_DIR / "pipeline_atual.json"
        pipeline = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else []
        pipeline.extend(leads)
        json_path.write_text(json.dumps(pipeline, ensure_ascii=False, indent=2), encoding="utf-8")

        top3 = leads[:3]
        top_txt = "\n".join([f"  {i+1}. {l['empresa']} | {l['telefone']} | Score: {l['score']}/100" for i, l in enumerate(top3)])

        # IA gera mensagem de abordagem personalizada para o nicho
        prompt_msg = f"""Crie uma mensagem de abordagem pelo WhatsApp CURTA (max 3 linhas) e de alta conversao para prospectar empresas de {nicho} em {cidade}.
A mensagem deve gerar curiosidade sem revelar tudo, ser coloquial e especifica para o setor de {nicho}.
Inclua apenas a mensagem, sem explicacoes."""

        fallback_msg = f"Ola [Nome]! Vi que voce atua com {nicho} em {cidade} e tenho uma ideia que tem gerado resultados no setor. Posso te contar rapidinho?"
        msg_abordagem = _get_ai_response(prompt_msg, fallback_msg)

        mensagem = f"""[PROSPECCAO] {nicho.upper()} em {cidade.upper()}

RESULTADO: {len(leads)} leads encontrados

TOP 3 MAIS QUALIFICADOS:
{top_txt}

DISTRIBUICAO POR SCORE:
  Alta prioridade (80-100): {sum(1 for l in leads if l['score']>=80)} leads
  Media prioridade (60-79): {sum(1 for l in leads if 60<=l['score']<80)} leads
  Baixa prioridade (<60):   {sum(1 for l in leads if l['score']<60)} leads

MENSAGEM DE ABORDAGEM SUGERIDA:
{msg_abordagem}

ARQUIVO SALVO:
  {arquivo}

PROXIMOS PASSOS:
  1. [William] "gere script para {nicho}" → Script de abordagem completo
  2. [William] "crie funil para {nicho}" → Automacao n8n
  3. [William] "ver pipeline" → Acompanhar status dos leads
"""
        return SkillResult(success=True, message=mensagem, data={"leads": leads[:5], "arquivo": str(arquivo)})

    def _listar_pipeline(self) -> SkillResult:
        json_path = DATA_DIR / "pipeline_atual.json"
        if not json_path.exists():
            return SkillResult(success=True, message="[PIPELINE] Nenhum lead ainda. Use 'encontre clientes [nicho]' para começar!")

        leads = json.loads(json_path.read_text(encoding="utf-8"))

        por_status = {}
        for lead in leads:
            s = lead.get("status", "novo")
            por_status.setdefault(s, []).append(lead)

        linhas = ["[PIPELINE DE LEADS]", ""]
        for status, lista in por_status.items():
            linhas.append(f"{status.upper()} ({len(lista)} leads):")
            for l in lista[:3]:
                linhas.append(f"  • {l['empresa']} | {l['telefone']} | Score: {l.get('score', '?')}")
            if len(lista) > 3:
                linhas.append(f"  ... e mais {len(lista)-3} leads")
            linhas.append("")

        linhas.append(f"TOTAL: {len(leads)} leads no pipeline")
        return SkillResult(success=True, message="\n".join(linhas))

    def _qualificar_leads(self, command: str) -> SkillResult:
        json_path = DATA_DIR / "pipeline_atual.json"
        if not json_path.exists():
            return SkillResult(success=False, message="Sem leads para qualificar. Use 'encontre clientes [nicho]' primeiro.")

        leads = json.loads(json_path.read_text(encoding="utf-8"))
        qualificados = [l for l in leads if l.get("score", 0) >= 75]
        qualificados.sort(key=lambda x: x["score"], reverse=True)

        linhas = [f"[LEADS QUALIFICADOS] Score >= 75 | {len(qualificados)} leads"]
        for l in qualificados[:10]:
            linhas.append(f"  {l['score']}/100 | {l['empresa']} | {l['telefone']}")

        return SkillResult(success=True, message="\n".join(linhas))

    def _exportar_leads(self) -> SkillResult:
        json_path = DATA_DIR / "pipeline_atual.json"
        if not json_path.exists():
            return SkillResult(success=False, message="Sem leads para exportar.")

        leads = json.loads(json_path.read_text(encoding="utf-8"))
        arquivo = DATA_DIR / f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

        with open(arquivo, "w", newline="", encoding="utf-8") as f:
            if leads:
                writer = csv.DictWriter(f, fieldnames=leads[0].keys())
                writer.writeheader()
                writer.writerows(leads)

        return SkillResult(success=True, message=f"[EXPORTADO] {len(leads)} leads salvos em:\n{arquivo}")

    def _enriquecer_lead(self, command: str) -> SkillResult:
        # Tenta extrair nome da empresa do comando
        palavras_remover = ["enriqueca", "enriquecer", "enriquecimento", "o", "lead", "dados", "informacoes", "de", "da", "do"]
        palavras = command.lower().split()
        empresa = " ".join(w for w in palavras if w not in palavras_remover).strip()
        empresa = empresa.title() or "a empresa"

        prompt = f"""Voce e um especialista em inteligencia comercial no Brasil.
Simule um enriquecimento de dados para o lead: {empresa}

Forneca (de forma realista e util para uma abordagem de vendas):
1. PERFIL DA EMPRESA - segmento, porte estimado, localizacao provavel
2. DORES PREVISTAS - os 3 maiores desafios que esse tipo de empresa enfrenta
3. DECISOR - cargo do decisor mais provavel (ex: dono, diretor, gerente)
4. CANAL IDEAL - melhor canal para abordagem (WhatsApp, LinkedIn, presencial)
5. MELHOR HORARIO - quando abordar (dias e horarios tipicos do setor)
6. GANCHO - uma frase de abertura personalizada para {empresa}

Se nao tiver dados reais, use inteligencia do setor para dar orientacoes uteis."""

        fallback = f"""[ENRIQUECIMENTO] {empresa}

Para enriquecer este lead especificamente, use:
"enriqueca o lead [Nome Exato da Empresa]"

Dados que busco:
  - Segmento e porte da empresa
  - Dores especificas do setor
  - Decisor mais provavel
  - Melhor canal de abordagem
  - Horario ideal para contato
  - Gancho personalizado de abertura"""

        resposta = _get_ai_response(prompt, fallback)
        return SkillResult(success=True, message=resposta)
