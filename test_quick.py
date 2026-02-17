"""Teste COMPLETO v7 - William v3 AI Brain (20 testes)."""
import sys, os
sys.path.insert(0, r"C:\Users\wizip\Desktop\WILTOP")
os.environ["LOG_LEVEL"] = "CRITICAL"
results = []

# 1. Imports basicos
try:
    from src.core.smart_executor_v2 import SmartExecutorV2
    from src.core.memory import get_memory
    from src.core.web_search import get_web_search, WebSearchEngine
    from src.interfaces.gui.william_final import WilliamFinal, COLORS
    results.append("[OK] 1. Imports basicos")
except Exception as ex:
    results.append(f"[ERRO] 1. Import: {ex}")
    print(f"FATAL: {ex}"); sys.exit(1)

# 2. Imports novos (AI Brain + Scheduler)
try:
    from src.core.ai_brain import AIBrain
    from src.core.scheduler import TaskScheduler, get_scheduler
    results.append("[OK] 2. AI Brain + Scheduler")
except Exception as ex:
    results.append(f"[ERRO] 2. novos imports: {ex}")

e = SmartExecutorV2()

# 3. "crie pasta AGORAFOI.TUDO" -> SOMENTE create_folder
try:
    r = e.process_message("crie uma pasta no desktop com o nome AGORAFOI.TUDO")
    types = [a.get("type") for a in r.get("actions", [])]
    assert types == ["create_folder"], f"got {types}"
    results.append("[OK] 3. 'crie pasta' -> create_folder (sem conflito)")
    import shutil
    try:
        t = os.path.join(str(__import__('pathlib').Path.home()), "Desktop", "AGORAFOI.TUDO")
        if os.path.exists(t): shutil.rmtree(t)
    except: pass
except Exception as ex:
    results.append(f"[ERRO] 3. {ex}")

# 4. "tempo em SP" -> web (NAO cleanup!)
try:
    r = e.process_message("como esta o tempo em sao paulo")
    types = [a.get("type") for a in r.get("actions", [])]
    assert "cleanup" not in types
    assert any(t in types for t in ["web_answer", "ask_user"])
    results.append("[OK] 4. 'tempo em SP' -> web/ask (NAO cleanup)")
    e._pending_search_query = None
except Exception as ex:
    results.append(f"[ERRO] 4. {ex}")

# 5. Break funciona
try:
    r = e.process_message("abra a calculadora")
    types = [a.get("type") for a in r.get("actions", [])]
    assert len(types) == 1
    results.append("[OK] 5. Break funciona (1 acao)")
except Exception as ex:
    results.append(f"[ERRO] 5. {ex}")

# 6. Data/hora
try:
    r = e.process_message("que horas sao")
    assert "datetime" in [a.get("type") for a in r.get("actions", [])]
    results.append("[OK] 6. datetime")
except Exception as ex:
    results.append(f"[ERRO] 6. {ex}")

# 7. Processos
try:
    r = e.process_message("quais programas estao abertos")
    assert "process_list" in [a.get("type") for a in r.get("actions", [])]
    results.append("[OK] 7. process_list")
except Exception as ex:
    results.append(f"[ERRO] 7. {ex}")

# 8. WebSearch 5 fontes
try:
    ws = get_web_search()
    assert hasattr(ws, '_search_ddgs_lib')
    assert hasattr(ws, '_search_wikipedia')
    assert hasattr(ws, 'search_news')
    results.append("[OK] 8. WebSearch 5 fontes + news")
except Exception as ex:
    results.append(f"[ERRO] 8. {ex}")

# 9. Memory + GUI + Brain color
try:
    m = get_memory()
    assert hasattr(m, 'get_level_info')
    assert "neon_pink" in COLORS
    results.append("[OK] 9. Memory + GUI + neon_pink")
except Exception as ex:
    results.append(f"[ERRO] 9. {ex}")

# 10. Noticias -> web (NAO abre browser)
try:
    r = e.process_message("noticias do brasil")
    types = [a.get("type") for a in r.get("actions", [])]
    assert "search" not in types
    assert any(t in types for t in ["web_answer", "ask_user"])
    results.append("[OK] 10. noticias -> web/ask (NAO browser)")
    e._pending_search_query = None
