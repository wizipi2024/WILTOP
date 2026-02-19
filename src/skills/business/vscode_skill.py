"""
VsCodeSkill - Criador de Apps com IA.
Cria projetos completos: HTML, PowerPoint, Word, Excel, Python.
Fluxo: perguntas chave → planejamento → revisão dos agentes → criação do arquivo.
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
    """Cria apps, apresentações, planilhas e sites usando IA + planejamento."""

    name = "vscode"
    description = "Cria apps, apresentações PowerPoint, planilhas Excel, documentos Word e sites"
    keywords = [
        "crie um app", "crie um site", "crie uma ferramenta", "desenvolva",
        "programe", "cria um sistema", "faca um aplicativo", "landing page",
        "pagina de captura", "dashboard web", "sistema de agendamento",
        "crm simples", "calculadora de roi", "gerador de proposta",
        "bot de telegram", "bot de whatsapp", "plataforma", "saas",
        "crie uma apresentacao", "crie um powerpoint", "crie uma planilha",
        "crie um excel", "crie um documento", "crie um word",
        "fazer apresentacao", "fazer powerpoint", "fazer planilha",
        "planilha de", "apresentacao de", "documento de",
    ]

    def can_handle(self, command: str) -> float:
        cmd = command.lower()
        score = 0.0
        for kw in self.keywords:
            if kw in cmd:
                score += 0.20
        return min(score, 1.0)

    def execute(self, command: str, params: dict = None, context: dict = None) -> SkillResult:
        """
        Ponto de entrada principal.
        O fluxo de perguntas/planejamento é gerido pela GUI (william_final.py).
        Aqui recebemos os dados já coletados via params ou um comando direto.
        """
        cmd = command.lower()
        p = params or {}

        # Dados de planejamento já coletados pela GUI
        if p.get("planned") and p.get("tipo") and p.get("descricao"):
            return self._executar_plano(p)

        # Detecção direta por tipo
        try:
            if any(w in cmd for w in ["powerpoint", "apresentacao", "apresentação", "slides", "pptx"]):
                return self._criar_powerpoint_direto(command)
            elif any(w in cmd for w in ["planilha", "excel", "xlsx", "spreadsheet"]):
                return self._criar_excel_direto(command)
            elif any(w in cmd for w in ["word", "documento", "docx", ".doc"]):
                return self._criar_word_direto(command)
            elif any(w in cmd for w in ["landing page", "pagina de captura", "pagina de vendas"]):
                return self._criar_landing_page(command)
            elif any(w in cmd for w in ["dashboard", "painel", "relatorio web"]):
                return self._criar_dashboard(command)
            elif any(w in cmd for w in ["calculadora", "roi", "simulador"]):
                return self._criar_calculadora(command)
            elif any(w in cmd for w in ["crm", "sistema de clientes", "gestao de leads"]):
                return self._criar_crm(command)
            else:
                return self._criar_app_generico(command)
        except Exception as e:
            log.error(f"VsCodeSkill erro: {e}")
            return SkillResult(success=False, message=f"Erro ao criar: {e}")

    # ================================================================
    # FLUXO PLANEJADO (chamado pela GUI após coletar perguntas)
    # ================================================================

    def _executar_plano(self, p: dict) -> SkillResult:
        """Executa criação com base no plano aprovado pelo usuário."""
        tipo = p.get("tipo", "html")
        descricao = p.get("descricao", "app")
        publico = p.get("publico", "")
        funcionalidades = p.get("funcionalidades", "")
        estilo = p.get("estilo", "profissional")
        extras = p.get("extras", "")

        contexto_completo = (
            f"Tipo: {tipo}\n"
            f"Descricao: {descricao}\n"
            f"Publico alvo: {publico}\n"
            f"Funcionalidades necessarias: {funcionalidades}\n"
            f"Estilo/Tom: {estilo}\n"
            f"Informacoes adicionais: {extras}"
        ).strip()

        tipo_lower = tipo.lower()
        if tipo_lower in ("powerpoint", "pptx", "apresentacao", "apresentação", "slides"):
            return self._criar_powerpoint_planejado(descricao, contexto_completo)
        elif tipo_lower in ("excel", "xlsx", "planilha"):
            return self._criar_excel_planejado(descricao, contexto_completo)
        elif tipo_lower in ("word", "docx", "documento"):
            return self._criar_word_planejado(descricao, contexto_completo)
        elif tipo_lower in ("landing", "landing_page", "pagina de captura"):
            return self._criar_landing_page(f"crie landing page {descricao}")
        elif tipo_lower in ("dashboard", "painel"):
            return self._criar_dashboard(f"crie dashboard {descricao}")
        elif tipo_lower in ("crm",):
            return self._criar_crm(f"crie crm {descricao}")
        else:
            return self._criar_app_html_planejado(descricao, contexto_completo)

    # ================================================================
    # POWERPOINT
    # ================================================================

    def _criar_powerpoint_planejado(self, descricao: str, contexto: str) -> SkillResult:
        """Cria apresentação PowerPoint real usando python-pptx com conteúdo da IA."""
        APPS_DIR.mkdir(parents=True, exist_ok=True)
        nome = f"apresentacao_{descricao.replace(' ', '_')[:30]}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        pasta = APPS_DIR / nome
        pasta.mkdir(parents=True, exist_ok=True)

        # Gera estrutura da apresentação com IA
        prompt = f"""Voce e um especialista em apresentacoes de negocios.
Com base nestas informacoes:
{contexto}

