"""Scrapers adicionais para múltiplos tribunais e diários oficiais.

Cada função recebe um termo de busca e retorna uma lista de dicionários com:
- tribunal: nome do tribunal
- numero: número do processo (se houver)
- ementa: trecho da ementa
- data: data do julgamento/publicação
- url: URL da fonte
- fonte: nome da fonte (ex: 'TJSP', 'DOU', 'TCE-SP')

Nota: Muitos portais de tribunais exigem login, CAPTCHA ou têm proteção anti-bot.
Os scrapers abaixo tentam acessar páginas públicas e tratam falhas graciosamente.
"""

import requests
from bs4 import BeautifulSoup
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

TIMEOUT = 15


def _requisitar(url: str, params: dict = None) -> str:
    """Faz requisição HTTP e retorna o texto HTML, ou string vazia em caso de falha."""
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return ""


def _limpar_texto(texto: str) -> str:
    """Remove espaços e quebras excessivas."""
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def buscar_tjsp(termo: str, limite: int = 10) -> list:
    """Busca jurisprudência no TJSP (Tribunal de Justiça de São Paulo).

    O TJSP possui consulta pública de jurisprudência, mas pode exigir
    sessão ou CAPTCHA. Este scraper tenta acessar a página pública.
    """
    resultados = []
    url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
    try:
        html = _requisitar(
            url,
            params={
                "tipoPesquisa": "ementa",
                "pesquisaLivre": termo,
                "pagina": 1,
            },
        )
        if not html:
            return resultados
        soup = BeautifulSoup(html, "html.parser")
        # Cada resultado é uma linha na tabela
        linhas = soup.select("tr.fundoClaro, tr.fundoEscuro")
        for linha in linhas[:limite]:
            cols = linha.find_all("td")
            if len(cols) >= 3:
                numero = _limpar_texto(cols[0].get_text())
                ementa = _limpar_texto(cols[2].get_text())
                if ementa:
                    resultados.append(
                        {
                            "tribunal": "TJSP",
                            "numero": numero,
                            "ementa": ementa,
                            "data": "",
                            "url": url,
                            "fonte": "TJSP",
                        }
                    )
    except Exception:
        pass
    return resultados


def buscar_tst(termo: str, limite: int = 10) -> list:
    """Busca jurisprudência no TST (Tribunal Superior do Trabalho)."""
    resultados = []
    url = "https://jurisprudencia.tst.jus.br/search"
    try:
        html = _requisitar(url, params={"q": termo})
        if not html:
            return resultados
        soup = BeautifulSoup(html, "html.parser")
        # Tenta extrair resultados genéricos
        items = soup.select(".resultado, .item, .processo")[:limite]
        if not items:
            # Fallback: pega links que contenham número de processo
            links = soup.find_all("a", href=True)
            for link in links[:limite]:
                texto = _limpar_texto(link.get_text())
                if re.search(r"\d{7}-\d{2}", texto):
                    resultados.append(
                        {
                            "tribunal": "TST",
                            "numero": texto,
                            "ementa": "",
                            "data": "",
                            "url": link["href"],
                            "fonte": "TST",
                        }
                    )
        else:
            for item in items:
                texto = _limpar_texto(item.get_text())
                resultados.append(
                    {
                        "tribunal": "TST",
                        "numero": "",
                        "ementa": texto[:500],
                        "data": "",
                        "url": url,
                        "fonte": "TST",
                    }
                )
    except Exception:
        pass
    return resultados


def buscar_dou(termo: str, limite: int = 10) -> list:
    """Busca no Diário Oficial da União (DOU) via portal.gov.br."""
    resultados = []
    url = "https://www.in.gov.br/web/rest/pesquisa"
    try:
        html = _requisitar(
            url,
            params={
                "q": termo,
                "sortType": "relevance",
                "page": 1,
            },
        )
        if not html:
            return resultados
        # Tenta parsear como JSON (API do DOU)
        try:
            import json

            data = html if isinstance(html, dict) else __import__("json").loads(html)
            itens = (
                data.get("resultados", [])[:limite] if isinstance(data, dict) else []
            )
            for item in itens:
                resultados.append(
                    {
                        "tribunal": "DOU",
                        "numero": item.get("numero", ""),
                        "ementa": _limpar_texto(item.get("ementa", ""))[:500],
                        "data": item.get("data", ""),
                        "url": item.get("url", url),
                        "fonte": "DOU",
                    }
                )
        except Exception:
            # Se não for JSON, tenta HTML
            soup = BeautifulSoup(html, "html.parser")
            items = soup.select(".resultado, .item, article")[:limite]
            for item in items:
                texto = _limpar_texto(item.get_text())
                if texto:
                    resultados.append(
                        {
                            "tribunal": "DOU",
                            "numero": "",
                            "ementa": texto[:500],
                            "data": "",
                            "url": url,
                            "fonte": "DOU",
                        }
                    )
    except Exception:
        pass
    return resultados


def buscar_tce_sp(termo: str, limite: int = 10) -> list:
    """Busca acórdãos no TCE-SP (Tribunal de Contas do Estado de São Paulo)."""
    resultados = []
    url = "https://www.tce.sp.gov.br/acordaos"
    try:
        html = _requisitar(url, params={"busca": termo})
        if not html:
            return resultados
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".acordao, .resultado, .item")[:limite]
        for item in items:
            texto = _limpar_texto(item.get_text())
            if texto:
                resultados.append(
                    {
                        "tribunal": "TCE-SP",
                        "numero": "",
                        "ementa": texto[:500],
                        "data": "",
                        "url": url,
                        "fonte": "TCE-SP",
                    }
                )
    except Exception:
        pass
    return resultados


def buscar_todos(termo: str, limite_por_fonte: int = 5) -> list:
    """Busca em todas as fontes disponíveis e consolida os resultados."""
    todos = []

    # Tenta cada fonte
    fontes = [
        ("TJSP", buscar_tjsp),
        ("TST", buscar_tst),
        ("DOU", buscar_dou),
        ("TCE-SP", buscar_tce_sp),
    ]

    for nome, funcao in fontes:
        try:
            res = funcao(termo, limite=limite_por_fonte)
            todos.extend(res)
        except Exception:
            continue

    return todos


if __name__ == "__main__":
    import sys

    termo = sys.argv[1] if len(sys.argv) > 1 else "dano moral"
    resultados = buscar_todos(termo)
    print(f"Busca por '{termo}': {len(resultados)} resultados")
    for r in resultados[:10]:
        print(f"  [{r['fonte']}] {r['tribunal']} | {r['numero']} | {r['ementa'][:100]}")
