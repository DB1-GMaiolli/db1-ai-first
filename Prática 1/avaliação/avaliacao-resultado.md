# Avaliação — Trilha AI First DGS | Cenário 1 | Papel: Desenvolvedor

> **Programa:** Trilha de Certificação AI First — DGS / DB1 Global Software
> **Cenário:** 1 — Fase de Entendimento e Contexto
> **Papel:** Desenvolvedor
> **Exercícios avaliados:** 1.1, 1.2, 1.3
> **Rubrica aplicada:** `avaliacao-foundation.md` + `avaliacao-desenvolvedor.md`

---

## Avaliação do Exercício 1.1
### Análise de Viabilidade Técnica com Fundamentos de LLM e Engenharia de Contexto

### Resumo

O entregável entrega uma análise técnica de alto nível, com cobertura completa dos quatro tópicos exigidos e iteração claramente demonstrada entre v1 e v2. A Parte 2 (crítica) é o ponto mais forte: identifica um bug crítico não-óbvio do `openpyxl data_only=True`, a ausência de busca híbrida e a falta de estratégia de fallback — todos riscos que um leitor desavisado não perceberia na v1. O entregável final (v2) é diretamente acionável para a base NovaTech.

### Scores por Dimensão

| Dimensão | Score | Justificativa |
|----------|-------|---------------|
| D1 — Domínio Conceitual | 3 | Cada tipo de fonte tem desafio, impacto e estratégia específicos e diferenciados. Estimativa de tokens mostra o cálculo (1 palavra ≈ 1,33 tokens aplicado por fonte). Orçamento de contexto calculado corretamente: 128K − 2K system − 500 query − 4K resposta ≈ 121K para chunks, com análise de 247 chunks teóricos vs. 8–15 práticos. Chunking híbrido justificado por tipo de conteúdo e tipo de pergunta, com referência ao efeito lost-in-the-middle e estratégia de reordenação de chunks nos extremos do contexto. |
| D2 — Uso de Ferramentas | 3 | Iteração explícita e verificável: a Parte 1 produz a análise inicial, a Parte 2 instrui o Claude a criticá-la e a versão final (v2) incorpora cada ponto levantado. O ciclo gerar → avaliar → iterar está visível e substancial: v1 estimava 4,1M tokens; v2 corrige para 4,7M justificando o overhead de Markdown. Seis pontos fracos identificados pela crítica foram todos incorporados à v2. |
| D3 — Qualidade do Entregável | 3 | Completo, correto e específico ao NovaTech. Cobre PDFs SharePoint, wiki Confluence, planilhas Excel e PDFs escaneados com estratégias distintas. Pipeline de ingestão e query documentados em pseudocódigo executável. Métricas RAGAS com targets definidos. Outro membro do time usaria sem pedir esclarecimentos. |
| D4 — Pensamento Crítico | 3 | Análise profunda na Parte 2: identifica o bug silencioso do `openpyxl data_only=True` (falha não-óbvia e crítica), a ausência de busca híbrida BM25 + dense embeddings como lacuna grave, o risco de controle de acesso e documentos restritos, a ausência de estratégia de avaliação contínua (RAGAS) e o fallback quando retrieval falha. Nenhum desses pontos é óbvio — demonstra julgamento técnico próprio, não delegação total à IA. |
| D5 — Aplicabilidade ao Projeto | 3 | Profundamente conectado: usa os volumes exatos (800 PDFs, 400 páginas wiki, 50 planilhas), referencia as fontes específicas (SharePoint, Confluence), calcula o total de tokens para esse corpus exato e propõe pipeline com tecnologias compatíveis com a infraestrutura NovaTech (Azure Document Intelligence mencionado por ser alinhado ao Azure já em uso). |

**Score do exercício: 3.0**

### Verificação de Armadilhas

Nenhuma armadilha intencional listada para este exercício nos critérios do Desenvolvedor.

### Pontos Fortes

1. **Bug não-óbvio identificado e corrigido:** O comportamento de `openpyxl data_only=True` retornar `None` para arquivos gerados programaticamente é uma limitação real, documentada e crítica — o participante a identificou na autocrítica e propôs solução concreta (pipeline de dois estágios com fallback via COM automation ou LibreOffice headless).
2. **Busca híbrida como não-negociável:** A v1 assumia busca semântica pura; a v2 argumenta corretamente que BM25 + dense embeddings com Reciprocal Rank Fusion é o padrão da indústria para cobrir termos corporativos exatos ("Cláusula 4.2.1", "NF-e 3.10") — raciocínio técnico sólido.
3. **Estimativa de tokens revisada com justificativa:** A v1 usava 300 palavras/página para PDFs com tabelas; a v2 revisa para 250 palavras com +40% de overhead de Markdown para tabelas densas, chegando a 4,7M tokens. A correção é justificada e o método de cálculo está exposto.

