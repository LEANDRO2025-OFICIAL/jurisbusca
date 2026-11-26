"""Parser de acordaos - extrai campos estruturados de PDFs.

Funcao principal: parse_acordao_pdf(caminho_pdf)
Retorna dicionario com:
- ementa
- relatorio
- voto
- dispositivo
- tribunal (detectado)
- numero (detectado)
- relator (detectado)
- data (detectada)
- texto_inteiro (texto completo extraido)
"""

import re
import os
import sys
import fitz  # PyMuPDF


def extrair_texto_pdf(caminho_pdf: str) -> str:
    """Extrai todo o texto de um PDF usando PyMuPDF."""
    texto = ""
    try:
        doc = fitz.open(caminho_pdf)
        for pagina in doc:
            texto += pagina.get_text() + "\n"
        doc.close()
    except Exception as e:
        texto = f"ERRO ao extrair PDF: {e}"
    return texto


def limpar_texto(texto: str) -> str:
    """Remove espacos duplicados, quebras de linha excessivas e caracteres inuteis."""
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = texto.strip()
    return texto


def detectar_tribunal(texto: str) -> str:
    """Tenta detectar o tribunal com base no texto."""
    texto_upper = texto.upper()
    if "SUPERIOR TRIBUNAL DE JUSTICA" in texto_upper or "STJ" in texto_upper:
        return "STJ"
    if "SUPREMO TRIBUNAL FEDERAL" in texto_upper or "STF" in texto_upper:
        return "STF"
    if "TRIBUNAL SUPERIOR DO TRABALHO" in texto_upper or "TST" in texto_upper:
        return "TST"
    if "TRIBUNAL DE JUSTICA" in texto_upper:
        # Tenta extrair a UF
        m = re.search(r"TRIBUNAL DE JUSTICA\s+DO\s+([A-ZÁÊÇÕ\s]+)", texto_upper)
        if m:
            return f"TJ {m.group(1).strip()}"
        return "TJ"
    if "TRIBUNAL REGIONAL FEDERAL" in texto_upper or "TRF" in texto_upper:
        return "TRF"
    if "TRIBUNAL DE CONTAS DA UNIAO" in texto_upper or "TCU" in texto_upper:
        return "TCU"
    if "TRIBUNAL DE CONTAS" in texto_upper:
        return "TCE"
    return "Não identificado"


def detectar_numero_processo(texto: str) -> str:
    """Detecta numero de processo no formato CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO."""
    padrao = r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
    m = re.search(padrao, texto)
    if m:
        return m.group(0)
    # Formatos simplificados: NNNNNNN-DD/AAAA ou NNNNNNN/AAAA
    padrao2 = r"\d{5,7}-\d{2}/\d{4}"
    m2 = re.search(padrao2, texto)
    if m2:
        return m2.group(0)
    padrao3 = r"\d{5,7}/\d{4}"
    m3 = re.search(padrao3, texto)
    if m3:
        return m3.group(0)
    padrao5 = r"\d{5,7}/[A-Z]{2}"
    m5 = re.search(padrao5, texto)
    if m5:
        return m5.group(0)
    # Qualquer sequencia que pareça numero de processo
    padrao4 = r"\d{5,7}[-./]\d{2}[-./]\d{4}"
    m4 = re.search(padrao4, texto)
    if m4:
        return m4.group(0)
    return "Não identificado"


def detectar_relator(texto: str) -> str:
    """Tenta detectar o relator com base em palavras-chave."""
    padroes = [
        r"(?:Relator|Relatora|Rel\.)\s*:\s*([^\n,;]+)",
        r"(?:Relator|Relatora|Rel\.)\s+([A-ZÁÊÇÕ][a-zãõçáêôúà]+(?:\s+[A-ZÁÊÇÕ][a-zãõçáêôúà]+){1,4})",
        r"(?:Min(?:istro|istra)\.?\s+)([A-ZÁÊÇÕ][a-zãõçáêôúà]+(?:\s+[A-ZÁÊÇÕ][a-zãõçáêôúà]+){1,4})",
        r"(?:Des(?:embargador|embargadora)\.?\s+)([A-ZÁÊÇÕ][a-zãõçáêôúà]+(?:\s+[A-ZÁÊÇÕ][a-zãõçáêôúà]+){1,4})",
    ]
    for padrao in padroes:
        m = re.search(padrao, texto, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return "Não identificado"


def detectar_data(texto: str) -> str:
    """Tenta detectar a data do julgamento."""
    padroes_numericos = [
        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}\.\d{2}\.\d{4}",
        r"\d{4}-\d{2}-\d{2}",
    ]
    for padrao in padroes_numericos:
        m = re.search(padrao, texto)
        if m:
            return m.group(0)

    # Formato extenso: "15 de março de 2024"
    meses = r"janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"
    padrao_extenso = rf"\d{{1,2}} de {meses} de \d{{4}}"
    m = re.search(padrao_extenso, texto, re.IGNORECASE)
    if m:
        return m.group(0)

    return "Não identificada"