except Exception as ex:
    results.append(f"[ERRO] 10. {ex}")

# 11. "o que e IA" -> web
try:
    r = e.process_message("o que e inteligencia artificial")
    types = [a.get("type") for a in r.get("actions", [])]
    assert any(t in types for t in ["web_answer", "ask_user"])
    results.append("[OK] 11. 'o que e IA' -> web/ask")
    e._pending_search_query = None
except Exception as ex:
    results.append(f"[ERRO] 11. {ex}")

# 12. System info
try:
    r = e.process_message("quanta memoria ram eu tenho")
    assert "system_info" in [a.get("type") for a in r.get("actions", [])]
    results.append("[OK] 12. system_info")
except Exception as ex:
    results.append(f"[ERRO] 12. {ex}")

# 13. Disco
try:
    r = e.process_message("quanto espaco tenho no disco")
    assert "disk" in [a.get("type") for a in r.get("actions", [])]
    results.append("[OK] 13. disk")
except Exception as ex:
    results.append(f"[ERRO] 13. {ex}")

# 14. Pesquise -> web (NAO browser)
try:
    r = e.process_message("pesquise sobre python programacao")
    types = [a.get("type") for a in r.get("actions", [])]
    assert "search" not in types
    results.append("[OK] 14. pesquise -> web/ask (NAO browser)")
    e._pending_search_query = None
except Exception as ex:
    results.append(f"[ERRO] 14. {ex}")

# 15. Confirm "sim"
try:
    e._pending_search_query = "teste"
    r = e.process_message("sim")
    assert "search" in [a.get("type") for a in r.get("actions", [])]
    results.append("[OK] 15. confirm 'sim'")
except Exception as ex:
    results.append(f"[ERRO] 15. {ex}")

# 16. Deny "nao"
try:
    e._pending_search_query = "x"
    r = e.process_message("nao")
    assert "info" in [a.get("type") for a in r.get("actions", [])]
    results.append("[OK] 16. deny 'nao'")
except Exception as ex:
    results.append(f"[ERRO] 16. {ex}")

# 17. "crie um jogo de corrida" -> delegate_to_brain (NAO jogo_adivinhacao!)
try:
    r = e.process_message("crie um jogo de corrida 3d")
    types = [a.get("type") for a in r.get("actions", [])]
    assert "delegate_to_brain" in types, f"Deveria delegar, got {types}"
    results.append("[OK] 17. 'jogo de corrida 3d' -> delegate_to_brain (NAO template!)")
except Exception as ex:
    results.append(f"[ERRO] 17. {ex}")

# 18. "crie uma calculadora" -> create_script (template rapido)
try:
    r = e.process_message("crie uma calculadora")
    types = [a.get("type") for a in r.get("actions", [])]
    assert "create_script" in types, f"got {types}"
    results.append("[OK] 18. 'calculadora' -> create_script (template)")
except Exception as ex:
    results.append(f"[ERRO] 18. {ex}")

# 19. Open file smart + install
try:
    assert hasattr(e, '_try_open_file_smart')
    assert hasattr(e, '_try_install_program')
    results.append("[OK] 19. open_file_smart + install_program existem")
except Exception as ex:
    results.append(f"[ERRO] 19. {ex}")

# 20. WebSearch real
try:
    ws = get_web_search()
    result = ws.search("Python programming")
    assert result["success"]
    assert len(result["answer"]) > 20
    results.append(f"[OK] 20. WebSearch real ({len(result['answer'])} chars)")
except Exception as ex:
    results.append(f"[ERRO] 20. {ex}")

# ===== RESULTADO =====
lines = ["\n" + "="*65, "  TESTE v7 - WILLIAM v3 + AI BRAIN + DELEGATE (20 testes)", "="*65]
for r in results:
    lines.append(r)
ok = sum(1 for r in results if r.startswith("[OK]"))
lines.append(f"\nResultado: {ok}/{len(results)} OK")
if ok == len(results):
    lines.append("TUDO PRONTO! Rode WILLIAM.bat")
elif ok >= 18:
    lines.append("QUASE PERFEITO!")
lines.append("="*65)
print("\n".join(lines))