### Pontos de Melhoria

1. **Custo operacional ausente na v2 também:** A crítica levantou esse ponto, mas a v2 não o incorporou quantitativamente. Para completude, adicionar estimativa de custo de embedding (4,7M tokens × preço do modelo) e de Document Intelligence (800 PDFs × 10 páginas × custo por página) antes da seção de pipeline.
2. **Graph-aware chunking ainda incompleto:** A v2 limita a expansão a 1 nível de profundidade e trata ciclos, mas não define como o "resumo de 150 tokens" da página destino é gerado (por LLM? sumário automático?) nem como é atualizado quando a página destino muda. Vale especificar o mecanismo.

### Classificação

**Aprovado com distinção** (score 3.0)

### Tópicos da Trilha para Reforço

Score ≥ 2.5 — nenhum tópico com necessidade de reforço identificado.

---

## Avaliação do Exercício 1.2
### Prototipação de Prompt com Engenharia de Contexto

### Resumo

O entregável é um dos mais completos desta avaliação: produz um system prompt bem estruturado (v1), testa três perguntas reais, realiza análise crítica granular das respostas com verificação por afirmação e documento, e produz uma v2 com changelog explícito de sete mudanças rastreáveis. A armadilha obrigatória da trilha (carga perigosa como inelegível) foi identificada corretamente já na v1. A v2 elimina todos os problemas de processo sem alterar a correção factual.

### Scores por Dimensão

| Dimensão | Score | Justificativa |
|----------|-------|---------------|
| D1 — Domínio Conceitual | 3 | System prompt com todas as seções exigidas (identidade, guardrails, hierarquia de fontes, formato de resposta, instruções para chunks). Mapeamento estático vs. dinâmico com estimativa de tokens por componente (670 tokens estáticos + 220–1.680 dinâmicos). Análise de estouro de contexto com quatro estratégias de mitigação ordenadas por preferência. Hierarquia de fontes (normativo > procedimento versão mais recente > FAQ) com lógica de desempate explícita. |
| D2 — Uso de Ferramentas | 3 | Iteração v1 → v2 verificável: changelog com sete itens mapeando falha → correção. A v1 tinha guardrails implícitos sobre conflito de versão; a v2 adiciona Regra 6 (declaração obrigatória de conflito) e Regra 7 (reconciliação FAQ × formal). Segunda rodada de testes demonstra que as correções funcionam — as três respostas da v2 eliminam todas as falhas identificadas no Item 4. |
| D3 — Qualidade do Entregável | 3 | Três perguntas testadas com respostas reais documentadas. Análise crítica por afirmação (tabela de verificação por chunk para as respostas 1, 2 e 3). System prompt v2 com impacto em tokens calculado (+280 tokens, total de ~950). Comparativo v1 × v2 em tabela. O entregável é acionável: outro dev do time poderia usar o system prompt e o processo de iteração diretamente. |
| D4 — Pensamento Crítico | 3 | Análise profunda das três respostas: identifica que a Resposta 1 não flagou a divergência com FAQ-03 (ponto sutil — a resposta estava factualmente correta, mas omitiu informação operacionalmente relevante); que a Resposta 2 expandiu escopo sem declarar; que a Resposta 3 usou o valor correto do multiplicador (1.8) mas silenciou sobre a existência da v1 com Norte = 1.6, risco concreto de subcobança de 12,5%. Identifica o padrão transversal de falha (processo, não fato). |
| D5 — Aplicabilidade ao Projeto | 3 | Usa os chunks reais da NovaTech (POL-001, SLA-2024, PROC-042-v2) e os guardrails definidos pelo Product Specialist do projeto. Hierarquia de fontes específica ao contexto (documentos normativos NovaTech vs. FAQ colaborativo não validado pelo Compliance). Sistema de citação de fonte (código + seção + versão) adequado ao corpus corporativo da empresa. |

**Score do exercício: 3.0**

### Verificação de Armadilhas

| Armadilha | Descrição | Identificada? |
|-----------|-----------|:---:|
| Prazo de devolução para carga perigosa | A resposta correta é que carga perigosa NÃO é elegível para devolução (POL-001, seção 3.2) — não há prazo, pois o processo padrão não se aplica. System prompt v1 que gere "prazo de X dias" seria falha de D4. | ✅ Sim |

**Detalhe:** A Resposta 1 do Item 3 declara explicitamente: *"Cargas perigosas classificadas nas classes 1 a 6 da ANTT não são elegíveis para devolução pelo processo padrão, independentemente do prazo. Não existe um prazo específico de devolução para esse tipo de carga dentro do procedimento regular."* — resposta correta, armadilha não ativou D4 ≤ 1.

### Pontos Fortes