def extrair_secao(texto: str, secao: str) -> str:
    """Extrai uma secao especifica do acordo (ementa, relatorio, voto, dispositivo)."""
    texto_upper = texto.upper()

    # Padroes para inicio de secao
    padroes_inicio = {
        "ementa": [
            r"EMENTA\s*[:-]?\s*",
            r"MENTA\s*[:-]?\s*",
        ],
        "relatorio": [
            r"RELAT[OÓ]RIO\s*[:-]?\s*",
            r"RELAT[OÓ]RI\s*[:-]?\s*",
        ],
        "voto": [
            r"VOTO\s*[:-]?\s*",
            r"VOT\s*[:-]?\s*",
        ],
        "dispositivo": [
            r"DISPOSITIVO\s*[:-]?\s*",
            r"DISPOSITIV\s*[:-]?\s*",
        ],
    }

    padroes_fim = {
        "ementa": [
            r"RELAT[OÓ]RIO\s*[:-]?",
            r"VOTO\s*[:-]?",
            r"DISPOSITIVO\s*[:-]?",
            r"ACORDAM\s*[:-]?",
        ],
        "relatorio": [
            r"VOTO\s*[:-]?",
            r"DISPOSITIVO\s*[:-]?",
            r"ACORDAM\s*[:-]?",
            r"EMENTA\s*[:-]?",
        ],
        "voto": [
            r"DISPOSITIVO\s*[:-]?",
            r"ACORDAM\s*[:-]?",
            r"JULGAMENTO\s*[:-]?",
        ],
        "dispositivo": [
            r"PUBL[IÍ]CA[ÇC][AÀ]O\s*[:-]?",
            r"INTIMA[ÇC][AÀ]O\s*[:-]?",
            r"(?:São Paulo|Rio de Janeiro|Belo Horizonte|Salvador|Brasília|Curitiba|Fortaleza|Recife|Porto Alegre|Manaus|Belém|Goiânia|Campinas|São Luís|Maceió|Natal|João Pessoa|Teresina|Aracaju|Florianópolis|Vitória|Cuiabá|Campo Grande|Boa Vista|Rio Branco|Macapá|Palmas),?\s+\d{1,2} de [a-zç]+ de \d{4}",
            r"\d{1,2} de [a-zç]+ de \d{4}",
            r"$",
        ],
    }

    inicio_patterns = padroes_inicio.get(secao, [])
    fim_patterns = padroes_fim.get(secao, [])

    pos_inicio = -1
    for p in inicio_patterns:
        m = re.search(p, texto_upper)
        if m:
            pos_inicio = m.end()
            break

    if pos_inicio == -1:
        return "Não encontrada"

    # Proxima secao depois do inicio
    pos_fim = len(texto)
    for p in fim_patterns:
        m = re.search(p, texto_upper[pos_inicio:])
        if m:
            pos_fim = pos_inicio + m.start()
            break

    secao_texto = texto[pos_inicio:pos_fim]
    return limpar_texto(secao_texto)


def parse_acordao_pdf(caminho_pdf: str) -> dict:
    """Extrai campos estruturados de um PDF de acordo.

    Retorna dicionario com todos os campos detectados.
    """
    texto_bruto = extrair_texto_pdf(caminho_pdf)
    texto_limpo = limpar_texto(texto_bruto)

    return {
        "arquivo": os.path.basename(caminho_pdf),
        "caminho": caminho_pdf,
        "tribunal": detectar_tribunal(texto_limpo),
        "numero_processo": detectar_numero_processo(texto_limpo),
        "relator": detectar_relator(texto_limpo),
        "data_julgamento": detectar_data(texto_limpo),
        "ementa": extrair_secao(texto_limpo, "ementa"),
        "relatorio": extrair_secao(texto_limpo, "relatorio"),
        "voto": extrair_secao(texto_limpo, "voto"),
        "dispositivo": extrair_secao(texto_limpo, "dispositivo"),
        "texto_inteiro": texto_limpo,
        "tamanho_caracteres": len(texto_limpo),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python parser_acordao.py <caminho_pdf>")
        sys.exit(1)
    resultado = parse_acordao_pdf(sys.argv[1])
    print(f"Arquivo: {resultado['arquivo']}")
    print(f"Tribunal: {resultado['tribunal']}")
    print(f"Numero: {resultado['numero_processo']}")
    print(f"Relator: {resultado['relator']}")
    print(f"Data: {resultado['data_julgamento']}")
    print(f"Ementa: {resultado['ementa'][:200]}...")
    print(f"Relatorio: {resultado['relatorio'][:200]}...")
    print(f"Voto: {resultado['voto'][:200]}...")
    print(f"Dispositivo: {resultado['dispositivo'][:200]}...")
    print(f"Tamanho: {resultado['tamanho_caracteres']} caracteres")
