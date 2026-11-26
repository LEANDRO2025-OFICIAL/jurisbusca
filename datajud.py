"""Integracao com CNJ DataJud - API publica do Conselho Nacional de Justica.

A API DataJud (https://api-publica.datajud.cnj.jus.br/) fornece acesso a
milhoes de acórdãos, processos e metadados de todos os tribunais brasileiros.

Endpoint base: https://api-publica.datajud.cnj.jus.br/api_publica/{tribunal}/_search
Chave publica: APIKey cnj-datajud (para uso publico)
"""

import requests
import json

DATAJUD_BASE = "https://api-publica.datajud.cnj.jus.br"
DATAJUD_APIKEY = "APIKey cnj-datajud"

# NOTA: A API DataJud CNJ requer autenticacao. A chave publica 'cnj-datajud'
# nao funciona em todos os endpoints. Se receber 401, forneca sua propria chave API.
# Documentacao: https://www.cnj.jus.br/sistemas/datajud/

# Mapeamento de sigla do tribunal para codigo DataJud
TRIBUNAL_CODIGOS = {
    "STF": "stf",
    "STJ": "stj",
    "TST": "tst",
    "TJSP": "tjsp",
    "TJMG": "tjmg",
    "TJRJ": "tjrj",
    "TJRS": "tjrs",
    "TJPR": "tjpr",
    "TJSC": "tjsc",
    "TJBA": "tjba",
    "TJPE": "tjpe",
    "TJCE": "tjce",
    "TJGO": "tjgo",
    "TJMT": "tjmt",
    "TJMS": "tjms",
    "TJPA": "tjpa",
    "TJAM": "tjam",
    "TJRN": "tjrn",
    "TJAL": "tjal",
    "TJSE": "tjse",
    "TJPI": "tjpi",
    "TJMA": "tjma",
    "TJTO": "tjto",
    "TJRO": "tjro",
    "TJAC": "tjac",
    "TJAP": "tjap",
    "TJRR": "tjrr",
    "TJDF": "tjdf",
    "TRF1": "trf1",
    "TRF2": "trf2",
    "TRF3": "trf3",
    "TRF4": "trf4",
    "TRF5": "trf5",
    "TRF6": "trf6",
    "TCU": "tcu",
    **{f"TRT{i}": f"trt{i}" for i in range(1, 25)},
}

HEADERS = {
    "Authorization": DATAJUD_APIKEY,
    "Content-Type": "application/json",
}

TIMEOUT = 30


def buscar_datajud(
    tribunal: str,
    query: str,
    limite: int = 20,
    pagina: int = 0,
) -> list:
    """Busca processos/acordaos no CNJ DataJud.

    Args:
        tribunal: sigla do tribunal (ex: 'STJ', 'TJSP', 'TRF4')
        query: termo de busca
        limite: numero maximo de resultados (1-50)
        pagina: pagina (0-based)

    Returns:
        Lista de dicionarios com metadados dos processos.
    """
    codigo = TRIBUNAL_CODIGOS.get(tribunal, tribunal.lower())
    url = f"{DATAJUD_BASE}/api_publica/{codigo}/_search"

    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "ementa",
                    "numeroProcesso",
                    "classe.nome",
                    "assunto.nome",
                    "orgaoJulgador.nome",
                ],
                "type": "best_fields",
            }
        },
        "size": min(limite, 50),
        "from": pagina * limite,
        "sort": [{"dataAjuizamento": {"order": "desc"}}],
    }

    try:
        resp = requests.post(url, headers=HEADERS, json=body, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            hits = data.get("hits", {}).get("hits", [])
            resultados = []
            for hit in hits:
                src = hit.get("_source", {})
                resultados.append(
                    {
                        "id": hit.get("_id", ""),
                        "tribunal": src.get("tribunal", tribunal),
                        "numero_processo": src.get("numeroProcesso", ""),
                        "classe": src.get("classe", {}).get("nome", "")
                        if isinstance(src.get("classe"), dict)
                        else src.get("classe", ""),
                        "assunto": src.get("assunto", {}).get("nome", "")
                        if isinstance(src.get("assunto"), dict)
                        else src.get("assunto", ""),
                        "orgao_julgador": src.get("orgaoJulgador", {}).get("nome", "")
                        if isinstance(src.get("orgaoJulgador"), dict)
                        else src.get("orgaoJulgador", ""),
                        "data_ajuizamento": src.get("dataAjuizamento", ""),
                        "data_julgamento": src.get(
                            "dataJulgamento", src.get("dataAjuizamento", "")
                        ),
                        "ementa": src.get("ementa", ""),
                        "situacao": src.get("situacao", ""),
                        "grau": src.get("grau", ""),
                        "url": f"{DATAJUD_BASE}/api_publica/{codigo}/_doc/{hit.get('_id', '')}",
                    }
                )
            return resultados
    except Exception as e:
        print(f"Erro DataJud {tribunal}: {e}")
    return []


def buscar_todos_tribunais_datajud(query: str, limite_por_tribunal: int = 3) -> list:
    """Busca em todos os tribunais disponiveis no DataJud."""
    todos = []
    for tribunal in TRIBUNAL_CODIGOS:
        try:
            res = buscar_datajud(tribunal, query, limite=limite_por_tribunal)
            todos.extend(res)
        except Exception:
            continue
    return todos


def listar_tribunais_datajud() -> list:
    """Retorna lista de tribunais disponiveis no DataJud."""
    return sorted(set(TRIBUNAL_CODIGOS.values()))


def popular_banco_com_datajud(
    query: str, tribunal: str = "STJ", limite: int = 20
) -> list:
    """Busca no DataJud e retorna no formato do JurisBusca para insercao no banco."""
    resultados = buscar_datajud(tribunal, query, limite=limite)
    formatados = []
    for r in resultados:
        formatados.append(
            {
                "tribunal": r.get("tribunal", tribunal),
                "numero": r.get("numero_processo", ""),
                "data_julgamento": r.get("data_julgamento", ""),
                "relator": r.get("orgao_julgador", ""),
                "ementa": r.get("ementa", ""),
                "relatorio": "",
                "voto": "",
                "dispositivo": "",
                "area": "",
                "tema": r.get("assunto", ""),
                "url_origem": r.get("url", ""),
                "pdf_url": None,
            }
        )
    return formatados


if __name__ == "__main__":
    print("Tribunais DataJud:", len(listar_tribunais_datajud()))
    print(listar_tribunais_datajud()[:10])
    # Teste
    r = buscar_datajud("STJ", "dano moral", limite=3)
    print(f"Resultados STJ 'dano moral': {len(r)}")
    for x in r[:3]:
        print(f"  {x['tribunal']} | {x['numero_processo']} | {x['ementa'][:80]}")