1. **Detecção do risco de subcobrança de frete:** O participante identifica que o silêncio da Resposta 3 sobre o conflito PROC-042 v1 vs. v2 levaria um atendente consultando a tabela antiga a aplicar Norte = 1.6 em vez de 1.8, gerando subcobrança de 12,5% — raciocínio de impacto operacional concreto, não apenas formal.
2. **Checklist pré-resposta na v2:** A adição da "Etapa Obrigatória Antes de Responder" (inventário de chunks, detecção de conflito de versão, divergência FAQ, disposições transitórias) transforma regras implícitas em processo explícito verificável — melhoria estrutural que vai além de corrigir sintomas.
3. **Campo `⚠️ Conflito de versões` no template:** A v2 adiciona um campo opcional ao formato de resposta especificamente para conflitos de versão, com estrutura padronizada. Isso torna o sistema auditável e protege contra erros em produção.

### Pontos de Melhoria

1. **Estimativa de tokens não revisada na v2:** O Item 2 calcula ~670 tokens para o system prompt v1. A v2 adiciona ~280 tokens, chegando a ~950 — mencionado apenas no rodapé. Vale atualizar a tabela do Item 2 com a nova estrutura, para o documento ficar autoconsistente.
2. **Não há teste de fallback (nenhum chunk relevante):** As três perguntas testadas têm resposta nos chunks. Seria valioso testar um cenário onde nenhum chunk é suficiente (ex.: "Qual o telefone do Comercial?") para verificar se o guardrail "Não localizei essa informação" funciona corretamente.

### Classificação

**Aprovado com distinção** (score 3.0)

### Tópicos da Trilha para Reforço

Score ≥ 2.5 — nenhum tópico com necessidade de reforço identificado.

---

## Avaliação do Exercício 1.3
### Construção de Pipeline de RAG com Ferramentas Open-Source

### Resumo

O entregável documenta um pipeline RAG funcional com ChromaDB e sentence-transformers, executa sete testes (acima do mínimo de cinco), compara os chunks recuperados com o gabarito e identifica dois problemas reais com propostas de correção implementáveis. O nível de detalhe dos testes é elevado: prompts completos documentados, scores de similaridade reais, avaliação por chunk e análise por resposta. A ferramenta de codificação com IA utilizada foi o Claude Code (uso autorizado em substituição ao GitHub Copilot), e a evidência está no próprio arquivo: o prompt de instrução ao Claude Code está documentado no início do 1.3.md — específico, com parâmetros técnicos já decididos pelo participante e justificativa de chunking solicitada como comentário no código gerado.

### Scores por Dimensão

| Dimensão | Score | Justificativa |
|----------|-------|---------------|
| D1 — Domínio Conceitual | 3 | Pipeline completo: ingestão (leitura de .txt, chunking com RecursiveCharacterTextSplitter, embedding com all-MiniLM-L6-v2, persistência no ChromaDB), função de busca com retorno estruturado (chunk_id, text, source, score) e build_prompt com SYSTEM/CONTEXTO/PERGUNTA/RESPOSTA. Chunking com separadores hierárquicos justificados (`["\n\n", "\n", ". "]`) e overlap de 200 chars justificado. Configuração (1200 chars, 200 overlap, 15 chunks indexados) está documentada e tem justificativa técnica. |
| D2 — Uso de Ferramentas | 3 | Claude Code foi usado como ferramenta de codificação com IA (uso autorizado). A evidência está no início do 1.3.md: o participante elaborou um prompt longo e específico — não genérico — que instrui o Claude Code com parâmetros técnicos já decididos (chunk_size 1200, overlap 200, separadores hierárquicos, modelo all-MiniLM-L6-v2, assinaturas das funções, formato de saída dos testes) e solicita explicitamente um comentário de justificativa técnica no código gerado. Isso demonstra que o participante dirigiu a ferramenta com julgamento próprio, não delegou a decisão de arquitetura. O pipeline rodou e os resultados documentados são coerentes com o código descrito. |
| D3 — Qualidade do Entregável | 3 | Sete testes executados (mínimo era cinco). Cada teste inclui: tabela de chunks com fonte, score e preview de 80 chars, classificação correto/incorreto, prompt completo (build_prompt) e avaliação estruturada (correta? citou fonte? respeitou guardrail?). Taxa de acerto calculada por teste (20% a 100%). Dois problemas reais identificados com propostas concretas. Ao menos 5/7 respostas finais corretas (testes 1, 2, 3, 4, 5 e 7 têm resposta correta; teste 6 tem resposta correta apesar de 20% de taxa de acerto nos chunks). |
| D4 — Pensamento Crítico | 3 | Os dois problemas identificados são derivados dos testes reais, não inventados: (1) versões conflitantes na mesma query (Teste 5, chunks com Norte = 1.6 e 1.8 no mesmo contexto) com score documentado; (2) chunks irrelevantes por similaridade semântica superficial (Teste 6 com 20% de acerto, Teste 4 com 40%). Propostas de correção são implementáveis: metadados `document_family` + `document_version` com filtro pós-recuperação; cross-encoder `ms-marco-MiniLM-L-6-v2` como reranker. Raciocínio técnico sólido sobre por que o modelo all-MiniLM-L6-v2 captura similaridade de domínio em vez de relevância específica. |
| D5 — Aplicabilidade ao Projeto | 3 | Pipeline construído sobre os documentos reais da NovaTech (POL-001, PROC-042 v1 e v2, SLA-2024, FAQ-atendimento). Perguntas de teste derivadas do contexto de negócio da empresa (devolução de carga perigosa, tiers de SLA, multiplicadores regionais). O Problema 1 identificado é diretamente relevante para a operação: a coexistência de PROC-042 v1 e v2 sem marcação de obsolescência no sistema da NovaTech é um risco real documentado no próprio arquivo fonte. |

