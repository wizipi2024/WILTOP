"""
Calculator Skill - Calculos matematicos.
Wraps funcionalidade de calculos existente.
"""

import re
import math
from typing import Dict, List, Optional
from src.skills.base_skill import BaseSkill, SkillResult


class CalculatorSkill(BaseSkill):
    """Skill de calculadora e conversoes."""

    name = "calculator_skill"
    display_name = "Calculadora"
    description = "Calculos matematicos, conversoes de unidades e expressoes"
    version = "1.0.0"
    category = "general"
    icon = "🧮"
    max_risk_level = "green"

    # Palavras-chave que indicam calculo
    _keywords = [
        "calcul", "quanto e", "quanto da", "quanto faz",
        "some", "subtraia", "multiplique", "divida",
        "raiz", "potencia", "porcentagem", "converta",
        "converter", "metros", "quilos", "celsius",
        "fahrenheit", "km", "milhas",
    ]

    _math_pattern = re.compile(
        r'[\d\s\+\-\*\/\(\)\.\,\^]{3,}'
    )

    def can_handle(self, command: str) -> float:
        """Verifica se e um pedido de calculo."""
        cmd = command.lower()

        # Match direto de keywords
        if any(kw in cmd for kw in self._keywords):
            return 0.8

        # Expressao matematica
        if self._math_pattern.search(command):
            return 0.7

        # Numeros com operadores
        if re.search(r'\d+\s*[\+\-\*\/]\s*\d+', command):
            return 0.9

        return 0.0

    def execute(self, command: str, params: Dict = None, context: Dict = None) -> SkillResult:
        """Executa calculo."""
        try:
            # Tenta extrair expressao matematica
            expr = self._extract_expression(command)
            if expr:
                result = self._safe_eval(expr)
                if result is not None:
                    return SkillResult(
                        success=True,
                        message=f"Resultado: {expr} = {result}",
                        data={"expression": expr, "result": result},
                        actions_taken=["calculate"],
                    )

            # Tenta conversao de unidades
            conversion = self._try_conversion(command)
            if conversion:
                return SkillResult(
                    success=True,
                    message=conversion,
                    data={"type": "conversion"},
                    actions_taken=["convert"],
                )

            return SkillResult(
                success=False,
                message="Nao consegui entender a expressao matematica.",
            )

        except Exception as e:
            return SkillResult(success=False, message=f"Erro no calculo: {str(e)}")

    def _extract_expression(self, command: str) -> Optional[str]:
        """Extrai expressao matematica do comando."""
        # Remove texto nao matematico
        cmd = command.lower()
        cmd = cmd.replace("quanto e", "").replace("quanto da", "")
        cmd = cmd.replace("quanto faz", "").replace("calcule", "")
        cmd = cmd.replace("calcular", "").replace(",", ".")
        cmd = cmd.replace("^", "**").replace("x", "*")
        cmd = cmd.strip()

        # Procura expressao
        match = re.search(r'([\d\s\+\-\*\/\(\)\.\%\*]{3,})', cmd)
        if match:
            return match.group(1).strip()

        return None

    def _safe_eval(self, expr: str):
        """Avalia expressao de forma segura."""
        # Permite apenas caracteres matematicos
        allowed = set("0123456789+-*/().% **")
        if not all(c in allowed or c.isspace() for c in expr):
            return None

        try:
            # Avalia com namespace limitado
            result = eval(expr, {"__builtins__": {}}, {
                "abs": abs, "round": round,
                "sqrt": math.sqrt, "pow": pow,
                "pi": math.pi, "e": math.e,
            })
            if isinstance(result, float):
                result = round(result, 6)
            return result
        except Exception:
            return None

    def _try_conversion(self, command: str) -> Optional[str]:
        """Tenta conversao de unidades."""
        cmd = command.lower()

        # Celsius <-> Fahrenheit
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:graus?\s*)?celsius\s+(?:em|para|to)\s+fahrenheit', cmd)
        if m:
            c = float(m.group(1))
            f = c * 9 / 5 + 32
            return f"{c}°C = {f:.1f}°F"

        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:graus?\s*)?fahrenheit\s+(?:em|para|to)\s+celsius', cmd)
        if m:
            f = float(m.group(1))
            c = (f - 32) * 5 / 9
            return f"{f}°F = {c:.1f}°C"

        # km <-> milhas
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:km|quilometros?)\s+(?:em|para)\s+milhas?', cmd)
        if m:
            km = float(m.group(1))
            mi = km * 0.621371
            return f"{km} km = {mi:.2f} milhas"

        m = re.search(r'(\d+(?:\.\d+)?)\s*milhas?\s+(?:em|para)\s+(?:km|quilometros?)', cmd)
        if m:
            mi = float(m.group(1))
            km = mi * 1.60934
            return f"{mi} milhas = {km:.2f} km"

        # kg <-> libras
        m = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|quilos?)\s+(?:em|para)\s+libras?', cmd)
        if m:
            kg = float(m.group(1))
            lb = kg * 2.20462
            return f"{kg} kg = {lb:.2f} libras"

        return None

    def get_commands(self) -> List[str]:
        return [
            "calcule 15 + 27 * 3",
            "quanto e 100 / 7",
            "converta 30 celsius para fahrenheit",
            "100 km em milhas",
        ]
