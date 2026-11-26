"""Busca vetorial (semantica) de acordaos usando ChromaDB + sentence-transformers.

Permite indexar acordaos e fazer busca por similaridade semantica,
complementando a busca full-text (FTS5) existente.
"""

import os
import sys
import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

sys.path.insert(0, os.path.dirname(__file__))
from db import get_acordao, count_acordaos

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_client = None
_collection = None
_model = None


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
    return _client


def _get_collection():
    global _collection
    if _collection is None:
        client = _get_client()
        try:
            _collection = client.get_collection(name="acordaos")
        except Exception:
            _collection = client.create_collection(name="acordaos")
    return _collection


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _texto_para_buscar(acordao: dict) -> str:
    """Monta o texto que sera embedado (ementa + relatorio + voto + dispositivo)."""
    partes = []
    for campo in ["ementa", "relatorio", "voto", "dispositivo"]:
        v = acordao.get(campo) or ""
        if v and v != "Não encontrada" and v != "Não identificado":
            partes.append(v)
    return " ".join(partes)


def indexar_todos():
    """Indexa todos os acordaos do SQLite no ChromaDB."""
    total = count_acordaos()
    if total == 0:
        return {"indexados": 0, "mensagem": "Nenhum acordo no banco SQLite"}

    collection = _get_collection()
    # Verifica se ja tem algo indexado
    try:
        ja_indexados = collection.count()
    except Exception:
        ja_indexados = 0

    if ja_indexados >= total:
        return {"indexados": ja_indexados, "mensagem": "Ja indexados"}

    model = _get_model()
    documentos = []
    metadados = []
    ids = []

    for i in range(1, total + 1):
        a = get_acordao(i)
        if not a:
            continue
        texto = _texto_para_buscar(a)
        if not texto.strip():
            continue
        documentos.append(texto)
        metadados.append(
            {
                "id": a["id"],
                "tribunal": a.get("tribunal", ""),
                "numero": a.get("numero_processo", ""),
                "relator": a.get("relator", ""),
                "area": a.get("area", ""),
                "tema": a.get("tema", ""),
                "data_julgamento": a.get("data_julgamento", ""),
            }
        )
        ids.append(f"acordao_{a['id']}")

    if not documentos:
        return {"indexados": 0, "mensagem": "Nenhum texto valido para indexar"}

    embeddings = model.encode(documentos, show_progress_bar=True)

    collection.add(
        documents=documentos,
        metadatas=metadados,
        ids=ids,
        embeddings=embeddings.tolist(),
    )

    return {
        "indexados": len(documentos),
        "mensagem": f"{len(documentos)} acordaos indexados no ChromaDB",
    }


def busca_semantica(
    query: str, limite: int = 10, tribunal: str = None, area: str = None
):
    """Faz busca semantica por similaridade de embeddings."""
    collection = _get_collection()
    model = _get_model()

    query_embedding = model.encode([query]).tolist()

    filtros = {}
    if tribunal:
        filtros["tribunal"] = tribunal
    if area:
        filtros["area"] = area

    try:
        resultados = collection.query(
            query_embeddings=query_embedding,
            n_results=min(limite, 50),
            where=filtros if filtros else None,
        )
    except Exception:
        resultados = collection.query(
            query_embeddings=query_embedding,
            n_results=min(limite, 50),
        )

    docs = resultados.get("documents", [[]])[0]
    dists = resultados.get("distances", [[]])[0]
    ids = resultados.get("ids", [[]])[0]

    resultados_formatados = []
    for i, doc in enumerate(docs):
        distancia = dists[i] if i < len(dists) else 0
        # Converte distancia (L2) para score de similaridade (0 a 1)
        similaridade = round(max(0, 1 - distancia / 20), 3)

        # Extrai o ID numerico do ID do ChromaDB (ex: "acordao_1" -> "1")
        id_acordao = None
        if ids and i < len(ids):
            id_str = ids[i]
            if id_str.startswith("acordao_"):
                id_acordao = id_str.replace("acordao_", "")

        # Busca metadados completos no SQLite
        tribunal = ""
        numero = ""
        relator = ""
        area = ""
        tema = ""
        data_julgamento = ""
        if id_acordao:
            try:
                a = get_acordao(int(id_acordao))
                if a:
                    tribunal = a.get("tribunal", "") or ""
                    numero = a.get("numero_processo", "") or ""
                    relator = a.get("relator", "") or ""
                    area = a.get("area", "") or ""
                    tema = a.get("tema", "") or ""
                    data_julgamento = a.get("data_julgamento", "") or ""
            except Exception:
                pass

        resultados_formatados.append(
            {
                "id": id_acordao or ids[i] if ids else i,
                "tribunal": tribunal,
                "numero": numero,
                "relator": relator,
                "area": area,
                "tema": tema,
                "data_julgamento": data_julgamento,
                "trecho": doc[:300] + ("..." if len(doc) > 300 else ""),
                "similaridade": similaridade,
            }
        )

    # Ordena por similaridade decrescente
    resultados_formatados.sort(key=lambda x: x["similaridade"], reverse=True)

    return {
        "query": query,
        "total": len(resultados_formatados),
        "resultados": resultados_formatados,
    }


def estatisticas():
    """Retorna estatísticas da base vetorial."""
    try:
        collection = _get_collection()
        return {"total_indexados": collection.count()}
    except Exception:
        return {"total_indexados": 0}


if __name__ == "__main__":
    resultado = indexar_todos()
    print(resultado)
    stats = estatisticas()
    print(stats)
