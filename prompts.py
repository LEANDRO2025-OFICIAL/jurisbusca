"""Biblioteca de prompts juridicos - agregado do curso 'Desbloqueando o uso da IA na Rotina Juridica'.

Categorias de prompts relevantes para o JurisBusca:
- Busca de Jurisprudencia
- Conferencia de Citacoes
- Analise de Acordao
- Extrator de Argumentos
- Auditoria de Acordao
- Pesquisa de Teses Repetitivas
- Leitura Profunda
"""

PROMPTS = {
    "busca_jurisprudencia": {
        "nome": "Busca de Jurisprudencia",
        "descricao": "Busca jurisprudencia relevante para uma tese juridica",
        "prompt": """Voce e um assistente juridico especializado em pesquisa de jurisprudencia.
Dado o tema/tese abaixo, identifique:
1. Quais sumulas e temas do CNJ se aplicam
2. Quais acordaos do STJ/STF/TST sao relevantes
3. Qual a tese firmada em cada precedente
4. A situacao atual de cada precedente (vigente, superado, modificado)

TEMA/TESE: {tema}

Responda de forma estruturada, com numero do precedente, orgao julgador, data e tese.""",
    },
    "conferencia_citacoes": {
        "nome": "Conferencia de Citacoes de Jurisprudencia",
        "descricao": "Confere se as citacoes de jurisprudencia em uma peca sao corretas",
        "prompt": """Voce e um assistente juridico especializado em conferencia de citacoes.
Analise as citacoes de jurisprudencia abaixo e verifique:
1. Se o numero do processo/acordao esta correto
2. Se a tese atribuida ao precedente corresponde ao que foi decidido
3. Se o precedente ainda esta vigente ou foi superado
4. Se ha divergencia entre tribunais sobre o tema

CITACOES: {citacoes}

Responda com: OK, INCORRETO ou NAO VERIFICADO para cada citacao, com justificativa.""",
    },
    "analise_acordao": {
        "nome": "Analise de Acordao",
        "descricao": "Analisa um acordao e extrai campos estruturados",
        "prompt": """Voce e um assistente juridico especializado em analise de acordaos.
Analise o acordao abaixo e extraia:
1. EMENTA (resumo da decisao)
2. RELATORIO (fatos do caso)
3. VOTO (fundamentacao juridica)
4. DISPOSITIVO (decisao final)
5. AREA DO DIREITO (civil, penal, trabalhista, tributario, administrativo, constitucional)
6. TEMA (tema principal)
7. TESE FIRMADA (se houver)
8. PRECEDENTES CITADOS (lista)
9. CONFLITO DE JURISPRUDENCIA (se houver divergencia)

ACORDAO: {acordao}

Responda em formato JSON estruturado.""",
    },
    "extrator_argumentos": {
        "nome": "Extrator de Argumentos e Fundamentos",
        "descricao": "Extrai argumentos e fundamentos de decisoes judiciais",
        "prompt": """Voce e um assistente juridico especializado em extracao de argumentos.
Analise a decisao abaixo e extraia:
1. ARGUMENTOS DO AUTOR/REQUERENTE
2. ARGUMENTOS DO REU/REQUERIDO
3. FUNDAMENTOS JURIDICOS (leis, sumulas, precedentes citados)
4. TESE CENTRAL DA DECISAO
5. PONTOS CONTROVERTIDOS
6. FATORES DETERMINANTES (o que levou a decisao)

DECISAO: {decisao}

Responda de forma estruturada.""",
    },
    "auditoria_acordao": {
        "nome": "Auditoria de Acordao",
        "descricao": "Audita um acordao verificando consistencia e fundamentacao",
        "prompt": """Voce e um assistente juridico especializado em auditoria de acordaos.
Audite o acordao abaixo verificando:
1. A ementa corresponde ao dispositivo?
2. A fundamentacao e suficiente e coerente?
3. Ha contradicao entre voto e dispositivo?
4. Os precedentes citados sao aplicaveis?
5. Ha vicio de motivacao?
6. A decisao respeita a jurisprudencia dominante?

ACORDAO: {acordao}

Responda com: APROVADO, RESSALVAS ou REPROVADO, com justificativa para cada item.""",
    },
    "pesquisa_teses": {
        "nome": "Pesquisa de Teses Repetitivas",
        "descricao": "Pesquisa teses repetitivas e recursos repetitivos",
        "prompt": """Voce e um assistente juridico especializado em teses repetitivas.
Para o tema abaixo, identifique:
1. Recursos repetitivos julgados pelo STJ/STF
2. Temas de repercussao geral do STF
3. Sumulas aplicaveis
4. A tese firmada em cada caso
5. A situacao atual (vigente, superada, modificada)

TEMA: {tema}

Responda de forma estruturada com numero do processo, orgao, data e tese.""",
    },
    "leitura_profunda": {
        "nome": "Leitura Profunda",
        "descricao": "Metodo de leitura aprofundada de documentos juridicos",
        "prompt": """Voce e um assistente juridico aplicando o metodo de Leitura Profunda.
Leia o documento abaixo e responda:
1. QUAL E O PEDIDO/QUESTAO PRINCIPAL?
2. QUAIS SAO OS FATOS RELEVANTES?
3. QUAIS SAO OS FUNDAMENTOS JURIDICOS?
4. QUAL E A DECISAO/CONCLUSAO?
5. QUAIS SAO OS PONTOS CONTROVERTIDOS?
6. O QUE FALTA SER ESCLARECIDO?
7. QUAL E A RELEVANCIA PARA O CASO EM ANALISE?

DOCUMENTO: {documento}

Responda de forma estruturada e objetiva.""",
    },
    "contraditorio_simulado": {
        "nome": "Contraditorio Simulado",
        "descricao": "Simula contraditorio para testar teses",
        "prompt": """Voce e um assistente juridico aplicando o metodo de Contraditorio Simulado.
Dada a tese abaixo, simule o contraditorio:
1. ARGUMENTOS A FAVOR DA TESE
2. ARGUMENTOS CONTRA A TESE (o que o outro lado diria)
3. PRECEDENTES QUE APOIAM
4. PRECEDENTES QUE CONTRARIAM
5. PONTOS FRACOS DA TESE
6. SUGESTOES DE REFORCO

TESE: {tese}

Responda de forma estruturada.""",
    },
}


def get_prompt(nome: str, **kwargs) -> str:
    """Retorna o prompt formatado com os parametros fornecidos."""
    if nome not in PROMPTS:
        return None
    template = PROMPTS[nome]["prompt"]
    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"Parametro faltando: {e}"


def list_prompts() -> list:
    """Lista todos os prompts disponiveis."""
    return [
        {"id": k, "nome": v["nome"], "descricao": v["descricao"]}
        for k, v in PROMPTS.items()
    ]


def get_prompt_info(nome: str) -> dict:
    """Retorna informacoes sobre um prompt."""
    if nome not in PROMPTS:
        return None
    return {
        "id": nome,
        "nome": PROMPTS[nome]["nome"],
        "descricao": PROMPTS[nome]["descricao"],
    }
