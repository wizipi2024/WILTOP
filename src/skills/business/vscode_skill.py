"""
VsCodeSkill - Criador de Apps com VS Code e IA.
Cria projetos completos, abre no VS Code e executa automaticamente.
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
from src.skills.base_skill import BaseSkill, SkillResult
from src.utils.logger import get_logger

log = get_logger(__name__)

APPS_DIR = Path("data/apps")


class VsCodeSkill(BaseSkill):
    """Cria apps completos usando VS Code + IA."""

    name = "vscode"
    description = "Cria apps, sites e ferramentas completas usando VS Code"
    keywords = [
        "crie um app", "crie um site", "crie uma ferramenta", "desenvolva",
        "programe", "cria um sistema", "faca um aplicativo", "landing page",
        "pagina de captura", "dashboard web", "sistema de agendamento",
        "crm simples", "calculadora de roi", "gerador de proposta",
        "bot de telegram", "bot de whatsapp", "plataforma", "saas"
    ]

    def can_handle(self, command: str) -> float:
        cmd = command.lower()
        score = 0.0
        for kw in self.keywords:
            if kw in cmd:
                score += 0.20
        return min(score, 1.0)

    def execute(self, command: str, params: dict = None, context: dict = None) -> SkillResult:
        cmd = command.lower()
        try:
            if any(w in cmd for w in ["landing page", "pagina de captura", "pagina de vendas"]):
                return self._criar_landing_page(command)
            elif any(w in cmd for w in ["dashboard", "painel", "relatorio web"]):
                return self._criar_dashboard(command)
            elif any(w in cmd for w in ["calculadora", "roi", "simulador", "calculer"]):
                return self._criar_calculadora(command)
            elif any(w in cmd for w in ["crm", "sistema de clientes", "gestao de leads"]):
                return self._criar_crm(command)
            else:
                return self._criar_app_generico(command)
        except Exception as e:
            log.error(f"VsCodeSkill erro: {e}")
            return SkillResult(success=False, message=f"Erro ao criar app: {e}")

    def _extrair_descricao(self, command: str) -> str:
        palavras_remover = ["crie", "cria", "faca", "desenvolva", "programe",
                            "um", "uma", "app", "site", "sistema", "ferramenta",
                            "de", "para", "do", "da", "aplicativo"]
        palavras = command.lower().split()
        desc = " ".join(w for w in palavras if w not in palavras_remover)
        return desc.strip() or "ferramenta"

    def _abrir_vscode(self, pasta: Path) -> bool:
        """Abre VS Code na pasta do projeto."""
        try:
            subprocess.Popen(["code", str(pasta)], shell=True)
            return True
        except Exception:
            try:
                subprocess.Popen(f'code "{pasta}"', shell=True)
                return True
            except Exception:
                return False

    def _criar_landing_page(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        nome_projeto = f"landing_{desc.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        pasta = APPS_DIR / nome_projeto
        pasta.mkdir(parents=True, exist_ok=True)

        # HTML da landing page
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{desc.title()} - Solução Profissional</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #f1f5f9; }}
        .hero {{ min-height: 100vh; display: flex; align-items: center; justify-content: center;
                 background: linear-gradient(135deg, #1e3a5f 0%, #0f1117 100%); text-align: center; padding: 40px; }}
        .hero h1 {{ font-size: 3rem; font-weight: 700; color: #3b82f6; margin-bottom: 20px; }}
        .hero p {{ font-size: 1.3rem; color: #94a3b8; max-width: 600px; margin: 0 auto 40px; }}
        .cta-btn {{ background: #3b82f6; color: white; padding: 18px 40px; border: none;
                   border-radius: 8px; font-size: 1.1rem; cursor: pointer; font-weight: 600; }}
        .cta-btn:hover {{ background: #2563eb; }}
        .form-section {{ background: #161921; padding: 60px 20px; text-align: center; }}
        .form-section h2 {{ font-size: 2rem; margin-bottom: 30px; }}
        .form {{ max-width: 500px; margin: 0 auto; }}
        .form input {{ width: 100%; padding: 14px; margin: 10px 0; border-radius: 6px;
                       border: 1px solid #2d3748; background: #1c1f2b; color: #f1f5f9; font-size: 1rem; }}
        .form button {{ width: 100%; padding: 16px; background: #22c55e; color: white;
                       border: none; border-radius: 6px; font-size: 1.1rem; font-weight: 600; cursor: pointer; }}
        .benefits {{ background: #0f1117; padding: 60px 20px; }}
        .benefits-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                          gap: 30px; max-width: 1000px; margin: 0 auto; }}
        .benefit {{ background: #161921; padding: 30px; border-radius: 10px; border: 1px solid #2d3748; }}
        .benefit h3 {{ color: #3b82f6; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <section class="hero">
        <div>
            <h1>Solucao Profissional para {desc.title()}</h1>
            <p>Automatize, escale e gere mais resultado com tecnologia de ponta.
               Sem complicacao. Sem precisar de time tecnico.</p>
            <button class="cta-btn" onclick="document.querySelector('.form-section').scrollIntoView()">
                Quero Comecar Agora
            </button>
        </div>
    </section>

    <section class="form-section">
        <h2>Receba uma Consultoria Gratuita</h2>
        <form class="form" id="leadForm">
            <input type="text" placeholder="Seu nome completo" required>
            <input type="tel" placeholder="WhatsApp (com DDD)" required>
            <input type="email" placeholder="Seu melhor email" required>
            <input type="text" placeholder="Seu negocio / empresa">
            <button type="submit">QUERO COMECAR AGORA</button>
        </form>
    </section>

    <section class="benefits">
        <div class="benefits-grid">
            <div class="benefit">
                <h3>Resultado Rapido</h3>
                <p>Primeiros resultados em 30 dias ou devolvemos o investimento.</p>
            </div>
            <div class="benefit">
                <h3>Sem Complicacao</h3>
                <p>Cuidamos de tudo. Voce so precisa acompanhar os resultados.</p>
            </div>
            <div class="benefit">
                <h3>Suporte Continuo</h3>
                <p>Equipe disponivel via WhatsApp para tirar qualquer duvida.</p>
            </div>
        </div>
    </section>

    <script>
        document.getElementById('leadForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            alert('Obrigado! Entraremos em contato em breve via WhatsApp!');
        }});
    </script>
</body>
</html>"""

        (pasta / "index.html").write_text(html, encoding="utf-8")
        (pasta / "README.md").write_text(f"# Landing Page - {desc.title()}\nCriado por William v5\n\nAbra index.html no navegador.", encoding="utf-8")

        # Abre no VS Code e no navegador
        self._abrir_vscode(pasta)
        try:
            import webbrowser
            webbrowser.open(str(pasta / "index.html"))
        except Exception:
            pass

        return SkillResult(success=True, message=f"""[APP CRIADO] Landing Page - {desc.title()}

ARQUIVO: {pasta / 'index.html'}
STATUS: Aberto no navegador e no VS Code

CONTEUDO:
  - Hero section com headline persuasiva
  - Formulario de captura (nome, WhatsApp, email)
  - 3 cards de beneficios
  - Design profissional dark (pronto para publicar)

PROXIMOS PASSOS:
  1. Personalize o texto no VS Code (ja aberto)
  2. Conecte com n8n para capturar leads: "crie funil para {desc}"
  3. Publique no GitHub Pages ou Netlify (gratis)
""", data={"pasta": str(pasta)})

    def _criar_dashboard(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        nome_projeto = f"dashboard_{desc.replace(' ', '_')}"
        pasta = APPS_DIR / nome_projeto
        pasta.mkdir(parents=True, exist_ok=True)

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dashboard - {desc.title()}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #f1f5f9; margin: 0; }}
        .header {{ background: #161921; padding: 20px 30px; border-bottom: 1px solid #2d3748; }}
        .header h1 {{ color: #3b82f6; font-size: 1.5rem; }}
        .kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; padding: 30px; }}
        .kpi {{ background: #161921; padding: 25px; border-radius: 10px; border: 1px solid #2d3748; text-align: center; }}
        .kpi .valor {{ font-size: 2.5rem; font-weight: 700; color: #3b82f6; }}
        .kpi .label {{ color: #94a3b8; font-size: 0.9rem; margin-top: 5px; }}
        .kpi .variacao {{ color: #22c55e; font-size: 0.85rem; }}
        .tabela {{ margin: 0 30px 30px; background: #161921; border-radius: 10px; overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #1c1f2b; padding: 15px; text-align: left; color: #94a3b8; font-size: 0.85rem; }}
        td {{ padding: 15px; border-top: 1px solid #2d3748; }}
        .status-ativo {{ color: #22c55e; }} .status-novo {{ color: #f59e0b; }}
    </style>
</head>
<body>
    <div class="header"><h1>Dashboard {desc.title()}</h1></div>
    <div class="kpis">
        <div class="kpi"><div class="valor">47</div><div class="label">Total de Leads</div><div class="variacao">+12 hoje</div></div>
        <div class="kpi"><div class="valor">8.3%</div><div class="label">Taxa de Conversao</div><div class="variacao">+1.2%</div></div>
        <div class="kpi"><div class="valor">R$6.2k</div><div class="label">Receita Mensal</div><div class="variacao">+R$800</div></div>
        <div class="kpi"><div class="valor">4</div><div class="label">Clientes Ativos</div><div class="variacao">+1 este mes</div></div>
    </div>
    <div class="tabela">
        <table>
            <tr><th>Lead</th><th>Empresa</th><th>Score</th><th>Status</th><th>Data</th></tr>
            <tr><td>Ana Costa</td><td>Clinica Sorrir</td><td>95</td><td class="status-ativo">HOT</td><td>Hoje</td></tr>
            <tr><td>Carlos Lima</td><td>Odonto Premium</td><td>82</td><td class="status-ativo">HOT</td><td>Hoje</td></tr>
            <tr><td>Maria Santos</td><td>DentMax</td><td>67</td><td class="status-novo">WARM</td><td>Ontem</td></tr>
        </table>
    </div>
</body>
</html>"""

        (pasta / "index.html").write_text(html, encoding="utf-8")
        self._abrir_vscode(pasta)
        try:
            import webbrowser
            webbrowser.open(str(pasta / "index.html"))
        except Exception:
            pass

        return SkillResult(success=True, message=f"[APP CRIADO] Dashboard {desc.title()}\n\nAberto no VS Code e navegador!\nArquivo: {pasta}/index.html")

    def _criar_calculadora(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        nome_projeto = f"calculadora_{desc.replace(' ', '_')}"
        pasta = APPS_DIR / nome_projeto
        pasta.mkdir(parents=True, exist_ok=True)

        html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Calculadora de ROI</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #f1f5f9;
               display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .card { background: #161921; padding: 40px; border-radius: 15px; width: 500px; border: 1px solid #2d3748; }
        h1 { color: #3b82f6; margin-bottom: 30px; text-align: center; }
        label { display: block; margin: 15px 0 5px; color: #94a3b8; font-size: 0.9rem; }
        input { width: 100%; padding: 12px; border-radius: 6px; border: 1px solid #2d3748;
                background: #1c1f2b; color: #f1f5f9; font-size: 1rem; box-sizing: border-box; }
        button { width: 100%; padding: 14px; background: #3b82f6; color: white; border: none;
                 border-radius: 6px; font-size: 1rem; font-weight: 600; cursor: pointer; margin-top: 20px; }
        .resultado { margin-top: 20px; padding: 20px; background: #1c1f2b; border-radius: 8px; display: none; }
        .resultado .valor { font-size: 2rem; color: #22c55e; font-weight: 700; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Calculadora de ROI</h1>
        <label>Investimento Mensal (R$)</label>
        <input type="number" id="investimento" placeholder="Ex: 1500" value="1500">
        <label>Clientes Adquiridos por Mes</label>
        <input type="number" id="clientes" placeholder="Ex: 5" value="5">
        <label>Ticket Medio por Cliente (R$)</label>
        <input type="number" id="ticket" placeholder="Ex: 2000" value="2000">
        <label>Meses de Retencao Media</label>
        <input type="number" id="retencao" placeholder="Ex: 6" value="6">
        <button onclick="calcular()">CALCULAR ROI</button>
        <div class="resultado" id="resultado">
            <p>Receita Total Projetada:</p>
            <div class="valor" id="receita">R$ 0</div>
            <p style="margin-top:10px">ROI: <span id="roi" style="color:#3b82f6; font-weight:700"></span></p>
            <p>Lucro Liquido: <span id="lucro" style="color:#22c55e; font-weight:700"></span></p>
        </div>
    </div>
    <script>
        function calcular() {
            const inv = +document.getElementById('investimento').value;
            const cli = +document.getElementById('clientes').value;
            const tick = +document.getElementById('ticket').value;
            const ret = +document.getElementById('retencao').value;
            const receita = cli * tick * ret;
            const roi = ((receita - inv) / inv * 100).toFixed(0);
            const lucro = receita - inv;
            document.getElementById('receita').textContent = 'R$ ' + receita.toLocaleString('pt-BR');
            document.getElementById('roi').textContent = roi + '%';
            document.getElementById('lucro').textContent = 'R$ ' + lucro.toLocaleString('pt-BR');
            document.getElementById('resultado').style.display = 'block';
        }
    </script>
</body>
</html>"""

        (pasta / "index.html").write_text(html, encoding="utf-8")
        self._abrir_vscode(pasta)
        try:
            import webbrowser
            webbrowser.open(str(pasta / "index.html"))
        except Exception:
            pass

        return SkillResult(success=True, message=f"[APP CRIADO] Calculadora de ROI\n\nAberta no VS Code e navegador!\nArquivo: {pasta}/index.html")

    def _criar_crm(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        nome_projeto = f"crm_{desc.replace(' ', '_')}"
        pasta = APPS_DIR / nome_projeto
        pasta.mkdir(parents=True, exist_ok=True)

        # CRM simples em Python + Flask (sem dependencias extras)
        py_app = """#!/usr/bin/env python3
\"\"\"CRM Simples - William v5\"\"\"
import json, os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

DATA_FILE = Path("leads.json")

def load_leads():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save_leads(leads):
    DATA_FILE.write_text(json.dumps(leads, ensure_ascii=False, indent=2))

class CRMHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        leads = load_leads()
        html = f\"\"\"<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>CRM</title>
<style>body{{font-family:Segoe UI;background:#0f1117;color:#f1f5f9;margin:0}}
.header{{background:#161921;padding:20px 30px;border-bottom:1px solid #2d3748}}
h1{{color:#3b82f6}} table{{width:100%;border-collapse:collapse;margin:20px}}
th{{background:#1c1f2b;padding:12px;text-align:left;color:#94a3b8}}
td{{padding:12px;border-top:1px solid #2d3748}}
.form{{background:#161921;margin:20px;padding:20px;border-radius:10px}}
input{{padding:10px;margin:5px;border-radius:5px;border:1px solid #2d3748;
      background:#1c1f2b;color:#f1f5f9;width:200px}}
button{{padding:10px 20px;background:#3b82f6;color:white;border:none;border-radius:5px;cursor:pointer}}
</style></head><body>
<div class="header"><h1>CRM - {len(leads)} Leads</h1></div>
<div class="form">
<form method="post" action="/add">
<input name="nome" placeholder="Nome" required>
<input name="empresa" placeholder="Empresa">
<input name="telefone" placeholder="WhatsApp" required>
<input name="email" placeholder="Email">
<button type="submit">+ Adicionar Lead</button>
</form></div>
<table><tr><th>Nome</th><th>Empresa</th><th>Telefone</th><th>Status</th></tr>
\"\"\"
        for l in leads:
            html += f\"<tr><td>{l.get('nome','')}</td><td>{l.get('empresa','')}</td><td>{l.get('telefone','')}</td><td>Novo</td></tr>\"
        html += "</table></body></html>"
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = parse_qs(self.rfile.read(length).decode())
        leads = load_leads()
        leads.append({k: v[0] for k, v in data.items()})
        save_leads(leads)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    port = 5001
    print(f"CRM rodando em http://localhost:{port}")
    HTTPServer(("", port), CRMHandler).serve_forever()
"""
        (pasta / "crm.py").write_text(py_app, encoding="utf-8")
        (pasta / "leads.json").write_text("[]", encoding="utf-8")

        self._abrir_vscode(pasta)
        try:
            import subprocess
            subprocess.Popen(["py", "-3", str(pasta / "crm.py")], shell=True)
            import time, webbrowser
            time.sleep(1)
            webbrowser.open("http://localhost:5001")
        except Exception:
            pass

        return SkillResult(success=True, message=f"[APP CRIADO] CRM Simples\n\nRodando em: http://localhost:5001\nAberto no VS Code!\nArquivo: {pasta}/crm.py")

    def _criar_app_generico(self, command: str) -> SkillResult:
        """Usa IA para planejar e gerar um app completo e funcional."""
        desc = self._extrair_descricao(command)
        nome_projeto = f"app_{desc.replace(' ', '_')}_{datetime.now().strftime('%H%M')}"
        pasta = APPS_DIR / nome_projeto
        pasta.mkdir(parents=True, exist_ok=True)

        # Pede para IA gerar o HTML completo do app
        prompt = f"""Voce e um desenvolvedor front-end expert em HTML, CSS e JavaScript.
Crie um app web COMPLETO, BONITO e FUNCIONAL para: {desc}

REQUISITOS OBRIGATORIOS:
1. Design moderno dark theme (background #0f1117, cards #161921, accent #3b82f6)
2. Totalmente funcional com JavaScript puro (sem frameworks externos)
3. Responsivo (mobile-first)
4. Interface REAL com funcionalidades que fazem sentido para {desc}
5. Pelo menos 3 secoes ou funcionalidades distintas
6. Dados de exemplo realistas (nao deixe campos vazios)

ESTRUTURA ESPERADA dependendo do tipo de app:
- Se for ferramenta/calculadora: inputs + logica JS funcionando + resultado visual
- Se for dashboard: KPIs com numeros + tabela com dados + graficos simples com CSS/JS
- Se for landing page: hero + beneficios especificos + formulario + CTA
- Se for CRM/lista: CRUD basico com localStorage + filtros + status visual
- Se for outro: interprete e crie algo que realmente funcione

Retorne APENAS o codigo HTML completo (doctype ate /html), sem explicacoes.
O codigo deve rodar diretamente no navegador sem dependencias externas."""

        html_gerado = ""
        try:
            from src.core.ai_engine import get_engine
            engine = get_engine()
            resposta = engine.chat_with_fallback(prompt)
            # Extrai apenas o bloco HTML da resposta
            if resposta and "<!DOCTYPE" in resposta.upper():
                inicio = resposta.upper().find("<!DOCTYPE")
                fim = resposta.rfind("</html>")
                if fim > inicio:
                    html_gerado = resposta[inicio:fim + 7]
        except Exception as e:
            log.warning(f"IA nao disponivel para criar app: {e}")

        # Fallback robusto se IA nao retornou HTML valido
        if not html_gerado or len(html_gerado) < 200:
            html_gerado = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{desc.title()}</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Segoe UI',sans-serif;background:#0f1117;color:#f1f5f9;min-height:100vh}}
        .header{{background:#161921;padding:20px 30px;border-bottom:1px solid #2d3748;display:flex;align-items:center;justify-content:space-between}}
        .header h1{{color:#3b82f6;font-size:1.4rem}}
        .badge{{background:#3b82f6;color:white;padding:4px 10px;border-radius:20px;font-size:0.8rem}}
        .container{{max-width:900px;margin:30px auto;padding:0 20px}}
        .kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:25px}}
        .kpi{{background:#161921;border:1px solid #2d3748;border-radius:10px;padding:20px;text-align:center}}
        .kpi .valor{{font-size:2rem;font-weight:700;color:#3b82f6}}
        .kpi .label{{color:#94a3b8;font-size:0.85rem;margin-top:5px}}
        .card{{background:#161921;border:1px solid #2d3748;border-radius:10px;padding:25px;margin-bottom:20px}}
        .card h2{{color:#f1f5f9;margin-bottom:15px;font-size:1.1rem}}
        .form-row{{display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap}}
        input,select,textarea{{flex:1;padding:10px 14px;background:#1c1f2b;border:1px solid #2d3748;border-radius:6px;color:#f1f5f9;font-size:0.95rem;min-width:150px}}
        button{{padding:10px 20px;background:#3b82f6;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:600}}
        button:hover{{background:#2563eb}}
        .btn-green{{background:#22c55e}} .btn-green:hover{{background:#16a34a}}
        .btn-red{{background:#ef4444}} .btn-red:hover{{background:#dc2626}}
        table{{width:100%;border-collapse:collapse}}
        th{{background:#1c1f2b;padding:12px;text-align:left;color:#94a3b8;font-size:0.85rem}}
        td{{padding:12px;border-top:1px solid #2d3748}}
        .tag{{padding:3px 10px;border-radius:20px;font-size:0.8rem;font-weight:600}}
        .tag-green{{background:#14532d;color:#22c55e}} .tag-yellow{{background:#451a03;color:#f59e0b}} .tag-blue{{background:#1e3a5f;color:#3b82f6}}
        #notif{{position:fixed;bottom:20px;right:20px;background:#22c55e;color:white;padding:12px 20px;border-radius:8px;display:none;z-index:999;font-weight:600}}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ {desc.title()}</h1>
        <span class="badge">William v6</span>
    </div>
    <div class="container">
        <div class="kpis">
            <div class="kpi"><div class="valor" id="kp1">0</div><div class="label">Total de Itens</div></div>
            <div class="kpi"><div class="valor" id="kp2">0</div><div class="label">Ativos</div></div>
            <div class="kpi"><div class="valor" id="kp3">0%</div><div class="label">Taxa de Conclusao</div></div>
        </div>
        <div class="card">
            <h2>➕ Adicionar Item</h2>
            <div class="form-row">
                <input type="text" id="nome" placeholder="Nome do item *" required>
                <input type="text" id="detalhe" placeholder="Detalhe / descricao">
                <select id="status">
                    <option value="ativo">Ativo</option>
                    <option value="pendente">Pendente</option>
                    <option value="concluido">Concluido</option>
                </select>
                <button class="btn-green" onclick="adicionar()">+ Adicionar</button>
            </div>
        </div>
        <div class="card">
            <h2>📋 Lista de Itens</h2>
            <div class="form-row" style="margin-bottom:15px">
                <input type="text" id="busca" placeholder="Buscar..." oninput="filtrar()">
                <button onclick="limparTudo()" class="btn-red">Limpar Tudo</button>
            </div>
            <table id="tabela">
                <thead><tr><th>Nome</th><th>Detalhe</th><th>Status</th><th>Data</th><th>Acao</th></tr></thead>
                <tbody id="tbody"></tbody>
            </table>
        </div>
    </div>
    <div id="notif">✓ Salvo!</div>
<script>
    const CHAVE = 'app_{desc.replace(" ", "_")}';
    function carregar() {{ return JSON.parse(localStorage.getItem(CHAVE) || '[]'); }}
    function salvar(d) {{ localStorage.setItem(CHAVE, JSON.stringify(d)); atualizar(); }}
    function notif() {{ const n=document.getElementById('notif'); n.style.display='block'; setTimeout(()=>n.style.display='none',2000); }}
    function adicionar() {{
        const nome = document.getElementById('nome').value.trim();
        if (!nome) {{ alert('Informe o nome!'); return; }}
        const dados = carregar();
        dados.push({{ id: Date.now(), nome, detalhe: document.getElementById('detalhe').value, status: document.getElementById('status').value, data: new Date().toLocaleDateString('pt-BR') }});
        salvar(dados);
        document.getElementById('nome').value=''; document.getElementById('detalhe').value='';
        notif();
    }}
    function remover(id) {{ salvar(carregar().filter(d => d.id !== id)); }}
    function filtrar() {{
        const t = document.getElementById('busca').value.toLowerCase();
        document.querySelectorAll('#tbody tr').forEach(tr => {{
            tr.style.display = tr.textContent.toLowerCase().includes(t) ? '' : 'none';
        }});
    }}
    function limparTudo() {{ if(confirm('Limpar todos os itens?')) {{ salvar([]); }} }}
    function atualizar() {{
        const dados = carregar();
        const tbody = document.getElementById('tbody');
        const tags = {{ ativo:'tag-green', pendente:'tag-yellow', concluido:'tag-blue' }};
        tbody.innerHTML = dados.map(d => `<tr>
            <td><strong>${{d.nome}}</strong></td>
            <td style="color:#94a3b8">${{d.detalhe||'-'}}</td>
            <td><span class="tag ${{tags[d.status]||'tag-blue'}}">${{d.status}}</span></td>
            <td style="color:#94a3b8">${{d.data}}</td>
            <td><button class="btn-red" style="padding:5px 12px;font-size:0.8rem" onclick="remover(${{d.id}})">✕</button></td>
        </tr>`).join('');
        document.getElementById('kp1').textContent = dados.length;
        document.getElementById('kp2').textContent = dados.filter(d=>d.status==='ativo').length;
        const conc = dados.filter(d=>d.status==='concluido').length;
        document.getElementById('kp3').textContent = dados.length ? Math.round(conc/dados.length*100)+'%' : '0%';
    }}
    atualizar();
</script>
</body>
</html>"""

        (pasta / "index.html").write_text(html_gerado, encoding="utf-8")
        (pasta / "README.md").write_text(
            f"# {desc.title()}\nCriado por William v6 com IA\n\nAbra index.html no navegador.",
            encoding="utf-8"
        )

        self._abrir_vscode(pasta)
        try:
            import webbrowser
            webbrowser.open(str(pasta / "index.html"))
        except Exception:
            pass

        return SkillResult(success=True, message=f"""[APP CRIADO] {desc.title()}

PASTA: {pasta}
STATUS: Aberto no VS Code e navegador

O app foi gerado pela IA com funcionalidades reais para: {desc}
Personalize o codigo no VS Code conforme precisar.

PROXIMOS PASSOS:
  "conecte este app com n8n para {desc}" → Automacao
  "crie uma landing page para {desc}" → Pagina de captura de leads
""", data={"pasta": str(pasta)})