Crie o roteiro completo de uma apresentacao profissional em formato JSON:
{{
  "titulo": "Titulo da apresentacao",
  "subtitulo": "Subtitulo ou tagline",
  "slides": [
    {{
      "titulo": "Titulo do slide",
      "tipo": "capa|conteudo|lista|dados|conclusao",
      "pontos": ["ponto 1", "ponto 2", "ponto 3"],
      "nota": "nota do apresentador (opcional)"
    }}
  ]
}}

REGRAS:
- Minimo 8 slides, maximo 15
- Dados e numeros ESPECIFICOS e REAIS (nao genericos)
- Conteudo ESPECIFICO para o contexto descrito, nao templates vazios
- Use linguagem assertiva e profissional
- Slides de dados: inclua numeros, percentuais, metricas reais do mercado
Retorne APENAS o JSON, sem explicacoes."""

        estrutura = None
        try:
            from src.core.ai_engine import get_engine
            engine = get_engine()
            resp = engine.chat_with_fallback(prompt)
            # Extrai JSON da resposta
            if "{" in resp:
                inicio = resp.find("{")
                fim = resp.rfind("}") + 1
                estrutura = json.loads(resp[inicio:fim])
        except Exception as e:
            log.warning(f"IA nao gerou estrutura: {e}")

        # Fallback de estrutura
        if not estrutura:
            estrutura = {
                "titulo": descricao.title(),
                "subtitulo": "Apresentacao Profissional",
                "slides": [
                    {"titulo": "Introducao", "tipo": "capa", "pontos": [descricao], "nota": ""},
                    {"titulo": "Contexto", "tipo": "conteudo", "pontos": ["Ponto 1", "Ponto 2", "Ponto 3"], "nota": ""},
                    {"titulo": "Solucao", "tipo": "lista", "pontos": ["Item A", "Item B", "Item C"], "nota": ""},
                    {"titulo": "Beneficios", "tipo": "lista", "pontos": ["Beneficio 1", "Beneficio 2", "Beneficio 3"], "nota": ""},
                    {"titulo": "Proximos Passos", "tipo": "conclusao", "pontos": ["Acao 1", "Acao 2", "Contato"], "nota": ""},
                ]
            }

        # Cria o arquivo .pptx
        arquivo_pptx = pasta / f"{nome}.pptx"
        try:
            self._montar_pptx(arquivo_pptx, estrutura)
        except ImportError:
            # Instala python-pptx
            log.info("Instalando python-pptx...")
            subprocess.run(["py", "-3", "-m", "pip", "install", "python-pptx", "-q"],
                           capture_output=True, timeout=60)
            try:
                self._montar_pptx(arquivo_pptx, estrutura)
            except Exception as e2:
                return SkillResult(success=False, message=f"Erro ao criar PowerPoint: {e2}")
        except Exception as e:
            return SkillResult(success=False, message=f"Erro ao montar PPTX: {e}")

        # Abre o arquivo
        try:
            os.startfile(str(arquivo_pptx))
        except Exception:
            subprocess.Popen(["start", "", str(arquivo_pptx)], shell=True)

        n_slides = len(estrutura.get("slides", []))
        lista_slides = "\n".join(
            f"  Slide {i+1}: {s.get('titulo', '')}"
            for i, s in enumerate(estrutura.get("slides", []))
        )
        return SkillResult(
            success=True,
            message=(
                f"[POWERPOINT CRIADO] {estrutura.get('titulo', descricao.title())}\n\n"
                f"ARQUIVO: {arquivo_pptx}\n"
                f"SLIDES: {n_slides} slides criados com conteudo real da IA\n"
                f"STATUS: Aberto no PowerPoint\n\n"
                f"CONTEUDO:\n{lista_slides}\n\n"
                f"Pronto para usar, editar e apresentar!"
            ),
            data={"arquivo": str(arquivo_pptx), "slides": n_slides}
        )

    def _montar_pptx(self, arquivo: Path, estrutura: dict):
        """Monta o arquivo .pptx usando python-pptx."""
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN

        prs = Presentation()
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)

        AZUL       = RGBColor(0x1E, 0x3A, 0x8A)
        AZUL_CLARO = RGBColor(0x3B, 0x82, 0xF6)
        BRANCO     = RGBColor(0xFF, 0xFF, 0xFF)
        CINZA      = RGBColor(0x64, 0x74, 0x8B)
        ESCURO     = RGBColor(0x0F, 0x17, 0x2A)
        ESCURO2    = RGBColor(0x16, 0x19, 0x21)

        def add_bg(slide, cor):
            bg = slide.background
            fill = bg.fill
            fill.solid()
            fill.fore_color.rgb = cor

        def add_box(slide, text, left, top, width, height,
                    bold=False, size=24, color=BRANCO, align=PP_ALIGN.LEFT):
            txBox = slide.shapes.add_textbox(
                Inches(left), Inches(top), Inches(width), Inches(height)
            )
            tf = txBox.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = align
            run = p.add_run()
            run.text = text
            run.font.bold = bold
            run.font.size = Pt(size)
            run.font.color.rgb = color
            return txBox

        slides_data = estrutura.get("slides", [])

        for i, slide_info in enumerate(slides_data):
            tipo = slide_info.get("tipo", "conteudo")
            titulo_slide = slide_info.get("titulo", f"Slide {i+1}")
            pontos = slide_info.get("pontos", [])

            layout = prs.slide_layouts[6]  # blank
            slide = prs.slides.add_slide(layout)

            if tipo == "capa" or i == 0:
                add_bg(slide, ESCURO)
                # Linha destaque
                linha = slide.shapes.add_shape(1, Inches(0), Inches(3.2), Inches(13.33), Pt(3))
                linha.fill.solid()
                linha.fill.fore_color.rgb = AZUL_CLARO
                linha.line.fill.background()
                add_box(slide, estrutura.get("titulo", titulo_slide),
                        0.8, 1.2, 11, 1.8, bold=True, size=44, color=BRANCO)
                add_box(slide, estrutura.get("subtitulo", ""),
                        0.8, 3.4, 9, 0.8, size=24, color=AZUL_CLARO)
                add_box(slide, f"Slide {i+1} de {len(slides_data)}",
                        10, 6.8, 3, 0.5, size=12, color=CINZA, align=PP_ALIGN.RIGHT)
            else:
                bg_cor = ESCURO if i % 2 == 0 else ESCURO2
                add_bg(slide, bg_cor)
                # Barra superior
                barra = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(1.1))
                barra.fill.solid()
                barra.fill.fore_color.rgb = AZUL
                barra.line.fill.background()
                add_box(slide, titulo_slide, 0.4, 0.12, 12, 0.85, bold=True, size=26, color=BRANCO)
                add_box(slide, f"{i+1:02d}", 11.8, 0.12, 1.2, 0.85, bold=True, size=28,
                        color=AZUL_CLARO, align=PP_ALIGN.RIGHT)

                y = 1.4
                for j, ponto in enumerate(pontos[:6]):
                    # Marcador
                    marc = slide.shapes.add_shape(1, Inches(0.5), Inches(y + 0.12), Inches(0.08), Inches(0.08))
                    marc.fill.solid()
                    marc.fill.fore_color.rgb = AZUL_CLARO
                    marc.line.fill.background()
                    add_box(slide, ponto, 0.8, y, 11.8, 0.75, bold=(j == 0), size=20, color=BRANCO)
                    y += 0.9

                nota = slide_info.get("nota", "")
                if nota:
                    slide.notes_slide.notes_text_frame.text = nota

        prs.save(str(arquivo))
        log.info(f"PowerPoint salvo: {arquivo}")

    def _criar_powerpoint_direto(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        return self._criar_powerpoint_planejado(desc, f"Descricao: {desc}\nEstilo: profissional")

    # ================================================================
    # EXCEL / PLANILHA
    # ================================================================

    def _criar_excel_planejado(self, descricao: str, contexto: str) -> SkillResult:
        """Cria planilha Excel com dados gerados pela IA."""
        APPS_DIR.mkdir(parents=True, exist_ok=True)
        nome = f"planilha_{descricao.replace(' ', '_')[:30]}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        pasta = APPS_DIR / nome
        pasta.mkdir(parents=True, exist_ok=True)
        arquivo = pasta / f"{nome}.xlsx"

        prompt = f"""Voce e um especialista em planilhas Excel de negocios.
