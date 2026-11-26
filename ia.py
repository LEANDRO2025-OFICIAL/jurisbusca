"""Modulo de servicos de IA - agregado do curso 'Desbloqueando o uso da IA na Rotina Juridica'.

Metodos do curso:
- Leitura Profunda
- Contraditorio Simulado
- Triagem de E-mail
- Organizador de Autos
- OCR de Processo Digitalizado
- Revisao da Peca

Agentes MCP do curso:
- Jurisprudencia e Citacoes (sumulas e temas do CNJ)
- Julgados do STJ (355 mil acordaos)
- Intimacoes do DJEN (API publica do CNJ)
- Atualizacao Monetaria (correcao + juros)
- Decisoes do Juizo (decisoes por comarca/vara)
- Consulta de CNPJ (Receita Federal)
- Taxas do BACEN
- Julgados do CARF (582 mil acordaos)
- Acordaos do TCU (528 mil acordaos + teses + sumulas)
- Acordaos dos TCEs e TCMs (31 tribunais)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from prompts import get_prompt, list_prompts

# Mapeamento de agentes MCP do curso para funcionalidades do JurisBusca
AGENTES_MCP = {
    "jurisprudencia_citacoes": {
        "nome": "Jurisprudencia e Citacoes",
        "descricao": "Diz quais sumulas e temas do CNJ se aplicam e confere citacoes",
        "funcionalidade": "conferencia_citacoes",
    },
    "julgados_stj": {
        "nome": "Julgados do STJ",
        "descricao": "Busca por tema nos 355 mil acordaos do STJ (fev/2016+)",
        "funcionalidade": "busca_jurisprudencia",
    },
    "intimacoes_djen": {
        "nome": "Intimacoes do DJEN",
        "descricao": "Busca intimacoes no DJEN (API publica do CNJ)",
        "funcionalidade": "intimacoes",
    },
    "atualizacao_monetaria": {
        "nome": "Atualizacao Monetaria",
        "descricao": "Atualiza valores com correcao monetaria e juros de mora",
        "funcionalidade": "atualizacao_monetaria",
    },
    "decisoes_juizo": {
        "nome": "Decisoes do Juizo",
        "descricao": "Mostra o que uma comarca/vara/juiz vem decidindo sobre um tema",
        "funcionalidade": "decisoes_juizo",
    },
    "consulta_cnpj": {
        "nome": "Consulta de CNPJ",
        "descricao": "Consulta CNPJ na base publica da Receita Federal",
        "funcionalidade": "consulta_cnpj",
    },
    "taxas_bacen": {
        "nome": "Taxas do BACEN",
        "descricao": "Taxas medias oficiais do BACEN (parametro STJ Tema 27)",
        "funcionalidade": "taxas_bacen",
    },
    "julgados_carf": {
        "nome": "Julgados do CARF",
        "descricao": "582 mil acordaos do CARF (contencioso tributario federal)",
        "funcionalidade": "busca_jurisprudencia",
    },
    "acordaos_tcu": {
        "nome": "Acordaos do TCU",
        "descricao": "528 mil acordaos do TCU + 17,7 mil teses + 294 sumulas",
        "funcionalidade": "busca_jurisprudencia",
    },
    "acordaos_tces": {
        "nome": "Acordaos dos TCEs e TCMs",
        "descricao": "31 tribunais de contas estaduais e municipais",
        "funcionalidade": "busca_jurisprudencia",
    },
}

# Metodos do curso (skills)
METODOS = {
    "leitura_profunda": {
        "nome": "Leitura Profunda",
        "descricao": "Metodo de leitura aprofundada de documentos juridicos",
        "prompt_id": "leitura_profunda",
    },
    "contraditorio_simulado": {
        "nome": "Contraditorio Simulado",
        "descricao": "Metodo de simulacao de contraditorio para testar teses",
        "prompt_id": "contraditorio_simulado",
    },
    "triagem_email": {
        "nome": "Triagem de E-mail",
        "descricao": "Metodo de triagem e organizacao de e-mails juridicos",
        "prompt_id": None,
    },
    "organizador_autos": {
        "nome": "Organizador de Autos",
        "descricao": "Metodo de organizacao de autos processuais",
        "prompt_id": None,
    },
    "ocr_processo": {
        "nome": "OCR de Processo Digitalizado",
        "descricao": "Metodo de OCR para processos digitalizados",
        "prompt_id": None,
    },
    "revisao_peca": {
        "nome": "Revisao da Peca",
        "descricao": "Metodo de revisao de pecas juridicas",
        "prompt_id": None,
    },
}


def analisar_acordao(acordao_texto: str) -> str:
    """Gera prompt para analise de acordao usando metodo de Leitura Profunda."""
    return get_prompt("analise_acordao", acordao=acordao_texto)


def conferir_citacoes(citacoes: str) -> str:
    """Gera prompt para conferencia de citacoes de jurisprudencia."""
    return get_prompt("conferencia_citacoes", citacoes=citacoes)


def extrair_argumentos(decisao_texto: str) -> str:
    """Gera prompt para extracao de argumentos e fundamentos."""
    return get_prompt("extrator_argumentos", decisao=decisao_texto)


def auditar_acordao(acordao_texto: str) -> str:
    """Gera prompt para auditoria de acordao."""
    return get_prompt("auditoria_acordao", acordao=acordao_texto)


def buscar_jurisprudencia(tema: str) -> str:
    """Gera prompt para busca de jurisprudencia por tema."""
    return get_prompt("busca_jurisprudencia", tema=tema)


def pesquisar_teses(tema: str) -> str:
    """Gera prompt para pesquisa de teses repetitivas."""
    return get_prompt("pesquisa_teses", tema=tema)


def leitura_profunda(documento: str) -> str:
    """Gera prompt para leitura profunda de documento juridico."""
    return get_prompt("leitura_profunda", documento=documento)


def contraditorio_simulado(tese: str) -> str:
    """Gera prompt para simulacao de contraditorio."""
    return get_prompt("contraditorio_simulado", tese=tese)


def listar_agentes_mcp() -> list:
    """Lista os agentes MCP do curso disponiveis."""
    return [
        {"id": k, "nome": v["nome"], "descricao": v["descricao"]}
        for k, v in AGENTES_MCP.items()
    ]


def listar_metodos() -> list:
    """Lista os metodos do curso disponiveis."""
    return [
        {"id": k, "nome": v["nome"], "descricao": v["descricao"]}
        for k, v in METODOS.items()
    ]


def get_agente_info(agente_id: str) -> dict:
    """Retorna informacoes sobre um agente MCP."""
    if agente_id not in AGENTES_MCP:
        return None
    return AGENTES_MCP[agente_id]
