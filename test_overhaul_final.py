"""
Teste Final - Overhaul Arquitetural 26 Itens
Verifica que todos os modulos v4 importam e funcionam corretamente.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

results = []
total = 0
ok = 0

# ===== MODULOS V4 =====
all_modules = [
    # FASE 0
    ('observability', 'src.core.observability', 'get_event_log'),
    ('contracts', 'src.core.contracts', 'ActionResult'),
    ('security', 'src.core.security', 'RiskPolicy'),
    # FASE 1
    ('orchestrator', 'src.core.orchestrator', 'AgentOrchestrator'),
    ('roles', 'src.core.roles', 'RoleCard'),
    ('task_queue', 'src.core.task_queue', 'TaskQueue'),
    ('playbooks', 'src.core.playbooks', 'PlaybookManager'),
    # FASE 2
    ('knowledge_base', 'src.core.knowledge_base', 'KnowledgeBase'),
    ('semantic_search', 'src.core.semantic_search', 'SemanticSearch'),
    ('ollama_provider', 'src.ai_providers.ollama_provider', 'OllamaProvider'),
    ('openai_provider', 'src.ai_providers.openai_provider', 'OpenAIProvider'),
    ('anthropic_provider', 'src.ai_providers.anthropic_provider', 'AnthropicProvider'),
    # FASE 3
    ('base_skill', 'src.skills.base_skill', 'BaseSkill'),
    ('skill_manager', 'src.skills.skill_manager', 'SkillManager'),
    ('skill_store', 'src.skills.skill_store', 'SkillStore'),
    ('calculator_skill', 'src.skills.builtin.calculator_skill', 'CalculatorSkill'),
    ('browser_skill', 'src.skills.builtin.browser_skill', 'BrowserSkill'),
    ('triggers', 'src.core.triggers', 'TriggerManager'),
    # FASE 4
    ('nlp_ptbr', 'src.core.nlp_ptbr', 'NLPProcessor'),
    ('planner', 'src.core.planner', 'TaskPlanner'),
    # FASE 5
    ('tray_service', 'src.core.tray_service', 'WilliamTrayService'),
    ('autopecas_skill', 'src.skills.business.autopecas_skill', 'AutoPecasSkill'),
]

print('=' * 60)
print('  TESTE FINAL - OVERHAUL COMPLETO (26 ITENS)')
print('=' * 60)
print()
print('--- Importacao de Modulos ---')

for name, module_path, class_name in all_modules:
    total += 1
    try:
        mod = __import__(module_path, fromlist=[class_name])
        cls = getattr(mod, class_name)
        print(f'  [OK] {name}: {class_name}')
        ok += 1
    except Exception as e:
        print(f'  [FAIL] {name}: {e}')

print(f'\n  Modulos: {ok}/{total}')
print()

# ===== TESTES FUNCIONAIS =====
print('--- Testes Funcionais ---')
func_ok = 0
func_total = 0

# Test 1: RiskPolicy
func_total += 1
try:
    from src.core.security import get_risk_policy
    rp = get_risk_policy()
    assert rp.classify('delete') == 'red', f"Expected red, got {rp.classify('delete')}"
    assert rp.classify('datetime') == 'green'
    assert rp.classify('install') == 'yellow'
    func_ok += 1
    print('  [OK] RiskPolicy classifica green/yellow/red')
except Exception as e:
    print(f'  [FAIL] RiskPolicy: {e}')

# Test 2: ActionResult from_legacy
func_total += 1
try:
    from src.core.contracts import ActionResult
    legacy = {'success': True, 'type': 'test', 'message': 'ok'}
    ar = ActionResult.from_legacy(legacy)
    assert ar.success == True
    assert ar.action_type == 'test'
    d = ar.to_dict()
    assert d['success'] == True
    func_ok += 1
    print('  [OK] ActionResult from_legacy() + to_dict()')
except Exception as e:
    print(f'  [FAIL] ActionResult: {e}')

# Test 3: EventLog
func_total += 1
try:
    from src.core.observability import get_event_log
    el = get_event_log()
    el.log_event('test_final', data={'phase': 'verification'})
    func_ok += 1
    print('  [OK] EventLog registra evento')
except Exception as e:
    print(f'  [FAIL] EventLog: {e}')

# Test 4: KnowledgeBase
func_total += 1
try:
    from src.core.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()
    kb.add_fact('Python foi criado por Guido van Rossum', category='tech', source='teste')
    r = kb.query('Python Guido')
    assert len(r) > 0
    func_ok += 1
    print('  [OK] KnowledgeBase add_fact + query')
except Exception as e:
    print(f'  [FAIL] KnowledgeBase: {e}')

# Test 5: SemanticSearch
func_total += 1
try:
    from src.core.semantic_search import SemanticSearch
    ss = SemanticSearch()
    docs = [
        {"id": "doc1", "content": "Python e uma linguagem de programacao"},
        {"id": "doc2", "content": "Java tambem e popular"},
    ]
    r = ss.search('Python programacao', documents=docs, limit=2)
    assert len(r) > 0
    assert r[0][0]["id"] == "doc1"
    func_ok += 1
    print('  [OK] SemanticSearch keyword search')
except Exception as e:
    print(f'  [FAIL] SemanticSearch: {e}')

# Test 6: NLP normaliza
func_total += 1
try:
    from src.core.nlp_ptbr import get_nlp_processor
    nlp = get_nlp_processor()
    result = nlp.normalize('vc pd abrir o chrome pfv')
    assert 'voce' in result.lower() or 'você' in result.lower()
    func_ok += 1
    print(f'  [OK] NLP normaliza: "vc pd...pfv" -> "{result}"')
except Exception as e:
    print(f'  [FAIL] NLP normalize: {e}')

# Test 7: NLP extract_intent
func_total += 1
try:
    from src.core.nlp_ptbr import get_nlp_processor
    nlp = get_nlp_processor()
    intent = nlp.extract_intent('abra o chrome')
    assert intent['action'] is not None
    func_ok += 1
    print(f'  [OK] NLP extract_intent: action={intent["action"]}, target={intent.get("target")}')
except Exception as e:
    print(f'  [FAIL] NLP intent: {e}')

# Test 8: Planner
func_total += 1
try:
    from src.core.planner import TaskPlanner
    tp = TaskPlanner()
    plan = tp.create_plan('pesquise precos e depois crie uma planilha')
    assert plan is not None
    assert len(plan.steps) >= 2
    func_ok += 1
    print(f'  [OK] Planner: {len(plan.steps)} steps decomposed')
except Exception as e:
    print(f'  [FAIL] Planner: {e}')

# Test 9: TaskQueue
func_total += 1
try:
    from src.core.task_queue import get_task_queue
    tq = get_task_queue()
    t = tq.create_task('TestFinal', 'desc', 'cmd', 'general_agent')
    tq.update_state(t.id, 'in_progress')
    tq.update_state(t.id, 'done')
    kanban = tq.get_kanban_view()
    assert 'done' in kanban
    func_ok += 1
    print('  [OK] TaskQueue state machine + kanban')
except Exception as e:
    print(f'  [FAIL] TaskQueue: {e}')

# Test 10: Scheduler stats
func_total += 1
try:
    from src.core.scheduler import get_scheduler
    sched = get_scheduler()
    stats = sched.get_stats()
    assert 'total_tasks' in stats
    assert 'running' in stats
    func_ok += 1
    print(f'  [OK] Scheduler stats: {stats}')
except Exception as e:
    print(f'  [FAIL] Scheduler: {e}')

# Test 11: SkillManager
func_total += 1
try:
    from src.skills.skill_manager import SkillManager
    sm = SkillManager()
    skills = sm.list_skills()
    assert len(skills) > 0
    func_ok += 1
    print(f'  [OK] SkillManager: {len(skills)} skills auto-discovered')
except Exception as e:
    print(f'  [FAIL] SkillManager: {e}')

# Test 12: CalculatorSkill
func_total += 1
try:
    from src.skills.builtin.calculator_skill import CalculatorSkill
    cs = CalculatorSkill()
    score = cs.can_handle('quanto e 2+2')
    assert score > 0.5
    result = cs.execute('calcule 2+2')
    assert result.success
    func_ok += 1
    print(f'  [OK] CalculatorSkill: 2+2 = {result.data.get("result", "?")}')
except Exception as e:
    print(f'  [FAIL] CalculatorSkill: {e}')

# Test 13: AutoPecasSkill
func_total += 1
try:
    from src.skills.business.autopecas_skill import AutoPecasSkill
    aps = AutoPecasSkill()
    score = aps.can_handle('tem alternador para gol g4')
    assert score > 0.5
    result = aps.execute('consultar peca alternador')
    assert result.success
    func_ok += 1
    print(f'  [OK] AutoPecasSkill: {result.message[:60]}')
except Exception as e:
    print(f'  [FAIL] AutoPecasSkill: {e}')

# Test 14: SandboxScope
func_total += 1
try:
    from src.core.security import SandboxScope
    scope = SandboxScope(allowed_dirs=['C:/Users/wizip/Desktop'])
    assert scope.validate_path('C:/Users/wizip/Desktop/test.txt') == True
    assert scope.validate_path('C:/Windows/System32/cmd.exe') == False
    func_ok += 1
    print('  [OK] SandboxScope: paths validados corretamente')
except Exception as e:
    print(f'  [FAIL] SandboxScope: {e}')

# Test 15: TriggerManager
func_total += 1
try:
    from src.core.triggers import get_trigger_manager
    tm = get_trigger_manager()
    stats = tm.get_stats()
    assert 'total_rules' in stats
    assert 'watchdog_available' in stats
    func_ok += 1
    print(f'  [OK] TriggerManager: watchdog={stats["watchdog_available"]}')
except Exception as e:
    print(f'  [FAIL] Triggers: {e}')

# Test 16: Playbooks
func_total += 1
try:
    from src.core.playbooks import get_playbook_manager
    pm = get_playbook_manager()
    pbs = pm.list_playbooks()
    assert len(pbs) > 0
    # Test pattern match
    match = pm.find_playbook('pesquise tudo sobre Python')
    func_ok += 1
    print(f'  [OK] Playbooks: {len(pbs)} loaded, match={"Yes" if match else "No"}')
except Exception as e:
    print(f'  [FAIL] Playbooks: {e}')

# Test 17: ProofCollector
func_total += 1
try:
    from src.core.contracts import ProofCollector, ActionResult
    ar = ActionResult(success=True, action_type='datetime', message='test')
    proof = ProofCollector.collect_proof(ar)
    func_ok += 1
    print(f'  [OK] ProofCollector: proof={proof}')
except Exception as e:
    print(f'  [FAIL] ProofCollector: {e}')

# Test 18: Roles
func_total += 1
try:
    from src.core.roles import get_all_roles, select_best_role
    roles = get_all_roles()
    assert len(roles) >= 5
    role = select_best_role('open_browser')
    assert role is not None
    func_ok += 1
    print(f'  [OK] Roles: {len(roles)} roles, open_browser -> {role.name}')
except Exception as e:
    print(f'  [FAIL] Roles: {e}')

# Test 19: NLP business intent detection
func_total += 1
try:
    from src.core.nlp_ptbr import get_nlp_processor
    nlp = get_nlp_processor()
    intent = nlp.detect_business_intent('tem peca para motor AP 1.8')
    assert intent is not None
    func_ok += 1
    print(f'  [OK] NLP business intent: {intent.get("type", "?")}')
except Exception as e:
    print(f'  [FAIL] NLP business: {e}')

# Test 20: SkillStore
func_total += 1
try:
    from src.skills.skill_store import SkillStore
    store = SkillStore()
    catalog = store.list_available()
    assert len(catalog) > 0
    func_ok += 1
    print(f'  [OK] SkillStore: {len(catalog)} skills in catalog')
except Exception as e:
    print(f'  [FAIL] SkillStore: {e}')

print(f'\n  Testes funcionais: {func_ok}/{func_total}')

# ===== RESUMO FINAL =====
print()
print('=' * 60)
grand_total = ok + func_ok
grand_max = total + func_total
print(f'  IMPORTACOES:  {ok}/{total}')
print(f'  FUNCIONAIS:   {func_ok}/{func_total}')
print(f'  TOTAL GERAL:  {grand_total}/{grand_max}')
print()
if grand_total == grand_max:
    print('  *** OVERHAUL 26 ITENS - COMPLETO E VERIFICADO! ***')
else:
    print(f'  ATENCAO: {grand_max - grand_total} falha(s)')
print('=' * 60)