Com base nestas informacoes:
{contexto}

Crie a estrutura de uma planilha em formato JSON:
{{
  "nome_arquivo": "nome",
  "abas": [
    {{
      "nome": "Nome da aba",
      "colunas": ["Coluna A", "Coluna B", "Coluna C"],
      "linhas_exemplo": [
        ["valor1", "valor2", "valor3"]
      ]
    }}
  ]
}}

REGRAS:
- Minimo 2 abas, maximo 5
- Dados de exemplo REALISTAS e ESPECIFICOS para o contexto
- Numeros, datas, percentuais, moedas conforme adequado
- Pelo menos 10 linhas de exemplo por aba
Retorne APENAS o JSON, sem explicacoes."""

        estrutura = None
        try:
            from src.core.ai_engine import get_engine
            engine = get_engine()
            resp = engine.chat_with_fallback(prompt)
            if "{" in resp:
                inicio = resp.find("{")
                fim = resp.rfind("}") + 1
                estrutura = json.loads(resp[inicio:fim])
        except Exception as e:
            log.warning(f"IA nao gerou estrutura Excel: {e}")

        if not estrutura:
            estrutura = {
                "nome_arquivo": descricao,
                "abas": [{
                    "nome": "Dados",
                    "colunas": ["Item", "Quantidade", "Valor Unit (R$)", "Total (R$)"],
                    "linhas_exemplo": [
                        [f"Item {i}", str(i * 2), f"{i * 50:.2f}", f"{i * 100:.2f}"]
                        for i in range(1, 11)
                    ]
                }]
            }

        try:
            self._montar_xlsx(arquivo, estrutura)
        except ImportError:
            log.info("Instalando openpyxl...")
            subprocess.run(["py", "-3", "-m", "pip", "install", "openpyxl", "-q"],
                           capture_output=True, timeout=60)
            try:
                self._montar_xlsx(arquivo, estrutura)
            except Exception as e2:
                return SkillResult(success=False, message=f"Erro ao criar Excel: {e2}")
        except Exception as e:
            return SkillResult(success=False, message=f"Erro ao montar Excel: {e}")

        try:
            os.startfile(str(arquivo))
        except Exception:
            subprocess.Popen(["start", "", str(arquivo)], shell=True)

        n_abas = len(estrutura.get("abas", []))
        nomes_abas = ", ".join(a.get("nome", "") for a in estrutura.get("abas", []))
        return SkillResult(
            success=True,
            message=(
                f"[PLANILHA CRIADA] {descricao.title()}\n\n"
                f"ARQUIVO: {arquivo}\n"
                f"ABAS: {n_abas} | {nomes_abas}\n"
                f"STATUS: Aberto no Excel\n\n"
                f"Planilha com dados reais criada pela IA!"
            ),
            data={"arquivo": str(arquivo)}
        )

    def _montar_xlsx(self, arquivo: Path, estrutura: dict):
        """Monta o arquivo .xlsx usando openpyxl."""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        wb = Workbook()
        wb.remove(wb.active)

        h_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        alt_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        h_font = Font(bold=True, color="FFFFFF", size=11)
        t_font = Font(bold=True, color="3B82F6", size=13)
        thin = Side(border_style="thin", color="CBD5E1")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        for aba_data in estrutura.get("abas", []):
            nome_aba = str(aba_data.get("nome", "Dados"))[:31]
            ws = wb.create_sheet(title=nome_aba)
            colunas = aba_data.get("colunas", [])
            linhas = aba_data.get("linhas_exemplo", [])

            # Título
            ws.merge_cells(f"A1:{get_column_letter(max(len(colunas), 1))}1")
            ws["A1"] = aba_data.get("nome", "Dados")
            ws["A1"].font = t_font
            ws["A1"].alignment = Alignment(horizontal="center")
            ws.row_dimensions[1].height = 28

            # Headers
            for ci, col in enumerate(colunas, 1):
                cell = ws.cell(row=2, column=ci, value=col)
                cell.font = h_font
                cell.fill = h_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = border
                ws.column_dimensions[get_column_letter(ci)].width = max(15, len(str(col)) + 4)
            ws.row_dimensions[2].height = 22

            # Dados
            for ri, linha in enumerate(linhas, 3):
                fill = alt_fill if ri % 2 == 0 else None
                for ci, valor in enumerate(linha[:len(colunas)], 1):
                    cell = ws.cell(row=ri, column=ci, value=valor)
                    cell.border = border
                    cell.alignment = Alignment(vertical="center")
                    if fill:
                        cell.fill = fill

            ws.freeze_panes = "A3"

        wb.save(str(arquivo))
        log.info(f"Excel salvo: {arquivo}")

    def _criar_excel_direto(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        return self._criar_excel_planejado(desc, f"Descricao: {desc}")

    # ================================================================
    # WORD / DOCUMENTO
    # ================================================================

    def _criar_word_planejado(self, descricao: str, contexto: str) -> SkillResult:
        """Cria documento Word com conteúdo gerado pela IA."""
        APPS_DIR.mkdir(parents=True, exist_ok=True)
        nome = f"doc_{descricao.replace(' ', '_')[:30]}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        pasta = APPS_DIR / nome
        pasta.mkdir(parents=True, exist_ok=True)
        arquivo = pasta / f"{nome}.docx"

        prompt = f"""Voce e um redator profissional de documentos de negocios.