**Score do exercício: 3.0**

### Verificação de Armadilhas

Nenhuma armadilha intencional listada para este exercício nos critérios do Desenvolvedor.
**Nota:** O Problema 1 identificado pelo participante (versões conflitantes recuperadas simultaneamente) reflete o risco real da coexistência de PROC-042 v1 e v2 — o que demonstra atenção a riscos de qualidade do sistema, alinhado ao espírito da rubrica.

### Pontos Fortes

1. **Execução real documentada:** Os scores de similaridade coseno (ex: 0.3979, 0.5137, 0.6827) com casas decimais e a variação real de taxa de acerto entre testes (20% no Teste 6 vs 100% no Teste 3) indicam execução genuína do pipeline — não resultados fabricados.
2. **Resposta correta no Teste 5 (conflito de versões):** Mesmo sem reranker, o LLM final identificou o conflito entre Norte = 1.6 (v1) e Norte = 1.8 (v2) no mesmo contexto e respondeu com a versão correta + disposições transitórias — demonstrando que o system prompt do pipeline lida bem com esse caso quando os dois chunks estão presentes.
3. **Problema 2 com proposta técnica sólida:** A proposta de cross-encoder como reranker pós-recuperação, com threshold de corte para fallback, é a solução padrão da indústria para o problema de chunks irrelevantes por similaridade superficial — demonstra domínio além do básico.

### Pontos de Melhoria

1. **Taxa de acerto por teste não consolidada:** O entregável calcula a taxa de acerto por teste individualmente, mas não apresenta média geral nem análise de por que certos tipos de pergunta (tier/classificação, carga danificada) têm desempenho sistematicamente pior. Uma tabela consolidada ao final (pergunta × taxa de acerto × causa provável da falha de retrieval) tornaria o diagnóstico mais acionável.
2. **Prompt ao Claude Code não inclui iteração documentada:** O prompt inicial ao Claude Code é detalhado, mas o entregável não mostra se houve ciclos de ajuste (ex.: o código rodou de primeira? houve erro de dependência? o formato de saída precisou ser corrigido?). Documentar ao menos uma rodada de ajuste — mesmo que pequena — evidenciaria o ciclo completo de uso da ferramenta.

### Classificação

**Aprovado com distinção** (score 3.0)

### Tópicos da Trilha para Reforço

Score ≥ 2.5 — nenhum tópico com necessidade de reforço identificado.

---

## Resumo Geral

| Exercício | D1 | D2 | D3 | D4 | D5 | Score | Classificação |
|-----------|:--:|:--:|:--:|:--:|:--:|:-----:|---------------|
| 1.1 — Viabilidade técnica RAG | 3 | 3 | 3 | 3 | 3 | **3.0** | Aprovado com distinção |
| 1.2 — Prototipação de prompt | 3 | 3 | 3 | 3 | 3 | **3.0** | Aprovado com distinção |
| 1.3 — Pipeline RAG open-source | 3 | 3 | 3 | 3 | 3 | **3.0** | Aprovado com distinção |
| **Média do cenário** | | | | | | **3.0** | **Aprovado com distinção** |

### Padrão geral do participante

O participante demonstra domínio sólido e consistente dos fundamentos de LLM, engenharia de contexto e RAG nos três exercícios. O diferencial está no pensamento crítico: em todos os exercícios o participante vai além da entrega inicial, identifica falhas não-óbvias (bug do `openpyxl`, risco de subcobrança de 12,5% por silêncio sobre conflito de versões, chunks irrelevantes por similaridade superficial) e produz versões melhoradas com justificativas rastreáveis. O uso de ferramentas de IA foi efetivo e dirigido — em todos os casos há evidência de ciclo gerar → avaliar → iterar, não delegação acrítica.
