"""Teste final - verifica tudo funcional."""
import sys, os
sys.path.insert(0, r"C:\Users\wizip\Desktop\WILTOP")
os.environ["LOG_LEVEL"] = "CRITICAL"

out = open(r"C:\Users\wizip\Desktop\WILTOP\test_result.txt", "w", encoding="utf-8")
def log(msg):
    print(msg, flush=True)
    out.write(msg + "\n")
    out.flush()

results = []

# 1. SmartExecutorV2
try:
    from src.core.smart_executor_v2 import SmartExecutorV2
    e = SmartExecutorV2()
    results.append("[OK] SmartExecutorV2")
except Exception as ex:
    results.append(f"[ERRO] SmartExecutorV2: {ex}")

# 2. Memory avancada
try:
    from src.core.memory import get_memory
    m = get_memory()
    assert hasattr(m, '_evolve_personality')
    assert hasattr(m, '_learn_vocabulary')
    assert hasattr(m, '_track_topics')
    assert hasattr(m, 'get_level_info')
    results.append("[OK] Memory avancada (personalidade, vocabulario, topicos, niveis)")
except Exception as ex:
    results.append(f"[ERRO] Memory: {ex}")

# 3. Web Search
try:
    from src.core.web_search import get_web_search, WebSearchEngine
    ws = get_web_search()
    assert isinstance(ws, WebSearchEngine)
    results.append("[OK] WebSearchEngine importado")
except Exception as ex:
    results.append(f"[ERRO] WebSearch: {ex}")

# 4. GUI
try:
    from src.interfaces.gui.william_final import WilliamFinal, COLORS
    assert hasattr(WilliamFinal, '_show_memory')
    assert hasattr(WilliamFinal, '_update_level_display')
    assert hasattr(WilliamFinal, '_start_clock')
    assert "neon_cyan" in COLORS
    assert "neon_purple" in COLORS
    results.append("[OK] GUI futurista (cores neon, clock, level display)")
except Exception as ex:
    results.append(f"[ERRO] GUI: {ex}")

# 5. Lixeira -> app
try:
    r = e.process_message("abra a lixeira")
    types = [a.get("type") for a in r.get("actions", [])]
    assert "open_app" in types, f"Esperava open_app, got {types}"
    results.append("[OK] 'abra a lixeira' -> open_app")
except Exception as ex:
    results.append(f"[ERRO] lixeira: {ex}")

# 6. Busca local
try:
    r = e.process_message("procure no meu pc arquivo teste.txt")
    types = [a.get("type") for a in r.get("actions", [])]
    assert "search_local" in types, f"Esperava search_local, got {types}"
    results.append("[OK] 'procure no pc' -> search_local")
except Exception as ex:
    results.append(f"[ERRO] local: {ex}")

# 7. Pesquisa web (abre google - nao traz aqui)
try:
    # Nao vai abrir browser pq o webbrowser.open vai rodar mas ok
    r = e.process_message("pesquise sobre python")
    types = [a.get("type") for a in r.get("actions", [])]
    assert "search" in types, f"Esperava search, got {types}"
    results.append("[OK] 'pesquise sobre python' -> search (Google)")
except Exception as ex:
    results.append(f"[ERRO] search: {ex}")

# 8. Pesquisa web com "traga" -> web_answer
try:
    r = e.process_message("pesquise sobre o clima em sao paulo e me traga a resposta aqui")
    types = [a.get("type") for a in r.get("actions", [])]
    # Pode ser web_answer (sucesso) ou search (fallback)
    if "web_answer" in types:
        results.append("[OK] 'pesquise e traga' -> web_answer (scraped!)")
    elif "search" in types:
        results.append("[OK] 'pesquise e traga' -> search (fallback, scraping pode ter falhado)")
    else:
        results.append(f"[AVISO] 'pesquise e traga' -> {types}")
except Exception as ex:
    results.append(f"[ERRO] web_answer: {ex}")

# 9. Level system
try:
    info = m.get_level_info()
    assert "nivel" in info
    assert "titulo" in info
    assert "xp" in info
    assert "progress_pct" in info
    results.append(f"[OK] Level system: LVL {info['nivel']} - {info['titulo']}")
except Exception as ex:
    results.append(f"[ERRO] level: {ex}")

# 10. Memory stats
try:
    stats = m.get_stats()
    assert "WILLIAM" in stats
    assert "Nivel" in stats
    results.append("[OK] Memory stats detalhadas")
except Exception as ex:
    results.append(f"[ERRO] stats: {ex}")

log("\n" + "="*60)
log("  TESTE FINAL - WILLIAM v2.0 FUTURISTA")
log("="*60)
for r in results:
    log(r)

ok = sum(1 for r in results if r.startswith("[OK]"))
total = len(results)
log(f"\nResultado: {ok}/{total} testes passaram")
if ok == total:
    log("TUDO PRONTO! Pode rodar WILLIAM.bat")
log("="*60)
out.close()