Com base nestas informacoes:
{contexto}

Escreva o documento completo em formato JSON:
{{
  "titulo": "Titulo do documento",
  "secoes": [
    {{
      "titulo": "Titulo da secao",
      "tipo": "normal|lista|destaque",
      "conteudo": "texto completo da secao; para lista use itens separados por |"
    }}
  ]
}}

REGRAS:
- Minimo 5 secoes bem desenvolvidas
- Conteudo ESPECIFICO, detalhado e profissional
- Dados, numeros e exemplos REAIS para o contexto
Retorne APENAS o JSON, sem explicacoes."""

        estrutura = None
        try:
            from src.core.ai_engine import get_engine
            engine = get_engine()
            resp = engine.chat_with_fallback(prompt)
            if "{" in resp:
                inicio = resp.find("{")
                fim = resp.rfind("}") + 1
                estrutura = json.loads(resp[inicio:fim])
        except Exception as e:
            log.warning(f"IA nao gerou estrutura Word: {e}")

        if not estrutura:
            estrutura = {
                "titulo": descricao.title(),
                "secoes": [
                    {"titulo": "Introducao", "tipo": "normal",
                     "conteudo": f"Este documento descreve {descricao}."},
                    {"titulo": "Objetivos", "tipo": "lista",
                     "conteudo": "Objetivo 1|Objetivo 2|Objetivo 3"},
                    {"titulo": "Desenvolvimento", "tipo": "normal",
                     "conteudo": "Conteudo principal do documento."},
                    {"titulo": "Conclusao", "tipo": "destaque",
                     "conteudo": "Conclusoes e proximos passos."},
                ]
            }

        try:
            self._montar_docx(arquivo, estrutura)
        except ImportError:
            log.info("Instalando python-docx...")
            subprocess.run(["py", "-3", "-m", "pip", "install", "python-docx", "-q"],
                           capture_output=True, timeout=60)
            try:
                self._montar_docx(arquivo, estrutura)
            except Exception as e2:
                return SkillResult(success=False, message=f"Erro ao criar Word: {e2}")
        except Exception as e:
            return SkillResult(success=False, message=f"Erro ao montar DOCX: {e}")

        try:
            os.startfile(str(arquivo))
        except Exception:
            subprocess.Popen(["start", "", str(arquivo)], shell=True)

        n_secoes = len(estrutura.get("secoes", []))
        return SkillResult(
            success=True,
            message=(
                f"[DOCUMENTO CRIADO] {estrutura.get('titulo', descricao.title())}\n\n"
                f"ARQUIVO: {arquivo}\n"
                f"SECOES: {n_secoes} secoes com conteudo real\n"
                f"STATUS: Aberto no Word\n\n"
                f"Documento profissional criado pela IA!"
            ),
            data={"arquivo": str(arquivo)}
        )

    def _montar_docx(self, arquivo: Path, estrutura: dict):
        """Monta o arquivo .docx usando python-docx."""
        from docx import Document
        from docx.shared import Pt, RGBColor, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement

        doc = Document()
        for section in doc.sections:
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.5)
            section.left_margin = Cm(3)
            section.right_margin = Cm(2)

        # Título
        titulo_para = doc.add_heading(estrutura.get("titulo", "Documento"), level=0)
        titulo_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in titulo_para.runs:
            run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

        doc.add_paragraph()
        data_para = doc.add_paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
        data_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for run in data_para.runs:
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        doc.add_paragraph()

        for secao in estrutura.get("secoes", []):
            titulo_sec = secao.get("titulo", "")
            tipo = secao.get("tipo", "normal")
            conteudo = secao.get("conteudo", "")

            h = doc.add_heading(titulo_sec, level=1)
            for run in h.runs:
                run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

            if tipo == "lista":
                itens = [x.strip() for x in conteudo.split("|") if x.strip()]
                for item in itens:
                    p = doc.add_paragraph(item, style="List Bullet")
                    for run in p.runs:
                        run.font.size = Pt(11)
            elif tipo == "destaque":
                p = doc.add_paragraph()
                run = p.add_run(conteudo)
                run.bold = True
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
                pPr = p._element.get_or_add_pPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "EFF6FF")
                pPr.append(shd)
            else:
                p = doc.add_paragraph(conteudo)
                for run in p.runs:
                    run.font.size = Pt(11)

            doc.add_paragraph()

        doc.save(str(arquivo))
        log.info(f"Word salvo: {arquivo}")

    def _criar_word_direto(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        return self._criar_word_planejado(desc, f"Descricao: {desc}")

    # ================================================================
    # HTML / WEB APPS
    # ================================================================

    def _extrair_descricao(self, command: str) -> str:
        palavras_remover = {
            "crie", "cria", "faca", "desenvolva", "programe",
            "um", "uma", "app", "site", "sistema", "ferramenta",
            "de", "para", "do", "da", "aplicativo", "apresentacao",
            "powerpoint", "planilha", "excel", "documento", "word"
        }
        palavras = command.lower().split()
        desc = " ".join(w for w in palavras if w not in palavras_remover)
        return desc.strip() or "ferramenta"

    def _abrir_vscode(self, pasta: Path) -> bool:
        try:
            subprocess.Popen(["code", str(pasta)], shell=True)
            return True
        except Exception:
            try:
                subprocess.Popen(f'code "{pasta}"', shell=True)
                return True
            except Exception:
                return False

    def _criar_app_html_planejado(self, descricao: str, contexto: str) -> SkillResult:
        """Cria app HTML com IA, usando contexto completo do planejamento."""
        nome_projeto = f"app_{descricao.replace(' ', '_')[:30]}_{datetime.now().strftime('%H%M')}"
        pasta = APPS_DIR / nome_projeto
        pasta.mkdir(parents=True, exist_ok=True)

        prompt = (
            "Voce e um desenvolvedor front-end expert em HTML, CSS e JavaScript.\n"
            f"Com base nestas informacoes:\n{contexto}\n\n"
            "Crie um app web COMPLETO, BONITO e FUNCIONAL.\n\n"
            "REQUISITOS OBRIGATORIOS:\n"
            "1. Design moderno dark theme (#0f1117, cards #161921, accent #3b82f6)\n"
            "2. Totalmente funcional com JavaScript puro (sem frameworks externos)\n"
            "3. Responsivo (mobile-first)\n"
            "4. Interface REAL com funcionalidades especificas para este contexto\n"
            "5. Pelo menos 3 secoes ou funcionalidades distintas\n"
            "6. Dados de exemplo ESPECIFICOS (nao genericos)\n"
            "7. localStorage para persistencia\n\n"
            "Retorne APENAS o codigo HTML completo (doctype ate /html), sem explicacoes."
        )

        html_gerado = ""
        try:
            from src.core.ai_engine import get_engine
            engine = get_engine()
            resposta = engine.chat_with_fallback(prompt)
            if resposta and "<!DOCTYPE" in resposta.upper():
                inicio = resposta.upper().find("<!DOCTYPE")
                fim = resposta.rfind("</html>")
                if fim > inicio:
                    html_gerado = resposta[inicio:fim + 7]
        except Exception as e:
            log.warning(f"IA nao disponivel: {e}")

        if not html_gerado or len(html_gerado) < 200:
            html_gerado = self._html_fallback(descricao)

        (pasta / "index.html").write_text(html_gerado, encoding="utf-8")
        (pasta / "README.md").write_text(
            f"# {descricao.title()}\nCriado por William v6 com IA\n\nAbra index.html no navegador.",
            encoding="utf-8"
        )
        self._abrir_vscode(pasta)
        try:
            import webbrowser
            webbrowser.open(str(pasta / "index.html"))
        except Exception:
            pass

        return SkillResult(
            success=True,
            message=(
                f"[APP CRIADO] {descricao.title()}\n\n"
                f"PASTA: {pasta}\n"
                f"STATUS: Aberto no VS Code e navegador\n"
                f"TIPO: App web HTML/JS funcional\n\n"
                f"Personalize o codigo no VS Code conforme precisar."
            ),
            data={"pasta": str(pasta)}
        )

    def _criar_landing_page(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        nome_projeto = f"landing_{desc.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        pasta = APPS_DIR / nome_projeto
        pasta.mkdir(parents=True, exist_ok=True)

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{desc.title()} - Solucao Profissional</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #f1f5f9; }}
        .hero {{ min-height: 100vh; display: flex; align-items: center; justify-content: center;
                 background: linear-gradient(135deg, #1e3a5f 0%, #0f1117 100%); text-align: center; padding: 40px; }}
        .hero h1 {{ font-size: 3rem; font-weight: 700; color: #3b82f6; margin-bottom: 20px; }}
        .hero p {{ font-size: 1.3rem; color: #94a3b8; max-width: 600px; margin: 0 auto 40px; }}
        .cta-btn {{ background: #3b82f6; color: white; padding: 18px 40px; border: none;
                   border-radius: 8px; font-size: 1.1rem; cursor: pointer; font-weight: 600; }}
        .form-section {{ background: #161921; padding: 60px 20px; text-align: center; }}
        .form {{ max-width: 500px; margin: 0 auto; }}
        .form input {{ width: 100%; padding: 14px; margin: 10px 0; border-radius: 6px;
                       border: 1px solid #2d3748; background: #1c1f2b; color: #f1f5f9; }}
        .form button {{ width: 100%; padding: 16px; background: #22c55e; color: white;
                       border: none; border-radius: 6px; font-size: 1.1rem; font-weight: 600; cursor: pointer; }}
        .benefits {{ background: #0f1117; padding: 60px 20px; }}
        .benefits-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                          gap: 30px; max-width: 1000px; margin: 0 auto; }}
        .benefit {{ background: #161921; padding: 30px; border-radius: 10px; }}
        .benefit h3 {{ color: #3b82f6; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <section class="hero">
        <div>
            <h1>Solucao Profissional para {desc.title()}</h1>
            <p>Automatize, escale e gere mais resultado. Sem complicacao.</p>
            <button class="cta-btn" onclick="document.querySelector('.form-section').scrollIntoView()">
                Quero Comecar Agora
            </button>
        </div>
    </section>
    <section class="form-section">
        <h2>Receba Consultoria Gratuita</h2>
        <form class="form" id="leadForm">
            <input type="text" placeholder="Seu nome completo" required>
            <input type="tel" placeholder="WhatsApp (com DDD)" required>
            <input type="email" placeholder="Seu melhor email" required>
            <button type="submit">QUERO COMECAR AGORA</button>
        </form>
    </section>
    <section class="benefits">
        <div class="benefits-grid">
            <div class="benefit"><h3>Resultado Rapido</h3><p>Primeiros resultados em 30 dias.</p></div>
            <div class="benefit"><h3>Sem Complicacao</h3><p>Cuidamos de tudo para voce.</p></div>
            <div class="benefit"><h3>Suporte Continuo</h3><p>Equipe via WhatsApp sempre disponivel.</p></div>
        </div>
    </section>
    <script>
        document.getElementById('leadForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            alert('Obrigado! Entraremos em contato em breve!');
        }});
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
        return SkillResult(success=True,
                           message=f"[LANDING PAGE] {desc.title()}\nArquivo: {pasta}/index.html\nAberta no navegador!",
                           data={"pasta": str(pasta)})

    def _criar_dashboard(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        pasta = APPS_DIR / f"dashboard_{desc.replace(' ', '_')}"
        pasta.mkdir(parents=True, exist_ok=True)
        html = (
            f"<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'>"
            f"<title>Dashboard {desc.title()}</title>"
            f"<style>body{{font-family:'Segoe UI',sans-serif;background:#0f1117;color:#f1f5f9;margin:0}}"
            f".header{{background:#161921;padding:20px 30px}}.header h1{{color:#3b82f6}}"
            f".kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;padding:30px}}"
            f".kpi{{background:#161921;padding:25px;border-radius:10px;text-align:center}}"
            f".kpi .v{{font-size:2.5rem;font-weight:700;color:#3b82f6}}"
            f".kpi .l{{color:#94a3b8}}.kpi .d{{color:#22c55e}}"
            f".table-wrap{{margin:0 30px 30px;background:#161921;border-radius:10px;overflow:hidden}}"
            f"table{{width:100%;border-collapse:collapse}}th{{background:#1c1f2b;padding:15px;text-align:left;color:#94a3b8}}"
            f"td{{padding:15px;border-top:1px solid #2d3748}}</style></head><body>"
            f"<div class='header'><h1>Dashboard {desc.title()}</h1></div>"
            f"<div class='kpis'>"
            f"<div class='kpi'><div class='v'>47</div><div class='l'>Total Leads</div><div class='d'>+12 hoje</div></div>"
            f"<div class='kpi'><div class='v'>8.3%</div><div class='l'>Conversao</div><div class='d'>+1.2%</div></div>"
            f"<div class='kpi'><div class='v'>R$6.2k</div><div class='l'>Receita</div><div class='d'>+R$800</div></div>"
            f"<div class='kpi'><div class='v'>4</div><div class='l'>Clientes</div><div class='d'>+1 mes</div></div>"
            f"</div><div class='table-wrap'><table>"
            f"<tr><th>Lead</th><th>Empresa</th><th>Score</th><th>Status</th></tr>"
            f"<tr><td>Ana Costa</td><td>Clinica Sorrir</td><td>95</td><td style='color:#22c55e'>HOT</td></tr>"
            f"<tr><td>Carlos Lima</td><td>Odonto Premium</td><td>82</td><td style='color:#22c55e'>HOT</td></tr>"
            f"<tr><td>Maria Santos</td><td>DentMax</td><td>67</td><td style='color:#f59e0b'>WARM</td></tr>"
            f"</table></div></body></html>"
        )
        (pasta / "index.html").write_text(html, encoding="utf-8")
        self._abrir_vscode(pasta)
        try:
            import webbrowser
            webbrowser.open(str(pasta / "index.html"))
        except Exception:
            pass
        return SkillResult(success=True,
                           message=f"[DASHBOARD] {desc.title()}\nArquivo: {pasta}/index.html",
                           data={"pasta": str(pasta)})

    def _criar_calculadora(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        pasta = APPS_DIR / f"calculadora_{desc.replace(' ', '_')}"
        pasta.mkdir(parents=True, exist_ok=True)
        html = """<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'><title>Calculadora ROI</title>
