"""API FastAPI para busca de jurisprudencia."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Query, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from db import init_db, search, get_acordao, count_acordaos, list_tribunais, list_areas
from prompts import list_prompts, get_prompt, get_prompt_info
from ia import (
    analisar_acordao,
    conferir_citacoes,
    extrair_argumentos,
    auditar_acordao,
    buscar_jurisprudencia,
    pesquisar_teses,
    leitura_profunda,
    contraditorio_simulado,
    listar_agentes_mcp,
    listar_metodos,
    get_agente_info,
)
from prompts import list_prompts, get_prompt, get_prompt_info
from ia import (
    analisar_acordao,
    conferir_citacoes,
    extrair_argumentos,
    auditar_acordao,
    buscar_jurisprudencia,
    pesquisar_teses,
    leitura_profunda,
    contraditorio_simulado,
    listar_agentes_mcp,
    listar_metodos,
    get_agente_info,
)
from parser_acordao import parse_acordao_pdf
import tempfile
from busca_vetorial import (
    indexar_todos,
    busca_semantica,
    estatisticas as estatisticas_vetor,
)
from rag import buscar_e_montar_rag, estatisticas as estatisticas_rag
from scrapers import buscar_todos
from dados import get_tribunais, get_areas, total_tribunais, total_areas

app = FastAPI(
    title="JurisBusca - Busca de Jurisprudencia + IA",
    description="Prototipo MVP de busca de jurisprudencia, acordaos, normas e servicos de IA juridica",
    version="0.2.0",
)

# Inicializa banco
init_db()

# Seed se vazio
from scraper import seed_db

seed_db()

# Inicializa indexacao vetorial
try:
    resultado_indexacao = indexar_todos()
    print("Indexacao vetorial:", resultado_indexacao)
except Exception as e:
    print("Aviso: indexacao vetorial falhou:", e)


@app.get("/", response_class=HTMLResponse)
def home():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, encoding="utf-8") as f:
            return f.read()
    return "<h1>JurisBusca</h1><p>Frontend nao encontrado.</p>"


@app.get("/api/search")
def api_search(
    q: str = Query(..., description="Termo de busca"),
    tribunal: str = Query(None, description="Filtrar por tribunal"),
    area: str = Query(None, description="Filtrar por area"),
    limit: int = Query(20, ge=1, le=100),
):
    results = search(q, tribunal=tribunal, area=area, limit=limit)
    return {
        "query": q,
        "total": len(results),
        "tribunais": list_tribunais(),
        "areas": list_areas(),
        "results": results,
    }


@app.get("/api/acordao/{acordao_id}")
def api_acordao(acordao_id: int):
    ac = get_acordao(acordao_id)
    if not ac:
        return JSONResponse({"error": "Não encontrado"}, status_code=404)
    return ac


@app.get("/api/stats")
def api_stats():
    return {
        "total_acordaos": count_acordaos(),
        "tribunais": list_tribunais(),
        "areas": list_areas(),
    }


@app.get("/api/tribunais")
def api_tribunais():
    return {"tribunais": list_tribunais()}


@app.get("/api/areas")
def api_areas():
    return {"areas": list_areas()}


@app.get("/api/tribunais-lista")
def api_tribunais_lista():
    return {"tribunais": get_tribunais(), "total": total_tribunais()}


@app.get("/api/areas-lista")
def api_areas_lista():
    return {"areas": get_areas(), "total": total_areas()}


# === ENDPOINT DE BUSCA VETORIAL ===


@app.get("/api/search-semantico")
def api_search_semantico(
    q: str = Query(..., description="Termo de busca semantica"),
    limite: int = Query(10, ge=1, le=50),
    tribunal: str = Query(None, description="Filtrar por tribunal"),
    area: str = Query(None, description="Filtrar por area"),
):
    return busca_semantica(q, limite=limite, tribunal=tribunal, area=area)


@app.get("/api/estatisticas-vetor")
def api_estatisticas_vetor():
    return estatisticas_vetor()


# === ENDPOINT RAG (Retrieval-Augmented Generation) ===


@app.get("/api/rag")
def api_rag(
    q: str = Query(..., description="Pergunta jurídica"),
    limite: int = Query(5, ge=1, le=20),
    tribunal: str = Query(None, description="Filtrar por tribunal"),
    area: str = Query(None, description="Filtrar por area"),
):
    return buscar_e_montar_rag(q, limite=limite, tribunal=tribunal, area=area)


# === ENDPOINT DE SCRAPERS (busca em múltiplos tribunais) ===


@app.get("/api/scraper/buscar-todos")
def api_scraper_buscar_todos(
    q: str = Query(..., description="Termo de busca"),
    limite_por_fonte: int = Query(5, ge=1, le=10),
):
    return {
        "query": q,
        "total": len(buscar_todos(q, limite_por_fonte=limite_por_fonte)),
        "resultados": buscar_todos(q, limite_por_fonte=limite_por_fonte),
    }


# === ENDPOINTS DE IA E PROMPTS (agregado do curso 'IA Juridico') ===


@app.get("/api/prompts")
def api_prompts():
    return {"prompts": list_prompts()}


@app.get("/api/prompt/{prompt_id}")
def api_prompt(prompt_id: str):
    info = get_prompt_info(prompt_id)
    if not info:
        return JSONResponse({"error": "Prompt nao encontrado"}, status_code=404)
    return info


@app.post("/api/prompt/{prompt_id}/format")
def api_prompt_format(prompt_id: str, params: dict):
    result = get_prompt(prompt_id, **params)
    if result is None:
        return JSONResponse(
            {"error": "Prompt nao encontrado ou parametros invalidos"}, status_code=404
        )
    return {"prompt_id": prompt_id, "prompt_formatado": result}


@app.get("/api/ia/analisar-acordao")
def api_ia_analisar(texto: str = Query(..., description="Texto do acordao")):
    return {"prompt": analisar_acordao(texto)}


@app.get("/api/ia/conferir-citacoes")
def api_ia_conferir(
    citacoes: str = Query(..., description="Citacoes de jurisprudencia"),
):
    return {"prompt": conferir_citacoes(citacoes)}


@app.get("/api/ia/extrair-argumentos")
def api_ia_extrair(decisao: str = Query(..., description="Texto da decisao")):
    return {"prompt": extrair_argumentos(decisao)}


@app.get("/api/ia/auditar-acordao")
def api_ia_auditar(texto: str = Query(..., description="Texto do acordao")):
    return {"prompt": auditar_acordao(texto)}


@app.get("/api/ia/buscar-jurisprudencia")
def api_ia_buscar(tema: str = Query(..., description="Tema ou tese")):
    return {"prompt": buscar_jurisprudencia(tema)}


@app.get("/api/ia/pesquisar-teses")
def api_ia_teses(tema: str = Query(..., description="Tema")):
    return {"prompt": pesquisar_teses(tema)}


@app.get("/api/ia/leitura-profunda")
def api_ia_leitura(documento: str = Query(..., description="Texto do documento")):
    return {"prompt": leitura_profunda(documento)}


@app.get("/api/ia/contraditorio-simulado")
def api_ia_contraditorio(tese: str = Query(..., description="Tese")):
    return {"prompt": contraditorio_simulado(tese)}


@app.get("/api/agentes-mcp")
def api_agentes_mcp():
    return {"agentes": listar_agentes_mcp()}


@app.get("/api/metodos")
def api_metodos():
    return {"metodos": listar_metodos()}


@app.get("/api/agente/{agente_id}")
def api_agente(agente_id: str):
    info = get_agente_info(agente_id)
    if not info:
        return JSONResponse({"error": "Agente nao encontrado"}, status_code=404)
    return info


# === ENDPOINT DE PARSER DE ACORDAO (PDF) ===


@app.post("/api/parser/upload")
def api_parser_upload(file: UploadFile = File(...)):
    """Faz upload de um PDF de acordo e extrai campos estruturados."""
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            {"error": "Apenas arquivos PDF sao aceitos"}, status_code=400
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        resultado = parse_acordao_pdf(tmp_path)
        os.unlink(tmp_path)

        return {
            "arquivo": file.filename,
            "tribunal": resultado["tribunal"],
            "numero_processo": resultado["numero_processo"],
            "relator": resultado["relator"],
            "data_julgamento": resultado["data_julgamento"],
            "ementa": resultado["ementa"],
            "relatorio": resultado["relatorio"],
            "voto": resultado["voto"],
            "dispositivo": resultado["dispositivo"],
            "tamanho_caracteres": resultado["tamanho_caracteres"],
        }
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao processar PDF: {str(e)}"}, status_code=500
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
