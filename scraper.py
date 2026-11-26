"""Scraper de jurisprudencia - prototipo MVP."""

import requests
from bs4 import BeautifulSoup
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from db import insert_acordao

STJ_SEARCH_URL = "https://www.stj.jus.br/SCON/pesquisar.jsp"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Dados de exemplo (seed) para demonstrar o prototipo
SEED_ACORDAOS = [
    {
        "tribunal": "STJ",
        "numero": "REsp 1.234.567/SP",
        "data_julgamento": "2024-03-15",
        "relator": "Min. Nancy Andrighi",
        "ementa": "DIREITO CIVIL. RESPONSABILIDADE CIVIL. DANO MORAL. INSCRIÇÃO INDEVIDA EM CADASTRO DE INADIMPLENTES. A inscrição indevida em cadastro de inadimplentes gera dano moral presumido, independentemente de prova do prejuízo. Precedentes. Recurso especial provido.",
        "relatorio": "Trata-se de recurso especial interposto contra acórdão do TJSP que julgou improcedente ação de indenização por dano moral...",
        "voto": "Voto do relator: a inscrição indevida gera dano moral presumido...",
        "dispositivo": "Recurso especial provido para condenar a ré ao pagamento de indenização por dano moral.",
        "area": "Civil",
        "tema": "Dano moral por inscrição indevida em cadastro de inadimplentes",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 2.345.678/RJ",
        "data_julgamento": "2024-01-20",
        "relator": "Min. Luis Felipe Salomão",
        "ementa": "DIREITO TRIBUTÁRIO. ICMS. BASE DE CÁLCULO. A base de cálculo do ICMS não pode incluir o próprio ICMS. Tese firmada em repercussão geral (Tema 69). Recurso especial provido.",
        "relatorio": "Recurso especial sobre a inclusão do ICMS na base de cálculo do próprio ICMS...",
        "voto": "Voto do relator: a base de cálculo do ICMS não pode incluir o próprio ICMS...",
        "dispositivo": "Recurso especial provido para excluir o ICMS da base de cálculo.",
        "area": "Tributário",
        "tema": "ICMS na base de cálculo do próprio ICMS (Tema 69)",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 3.456.789/MG",
        "data_julgamento": "2023-11-10",
        "relator": "Min. Maria Isabel Gallotti",
        "ementa": "DIREITO DO TRABALHO. HORAS EXTRAS. BANCO DE HORAS. O banco de horas deve ser instituído por acordo individual ou coletivo, com compensação no mesmo mês. Precedentes. Recurso especial provido em parte.",
        "relatorio": "Recurso especial sobre a validade do banco de horas...",
        "voto": "Voto do relator: o banco de horas deve ser instituído por acordo...",
        "dispositivo": "Recurso especial provido em parte para reconhecer a validade do banco de horas com compensação no mesmo mês.",
        "area": "Trabalhista",
        "tema": "Banco de horas e compensação",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "STF",
        "numero": "RE 1.234.567/DF",
        "data_julgamento": "2024-02-28",
        "relator": "Min. Alexandre de Moraes",
        "ementa": "DIREITO CONSTITUCIONAL. REPERCUSSÃO GERAL. TEMA 1.000. MARCO TEMPORAL DAS TERRAS INDÍGENAS. O marco temporal para demarcação de terras indígenas é a data da promulgação da Constituição Federal de 1988. Tese fixada em repercussão geral.",
        "relatorio": "Recurso extraordinário sobre o marco temporal das terras indígenas...",
        "voto": "Voto do relator: o marco temporal é a data da promulgação da CF/88...",
        "dispositivo": "Tese fixada: o marco temporal para demarcação de terras indígenas é a data da promulgação da Constituição Federal de 1988.",
        "area": "Constitucional",
        "tema": "Marco temporal das terras indígenas (Tema 1.000)",
        "url_origem": "https://www.stf.jus.br/",
    },
    {
        "tribunal": "STF",
        "numero": "ADI 5.678/DF",
        "data_julgamento": "2023-09-15",
        "relator": "Min. Edson Fachin",
        "ementa": "DIREITO CONSTITUCIONAL. AÇÃO DIRETA DE INCONSTITUCIONALIDADE. LEI DE IMPROBIDADE ADMINISTRATIVA. A nova Lei de Improbidade Administrativa (Lei 14.230/2021) é constitucional. A exigência de dolo para a prática de ato de improbidade é constitucional.",
        "relatorio": "ADI sobre a constitucionalidade da Lei de Improbidade Administrativa...",
        "voto": "Voto do relator: a nova LIA é constitucional...",
        "dispositivo": "ADI julgada improcedente. A Lei 14.230/2021 é constitucional.",
        "area": "Constitucional",
        "tema": "Constitucionalidade da Lei de Improbidade Administrativa (Lei 14.230/2021)",
        "url_origem": "https://www.stf.jus.br/",
    },
    {
        "tribunal": "TST",
        "numero": "RR 456.789/SP",
        "data_julgamento": "2024-04-05",
        "relator": "Min. Maria Cristina Peduzzi",
        "ementa": "DIREITO DO TRABALHO. RESCISÃO INDIRETA. ATRASO NO PAGAMENTO DE SALÁRIOS. O atraso reiterado no pagamento de salários autoriza a rescisão indireta do contrato de trabalho, nos termos do art. 483, 'd', da CLT. Precedentes. Recurso de revista provido.",
        "relatorio": "Recurso de revista sobre rescisão indireta por atraso no pagamento de salários...",
        "voto": "Voto do relator: o atraso reiterado autoriza a rescisão indireta...",
        "dispositivo": "Recurso de revista provido para reconhecer a rescisão indireta.",
        "area": "Trabalhista",
        "tema": "Rescisão indireta por atraso no pagamento de salários",
        "url_origem": "https://www.tst.jus.br/",
    },
    {
        "tribunal": "TJSP",
        "numero": "Apelação 1001234-56.2023.8.26.0100",
        "data_julgamento": "2024-05-12",
        "relator": "Des. Ricardo Mair Anafe",
        "ementa": "DIREITO CIVIL. LOCAÇÃO. DESPEJO. FALTA DE PAGAMENTO. A falta de pagamento do aluguel autoriza o despejo por falta de pagamento, nos termos do art. 9º, III, da Lei 8.245/91. Apelação provida.",
        "relatorio": "Apelação sobre despejo por falta de pagamento de aluguel...",
        "voto": "Voto do relator: a falta de pagamento autoriza o despejo...",
        "dispositivo": "Apelação provida para decretar o despejo.",
        "area": "Civil",
        "tema": "Despejo por falta de pagamento de aluguel",
        "url_origem": "https://www.tjsp.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 4.567.890/PR",
        "data_julgamento": "2024-06-01",
        "relator": "Min. Raul Araújo",
        "ementa": "DIREITO ADMINISTRATIVO. LICITAÇÃO. HABILITAÇÃO. A empresa que não apresenta documentação exigida no edital não pode ser habilitada. Precedentes. Recurso especial provido.",
        "relatorio": "Recurso especial sobre habilitação em licitação...",
        "voto": "Voto do relator: a empresa que não apresenta documentação não pode ser habilitada...",
        "dispositivo": "Recurso especial provido para anular a habilitação.",
        "area": "Administrativo",
        "tema": "Habilitação em licitação - documentação",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 5.678.901/RS",
        "data_julgamento": "2023-12-15",
        "relator": "Min. Moura Ribeiro",
        "ementa": "DIREITO PENAL. TRÁFICO DE DROGAS. PENA. A quantidade de droga é circunstância judicial, não causa de aumento de pena. Precedentes. Recurso especial provido em parte.",
        "relatorio": "Recurso especial sobre a pena no tráfico de drogas...",
        "voto": "Voto do relator: a quantidade de droga é circunstância judicial...",
        "dispositivo": "Recurso especial provido em parte para redimensionar a pena.",
        "area": "Penal",
        "tema": "Quantidade de droga e pena no tráfico",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
]


def seed_db():
    """Popula o banco com dados de exemplo."""
    from db import init_db, count_acordaos

    init_db()
    if count_acordaos() == 0:
        for ac in SEED_ACORDAOS:
            insert_acordao(ac)
        print(f"Seed: {len(SEED_ACORDAOS)} acórdãos inseridos.")
    else:
        print(f"Banco já possui {count_acordaos()} acórdãos.")


def scrape_stj(termo: str, max_results: int = 10):
    """Tenta buscar jurisprudencia no STJ. Retorna lista de dicts."""
    results = []
    try:
        params = {
            "livre": termo,
            "b": "ACOR",
        }
        resp = requests.get(STJ_SEARCH_URL, params=params, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Extrai resultados (estrutura pode variar)
            items = soup.select(".resultado, .item-resultado, tr")
            for item in items[:max_results]:
                text = item.get_text(strip=True)
                if len(text) > 50:
                    results.append({"raw": text[:500]})
    except Exception as e:
        print(f"Erro ao acessar STJ: {e}")
    return results


if __name__ == "__main__":
    seed_db()
    from db import count_acordaos

    print("Scraper pronto. Total:", count_acordaos())