<style>body{font-family:'Segoe UI',sans-serif;background:#0f1117;color:#f1f5f9;display:flex;align-items:center;justify-content:center;min-height:100vh}
.card{background:#161921;padding:40px;border-radius:15px;width:500px;border:1px solid #2d3748}
h1{color:#3b82f6;margin-bottom:30px;text-align:center}label{display:block;margin:15px 0 5px;color:#94a3b8}
input{width:100%;padding:12px;border-radius:6px;border:1px solid #2d3748;background:#1c1f2b;color:#f1f5f9;font-size:1rem;box-sizing:border-box}
button{width:100%;padding:14px;background:#3b82f6;color:white;border:none;border-radius:6px;font-size:1rem;font-weight:600;cursor:pointer;margin-top:20px}
.res{margin-top:20px;padding:20px;background:#1c1f2b;border-radius:8px;display:none}
.res .v{font-size:2rem;color:#22c55e;font-weight:700}
</style></head><body><div class='card'>
<h1>Calculadora de ROI</h1>
<label>Investimento Mensal (R$)</label><input type='number' id='inv' value='1500'>
<label>Clientes por Mes</label><input type='number' id='cli' value='5'>
<label>Ticket Medio (R$)</label><input type='number' id='tick' value='2000'>
<label>Meses de Retencao</label><input type='number' id='ret' value='6'>
<button onclick='calc()'>CALCULAR ROI</button>
<div class='res' id='res'>
<p>Receita Total:</p><div class='v' id='rec'></div>
<p style='margin-top:10px'>ROI: <span id='roi' style='color:#3b82f6;font-weight:700'></span></p>
<p>Lucro: <span id='luc' style='color:#22c55e;font-weight:700'></span></p>
</div></div>
<script>
function calc(){
var inv=+document.getElementById('inv').value,cli=+document.getElementById('cli').value,
tick=+document.getElementById('tick').value,ret=+document.getElementById('ret').value;
var rec=cli*tick*ret,roi=((rec-inv)/inv*100).toFixed(0),luc=rec-inv;
document.getElementById('rec').textContent='R$'+rec.toLocaleString('pt-BR');
document.getElementById('roi').textContent=roi+'%';
document.getElementById('luc').textContent='R$'+luc.toLocaleString('pt-BR');
document.getElementById('res').style.display='block';
}
</script></body></html>"""
        (pasta / "index.html").write_text(html, encoding="utf-8")
        self._abrir_vscode(pasta)
        try:
            import webbrowser
            webbrowser.open(str(pasta / "index.html"))
        except Exception:
            pass
        return SkillResult(success=True,
                           message=f"[CALCULADORA ROI] Aberta!\nArquivo: {pasta}/index.html",
                           data={"pasta": str(pasta)})

    def _criar_crm(self, command: str) -> SkillResult:
        desc = self._extrair_descricao(command)
        pasta = APPS_DIR / f"crm_{desc.replace(' ', '_')}"
        pasta.mkdir(parents=True, exist_ok=True)
        key = desc.replace(" ", "_")
        html = f"""<!DOCTYPE html><html lang='pt-BR'><head><meta charset='UTF-8'><title>CRM {desc.title()}</title>
<style>body{{font-family:'Segoe UI',sans-serif;background:#0f1117;color:#f1f5f9;margin:0}}
.header{{background:#161921;padding:20px 30px}}.header h1{{color:#3b82f6}}
.form{{background:#161921;margin:20px;padding:20px;border-radius:10px}}
.fr{{display:flex;gap:10px;flex-wrap:wrap}}
input{{padding:10px;border-radius:5px;border:1px solid #2d3748;background:#1c1f2b;color:#f1f5f9;flex:1;min-width:120px}}
button{{padding:10px 20px;background:#3b82f6;color:white;border:none;border-radius:5px;cursor:pointer;font-weight:600}}
.table-wrap{{margin:20px;background:#161921;border-radius:10px;overflow:hidden}}
table{{width:100%;border-collapse:collapse}}th{{background:#1c1f2b;padding:12px;text-align:left;color:#94a3b8}}
td{{padding:12px;border-top:1px solid #2d3748}}
</style></head><body>
<div class='header'><h1 id='tit'>CRM - 0 Leads</h1></div>
<div class='form'><div class='fr'>
<input id='n' placeholder='Nome *'><input id='emp' placeholder='Empresa'>
<input id='tel' placeholder='WhatsApp'><input id='email' placeholder='Email'>
<button onclick='add()'>+ Adicionar</button>
</div></div>
<div class='table-wrap'><table>
<thead><tr><th>Nome</th><th>Empresa</th><th>Telefone</th><th>Email</th><th>Data</th><th>Acao</th></tr></thead>
<tbody id='tb'></tbody></table></div>
<script>
var K='crm_{key}';
function load(){{return JSON.parse(localStorage.getItem(K)||'[]')}}
function save(d){{localStorage.setItem(K,JSON.stringify(d));render()}}
function add(){{
var n=document.getElementById('n').value.trim();
if(!n){{alert('Informe o nome!');return;}}
var d=load();
d.push({{id:Date.now(),nome:n,emp:document.getElementById('emp').value,
tel:document.getElementById('tel').value,email:document.getElementById('email').value,
data:new Date().toLocaleDateString('pt-BR')}});
save(d);['n','emp','tel','email'].forEach(function(id){{document.getElementById(id).value=''}});
}}
function del(id){{save(load().filter(function(x){{return x.id!==id}}))}}
function render(){{
var d=load();
document.getElementById('tit').textContent='CRM - '+d.length+' Leads';
document.getElementById('tb').innerHTML=d.map(function(x){{
return '<tr><td>'+x.nome+'</td><td>'+(x.emp||'-')+'</td><td>'+(x.tel||'-')+'</td><td>'+(x.email||'-')+'</td><td>'+x.data+'</td><td><button onclick="del('+x.id+')" style="background:#ef4444;padding:4px 10px">x</button></td></tr>';
}}).join('');
}}
render();
</script></body></html>"""
        (pasta / "index.html").write_text(html, encoding="utf-8")
        self._abrir_vscode(pasta)
        try:
            import webbrowser
            webbrowser.open(str(pasta / "index.html"))
        except Exception:
            pass
        return SkillResult(success=True,
                           message=f"[CRM] {desc.title()}\nArquivo: {pasta}/index.html",
                           data={"pasta": str(pasta)})

    def _criar_app_generico(self, command: str) -> SkillResult:
        """Cria app genérico com IA."""
        desc = self._extrair_descricao(command)
        return self._criar_app_html_planejado(
            desc,
            f"Descricao: {desc}\nTipo: app web geral\nEstilo: moderno profissional"
        )

    def _html_fallback(self, desc: str) -> str:
        key = desc.replace(" ", "_")
        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8"><title>{desc.title()}</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Segoe UI',sans-serif;background:#0f1117;color:#f1f5f9}}
        .header{{background:#161921;padding:20px 30px;border-bottom:1px solid #2d3748}}
        .header h1{{color:#3b82f6}}
        .container{{max-width:900px;margin:30px auto;padding:0 20px}}
        .kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:25px}}
        .kpi{{background:#161921;border:1px solid #2d3748;border-radius:10px;padding:20px;text-align:center}}
        .kpi .valor{{font-size:2rem;font-weight:700;color:#3b82f6}}
        .kpi .label{{color:#94a3b8;font-size:0.85rem}}
        .card{{background:#161921;border:1px solid #2d3748;border-radius:10px;padding:25px;margin-bottom:20px}}
        .card h2{{color:#f1f5f9;margin-bottom:15px}}
        .fr{{display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap}}
        input,select{{flex:1;padding:10px 14px;background:#1c1f2b;border:1px solid #2d3748;border-radius:6px;color:#f1f5f9;min-width:150px}}
        button{{padding:10px 20px;background:#3b82f6;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:600}}
        button:hover{{background:#2563eb}}
        .btn-red{{background:#ef4444}}
        table{{width:100%;border-collapse:collapse}}
        th{{background:#1c1f2b;padding:12px;text-align:left;color:#94a3b8}}
        td{{padding:12px;border-top:1px solid #2d3748}}
        .tag{{padding:3px 10px;border-radius:20px;font-size:0.8rem;font-weight:600}}
        .tag-g{{background:#14532d;color:#22c55e}}
        .tag-y{{background:#451a03;color:#f59e0b}}
        .tag-b{{background:#1e3a5f;color:#3b82f6}}
    </style>
</head>
<body>
    <div class="header"><h1>⚡ {desc.title()}</h1></div>
    <div class="container">
        <div class="kpis">
            <div class="kpi"><div class="valor" id="k1">0</div><div class="label">Total</div></div>
            <div class="kpi"><div class="valor" id="k2">0</div><div class="label">Ativos</div></div>
            <div class="kpi"><div class="valor" id="k3">0%</div><div class="label">Conclusao</div></div>
        </div>
        <div class="card">
            <h2>Adicionar Item</h2>
            <div class="fr">
                <input type="text" id="nome" placeholder="Nome *" required>
                <input type="text" id="detalhe" placeholder="Detalhe">
                <select id="status">
                    <option value="ativo">Ativo</option>
                    <option value="pendente">Pendente</option>
                    <option value="concluido">Concluido</option>
                </select>
                <button class="btn-green" onclick="adicionar()">+ Adicionar</button>
            </div>
        </div>
        <div class="card">
            <h2>Lista</h2>
            <table>
                <thead><tr><th>Nome</th><th>Detalhe</th><th>Status</th><th>Data</th><th>Acao</th></tr></thead>
                <tbody id="tbody"></tbody>
            </table>
        </div>
    </div>
<script>
var K='{key}';
function carregar(){{return JSON.parse(localStorage.getItem(K)||'[]');}}
function salvar(d){{localStorage.setItem(K,JSON.stringify(d));atualizar();}}
function adicionar(){{
    var nome=document.getElementById('nome').value.trim();
    if(!nome){{alert('Informe o nome!');return;}}
    var dados=carregar();
    dados.push({{id:Date.now(),nome:nome,detalhe:document.getElementById('detalhe').value,
        status:document.getElementById('status').value,data:new Date().toLocaleDateString('pt-BR')}});
    salvar(dados);
    document.getElementById('nome').value='';
    document.getElementById('detalhe').value='';
}}
function remover(id){{salvar(carregar().filter(function(d){{return d.id!==id;}}));}}
function atualizar(){{
    var dados=carregar();
    var tags={{ativo:'tag-g',pendente:'tag-y',concluido:'tag-b'}};
    document.getElementById('tbody').innerHTML=dados.map(function(d){{
        return '<tr><td><strong>'+d.nome+'</strong></td><td style="color:#94a3b8">'+(d.detalhe||'-')+'</td>'
            +'<td><span class="tag '+(tags[d.status]||'tag-b')+'">'+d.status+'</span></td>'
            +'<td style="color:#94a3b8">'+d.data+'</td>'
            +'<td><button class="btn-red" style="padding:5px 12px" onclick="remover('+d.id+')">x</button></td></tr>';
    }}).join('');
    document.getElementById('k1').textContent=dados.length;
    document.getElementById('k2').textContent=dados.filter(function(d){{return d.status==='ativo';}}).length;
    var conc=dados.filter(function(d){{return d.status==='concluido';}}).length;
    document.getElementById('k3').textContent=dados.length?Math.round(conc/dados.length*100)+'%':'0%';
}}
atualizar();
</script>
</body>
</html>"""
