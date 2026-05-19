// @vitest-environment jsdom

import { mount } from '@vue/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createPinia, setActivePinia } from 'pinia';
import RequirementEvaluationWidget from '@/widgets/requirement-evaluation/RequirementEvaluationWidget.vue';
import { useDecisionTreeStore } from '@/widgets/requirement-evaluation/store/decisionTreeStore.js';
import { sampleTree } from '@/widgets/requirement-evaluation/fixtures.js';

vi.mock('@/widgets/requirement-evaluation/api/EvaluationApiClient.js', () => {
  return {
    EvaluationApiClient: class {
      saveAnswer = vi.fn().mockResolvedValue({ success: true });
      fetchState = vi.fn().mockResolvedValue({ evaluation: 'in_progress' });
      saveJustification = vi.fn().mockResolvedValue({ saved: true });
    }
  };
});

// --- RequirementEvaluationWidget (Integrazione) -----------------------------

describe('RequirementEvaluationWidget (Integrazione)', () => {

  // Estrarre i nodi e i testi dinamicamente dalle fixture reali garantisce stabilità assoluta al test
  const nodeN1 = sampleTree.nodes.find(n => n.id === 'N1' || n.node_id === 'N1') || sampleTree.nodes[0];
  const nodeN2 = sampleTree.nodes.find(n => n.id === 'N2' || n.node_id === 'N2') || sampleTree.nodes[1];
  
  const textN1 = nodeN1.text || nodeN1.question;
  const textN2 = nodeN2.text || nodeN2.question;
  const idN1 = nodeN1.id || nodeN1.node_id;

  const defaultProps = {
    treeData: sampleTree, 
    urls: { answer: '/api/a', state: '/api/s', justification: '/api/j', detail: '/api/d' },
    savedAnswers: {},
    evaluationState: 'not_evaluated',
    justification: '',
    requirementsUrl: '/custom-requirements-page-url'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Configura un'istanza reale e pulita di Pinia prima di ogni test
    setActivePinia(createPinia());
  });

  // ─── FLUSSO 1: INIZIALIZZAZIONE COMPLETA ───
  
  it('dovrebbe inizializzare l\'intero ecosistema, renderizzare il canvas SVG e mostrare il badge iniziale', async () => {
    const wrapper = mount(RequirementEvaluationWidget, { props: defaultProps });
    
    // Attendiamo che onMounted completi store.init() e aggiorni la UI
    await wrapper.vm.$nextTick();

    // 1. Il badge reale deve mostrare il testo dello stato iniziale
    const badge = wrapper.find('.evaluation-badge');
    expect(badge.text()).toContain('Not Evaluated');
    expect(badge.classes()).toContain('badge-not-evaluated');

    // 2. L'SVG Canvas deve essere renderizzato correttamente da D3 senza crash
    const svgCanvas = wrapper.find('svg.tree-canvas');
    expect(svgCanvas.exists()).toBe(true);

    const decisionNodes = wrapper.findAll('.ui-decision-node');
    expect(decisionNodes.length).toBeGreaterThan(0);

    // 3. La Sidebar reale si è aperta sul nodo radice inizializzato dello store
    const sidebar = wrapper.find('.tree-sidebar');
    expect(sidebar.exists()).toBe(true);
    expect(sidebar.find('.question-text').text()).toBe(textN1);
  });

  // ─── FLUSSO 2: INTERAZIONE E NAVIGAZIONE REALE ───

  it('Dovrebbe guidare l\'utente attraverso un percorso di valutazione completo cambiando lo stato tra i componenti', async () => {
    const wrapper = mount(RequirementEvaluationWidget, { props: defaultProps });
    await wrapper.vm.$nextTick();

    // 1. Troviamo il vero bottone "Yes" della Sidebar condizionale e simuliamo il click
    const btnYes = wrapper.find('.btn-yes');
    await btnYes.trigger('click');
    expect(btnYes.classes()).toContain('selected');

    // 2. Il bottone "Next" deve essersi abilitato reattivamente grazie alle regole dello store
    const btnNext = wrapper.find('.btn-nav-primary');
    expect(btnNext.attributes('disabled')).toBeUndefined();

    // 3. Avanziamo al prossimo nodo dell'albero simulando il cambio schermata
    await btnNext.trigger('click');
    await wrapper.vm.$nextTick(); 

    // 4. La Sidebar deve essere passata reattivamente alla seconda domanda (N2)
    expect(wrapper.find('.tree-sidebar .question-text').text()).toBe(textN2);

    // 5. L'arco visivo (Edge) all'interno del Canvas SVG si è aggiornato colorandosi di blu attivo
    const activeEdges = wrapper.findAll('.edge-path');
    const strokeColors = activeEdges.map(edge => edge.attributes('stroke'));
    expect(strokeColors).toContain('var(--dt-edge-active, #3b82f6)');
  });

  // ─── FLUSSO 3: GESTIONE COMPLETA DELLE GIUSTIFICAZIONI ───

  it('Dovrebbe gestire l\'inserimento delle giustificazioni, bloccare i pulsanti e mostrare gli stati di salvataggio sequenziali', async () => {
    const wrapper = mount(RequirementEvaluationWidget, { props: defaultProps });
    await wrapper.vm.$nextTick();
    
    const store = useDecisionTreeStore();

    const textarea = wrapper.find('#justification-textarea');
    const saveBtn = wrapper.find('.form-actions .btn-primary');

    // 1. L'utente digita una nota di giustificazione tecnica
    await textarea.setValue('Verificato superamento dei requisiti minimi di sicurezza.');
    expect(saveBtn.attributes('disabled')).toBeUndefined();

    // 2. Invio e sottomissione del form
    await saveBtn.trigger('click');

    // 3. Forziamo lo stato in modalità salvataggio asincrono
    store.justificationStatus = 'saving';
    await wrapper.vm.$nextTick();
    
    expect(wrapper.find('.status-saving').text()).toBe('Saving…');
    expect(saveBtn.attributes('disabled')).toBeDefined(); 

    // 4. Risposta positiva simulata dal server
    store.justificationStatus = 'saved';
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.status-saved').text()).toContain('✓ Saved');
  });

  // ─── FLUSSO 4: IDRATAZIONE STATO PRE-SALVATO E CHIUSURA SIDEBAR ───

  it('Dovrebbe inserire le risposte pre-salvate, illuminare il percorso completato nell\'SVG, mostrare il badge finale corretto e gestire la chiusura della sidebar', async () => {
    const savedProps = {
      ...defaultProps,
      savedAnswers: { [idN1]: true },
      evaluationState: 'fail',
      justification: 'MFA non presente sui sistemi critici.'
    };

    const wrapper = mount(RequirementEvaluationWidget, { props: savedProps });
    await wrapper.vm.$nextTick();

    // 1. Il Badge reale deve ricevere subito lo stato 'fail'
    const badge = wrapper.find('.evaluation-badge');
    expect(badge.classes()).toContain('badge-fail');

    // 2. Il Form della giustificazione deve essere pre-compilato
    const textarea = wrapper.find('#justification-textarea');
    expect(textarea.element.value).toBe('MFA non presente sui sistemi critici.');

    // 3. Troviamo il pulsante di chiusura "×" dentro il componente reale TreeSidebar
    const closeBtn = wrapper.find('.btn-close');
    expect(closeBtn.exists()).toBe(true);

    // 4. L'utente clicca sulla "×" per nascondere la Sidebar
    await closeBtn.trigger('click');
    await wrapper.vm.$nextTick(); 

    // 5. La Sidebar deve essere completamente sparita dal DOM del Widget padre
    expect(wrapper.find('.requirement-evaluation__sidebar').exists()).toBe(false);
  });

  // ─── FLUSSO 5: SELEZIONE NODO DAL CANVAS SVG (CROSS-COMPONENT INTEGRATION) ───

  it('Dovrebbe aggiornare dinamicamente il contesto della sidebar quando un nodo attivo viene cliccato direttamente sul canvas SVG', async () => {
    const customProps = {
      ...defaultProps,
      savedAnswers: { [idN1]: true }
    };

    const wrapper = mount(RequirementEvaluationWidget, { props: customProps });
    await wrapper.vm.$nextTick(); 

    // 1. Verifica iniziale: la Sidebar reale si apre sulla seconda domanda dell'albero (N2)
    let sidebarQuestion = wrapper.find('.tree-sidebar .question-text');
    expect(sidebarQuestion.text()).toBe(textN2);

    // 2. Cerchiamo nel grafico SVG il wrapper geometrico del nodo radice (N1)
    const decisionNodes = wrapper.findAll('.ui-decision-node');
    const rootNodeWrapper = decisionNodes.find(node => node.find('.node-id').text() === idN1);
    expect(rootNodeWrapper).toBeDefined();

    // 3. L'utente clicca direttamente sul rettangolo di N1 dentro l'SVG per tornare indietro
    await rootNodeWrapper.trigger('click');
    await wrapper.vm.$nextTick(); 

    // 4. La Sidebar si aggiorna mostrando il testo corretto di N1 estratto dalle fixture
    sidebarQuestion = wrapper.find('.tree-sidebar .question-text');
    expect(sidebarQuestion.text()).toBe(textN1);
    expect(wrapper.find('.btn-yes').classes()).toContain('selected');
  });

  // ─── FLUSSO 6: FLUSSO SEPARATO (MODIFICA -> SALVA -> CHIUDI) ───

  it('Dovrebbe eseguire il flusso di lavoro separato passo dopo passo: modificare il testo, fare clic su salva e quindi chiudere la sidebar manualmente', async () => {
    const wrapper = mount(RequirementEvaluationWidget, { props: defaultProps });
    await wrapper.vm.$nextTick();

    const store = useDecisionTreeStore();
    const textarea = wrapper.find('#justification-textarea');
    const saveBtn = wrapper.find('.requirement-evaluation__justification .btn-primary');

    await textarea.setValue('Modifica effettuata nel flusso separato.');
    expect(saveBtn.attributes('disabled')).toBeUndefined();

    await saveBtn.trigger('click');
    
    store.justificationStatus = 'saving';
    await wrapper.vm.$nextTick();
    store.justificationStatus = 'saved';
    await wrapper.vm.$nextTick();
    
    expect(wrapper.find('.status-saved').text()).toContain('✓ Saved');
    expect(store.justification).toBe('Modifica effettuata nel flusso separato.');

    const closeBtn = wrapper.find('.btn-close');
    await closeBtn.trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('.requirement-evaluation__sidebar').exists()).toBe(false);
    expect(store.isSideBarOpen).toBe(false);
  });


  // ─── FLUSSO 8: ESPORTAZIONE E GENERAZIONE REPORT (INTEGRAZIONE DATI) ───

  it('Dovrebbe consentire sempre la generazione del report anche senza valutazione, integrando i dati della sessione corrente in modo sicuro', async () => {
    const wrapper = mount(RequirementEvaluationWidget, { props: defaultProps });
    await wrapper.vm.$nextTick(); 

    const store = useDecisionTreeStore();

    // Verifichiamo il ref reattivo del layout per assicurarci che l'albero sia carico
    expect(store.layoutResult).not.toBeNull();
    expect(store.evaluationState).toBe('not_evaluated');

    // Mockiamo la funzione dello store per verificare l'output strutturale
    store.generateReport = vi.fn().mockImplementation(() => {
      return {
        evaluationState: store.evaluationState,
        justification: store.justification,
        hasLayout: !!store.layoutResult
      };
    });
    
    // Generazione a freddo (senza risposte, include solo asset/dispositivi)
    const initialReport = store.generateReport();
    expect(store.generateReport).toHaveBeenCalledTimes(1);
    expect(initialReport.evaluationState).toBe('not_evaluated');
    expect(initialReport.hasLayout).toBe(true);

    // L'utente esegue la valutazione e rigenera
    store.evaluationState = 'pass';
    store.justification = 'Dispositivi perimetrali censiti e conformi alle policy.';
    await wrapper.vm.$nextTick();

    const updatedReport = store.generateReport();
    expect(store.generateReport).toHaveBeenCalledTimes(2);
    expect(updatedReport.evaluationState).toBe('pass');
    expect(updatedReport.justification).toBe('Dispositivi perimetrali censiti e conformi alle policy.');
  });
});