"""Módulo RAG (Retrieval-Augmented Generation) para JurisBusca.

Combina busca semântica (ChromaDB) com geração de resposta em linguagem natural,
citando as fontes (acórdãos) encontradas.

Funciona de duas formas:
1. Gera um prompt RAG estruturado para ser usado com qualquer LLM (local ou remoto).
2. (Opcional) Se houver um modelo LLM local disponível, gera a resposta diretamente.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from busca_vetorial import busca_semantica, estatisticas as estatisticas_vetor


def montar_contexto_rag(resultados_busca: list) -> str:
    """Monta o contexto a partir dos resultados da busca semântica."""
    if not resultados_busca:
        return "Nenhum acórdão relevante encontrado na base."

    partes = []
    for i, r in enumerate(resultados_busca, 1):
        parte = (
            f"[Fonte {i}] "
            f"Tribunal: {r.get('tribunal', 'N/A')}\n"
            f"Processo: {r.get('numero', 'N/A')}\n"
            f"Relator: {r.get('relator', 'N/A')}\n"
            f"Área: {r.get('area', 'N/A')}\n"
            f"Similaridade: {r.get('similaridade', 0)}\n"
            f"Trecho: {r.get('trecho', '')}\n"
        )
        partes.append(parte)
    return "\n".join(partes)


def gerar_prompt_rag(pergunta: str, resultados_busca: list) -> str:
    """Gera um prompt RAG completo para um LLM."""
    contexto = montar_contexto_rag(resultados_busca)

    prompt = f"""Você é um assistente jurídico especializado em pesquisa de jurisprudência.

Responda à pergunta do usuário com base APENAS nos acórdãos fornecidos abaixo.
Cite as fontes usando o formato [Fonte N] onde N é o número da fonte.
Se a informação não estiver nos acórdãos, diga que não há informação suficiente na base.

PERGUNTA DO USUÁRIO:
{pergunta}

ACÓRDÃOS ENCONTRADOS (FONTES):
{contexto}

INSTRUÇÕES:
1. Responda em português do Brasil.
2. Cite sempre a fonte [Fonte N] ao afirmar algo.
3. Se houver divergência entre tribunais, mencione.
4. Mantenha a resposta objetiva e fundamentada.
5. Não invente processos, valores ou datas que não estejam nos textos fornecidos."""

    return prompt


def buscar_e_montar_rag(
    pergunta: str,
    limite: int = 5,
    tribunal: str = None,
    area: str = None,
) -> dict:
    """Executa busca semântica e monta o contexto RAG."""
    resultado_busca = busca_semantica(
        query=pergunta,
        limite=limite,
        tribunal=tribunal,
        area=area,
    )

    prompt = gerar_prompt_rag(pergunta, resultado_busca["resultados"])

    return {
        "pergunta": pergunta,
        "total_encontrados": resultado_busca["total"],
        "resultados": resultado_busca["resultados"],
        "prompt_rag": prompt,
        "contexto": montar_contexto_rag(resultado_busca["resultados"]),
    }


def estatisticas():
    return estatisticas_vetor()


if __name__ == "__main__":
    # Teste rápido
    r = buscar_e_montar_rag(
        "dano moral inscrição indevida cadastro inadimplentes", limite=3
    )
    print("Pergunta:", r["pergunta"])
    print("Total encontrados:", r["total_encontrados"])
    print("\n--- PROMPT RAG ---\n")
    print(r["prompt_rag"][:1500])
    print("...")
