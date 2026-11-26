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
    {
        "tribunal": "STF",
        "numero": "RE 987.654/MG",
        "data_julgamento": "2024-07-10",
        "relator": "Min. Gilmar Mendes",
        "ementa": "DIREITO TRIBUTÁRIO. ICMS. SUBSTITUIÇÃO TRIBUTÁRIA. O regime de substituição tributária do ICMS não viola o princípio da não-cumulatividade. Precedentes. Recurso extraordinário provido.",
        "relatorio": "Recurso extraordinário sobre a constitucionalidade da substituição tributária do ICMS...",
        "voto": "Voto do relator: a substituição tributária não viola a não-cumulatividade...",
        "dispositivo": "Recurso extraordinário provido para reconhecer a constitucionalidade da substituição tributária.",
        "area": "Tributário",
        "tema": "Substituição tributária do ICMS",
        "url_origem": "https://www.stf.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 6.789.012/BA",
        "data_julgamento": "2024-02-20",
        "relator": "Min. Ricardo Villas Bôas Cueva",
        "ementa": "DIREITO DO CONSUMIDOR. PLANO DE SAÚDE. COBERTURA. A operadora de plano de saúde deve cobrir tratamento não previsto no rol da ANS quando houver recomendação médica. Precedentes. Recurso especial provido.",
        "relatorio": "Recurso especial sobre cobertura de tratamento de saúde não previsto no rol da ANS...",
        "voto": "Voto do relator: a operadora deve cobrir tratamento recomendado por médico...",
        "dispositivo": "Recurso especial provido para obrigar a cobertura do tratamento.",
        "area": "Civil",
        "tema": "Cobertura de plano de saúde - tratamento não previsto no rol da ANS",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "TJSP",
        "numero": "Apelação 1002345-67.2023.8.26.0100",
        "data_julgamento": "2024-03-05",
        "relator": "Des. Eduardo Siqueira",
        "ementa": "DIREITO CIVIL. CONTRATO. RESCISÃO. INADIMPLEMENTO. O inadimplemento contratual autoriza a rescisão do contrato com perdas e danos. Apelação provida.",
        "relatorio": "Apelação sobre rescisão de contrato por inadimplemento...",
        "voto": "Voto do relator: o inadimplemento autoriza a rescisão...",
        "dispositivo": "Apelação provida para decretar a rescisão do contrato.",
        "area": "Civil",
        "tema": "Rescisão de contrato por inadimplemento",
        "url_origem": "https://www.tjsp.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 7.890.123/PR",
        "data_julgamento": "2023-10-18",
        "relator": "Min. João Otávio de Noronha",
        "ementa": "DIREITO ADMINISTRATIVO. SERVIDOR PÚBLICO. DEMISSÃO. A demissão por abandono de cargo exige processo administrativo com ampla defesa. Precedentes. Recurso especial provido.",
        "relatorio": "Recurso especial sobre demissão por abandono de cargo...",
        "voto": "Voto do relator: a demissão exige processo administrativo...",
        "dispositivo": "Recurso especial provido para anular a demissão.",
        "area": "Administrativo",
        "tema": "Demissão por abandono de cargo - processo administrativo",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "STF",
        "numero": "RE 890.123/RJ",
        "data_julgamento": "2024-01-15",
        "relator": "Min. Luís Roberto Barroso",
        "ementa": "DIREITO CONSTITUCIONAL. LIBERDADE DE EXPRESSÃO. A liberdade de expressão não abrange discurso de ódio. Precedentes. Recurso extraordinário provido.",
        "relatorio": "Recurso extraordinário sobre limites da liberdade de expressão...",
        "voto": "Voto do relator: a liberdade de expressão não abrange discurso de ódio...",
        "dispositivo": "Recurso extraordinário provido para reconhecer a limitação.",
        "area": "Constitucional",
        "tema": "Limites da liberdade de expressão - discurso de ódio",
        "url_origem": "https://www.stf.jus.br/",
    },
    {
        "tribunal": "TST",
        "numero": "RR 567.890/MG",
        "data_julgamento": "2024-05-20",
        "relator": "Min. Maria Cristina Peduzzi",
        "ementa": "DIREITO DO TRABALHO. ASSÉDIO MORAL. O assédio moral no ambiente de trabalho gera dano moral presumido. Precedentes. Recurso de revista provido.",
        "relatorio": "Recurso de revista sobre assédio moral no trabalho...",
        "voto": "Voto do relator: o assédio moral gera dano moral presumido...",
        "dispositivo": "Recurso de revista provido para condenar a empresa.",
        "area": "Trabalhista",
        "tema": "Assédio moral no ambiente de trabalho",
        "url_origem": "https://www.tst.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 8.901.234/SC",
        "data_julgamento": "2023-11-28",
        "relator": "Min. Nancy Andrighi",
        "ementa": "DIREITO CIVIL. CONTRATO. REVISÃO. A revisão contratual exige demonstração de desequilíbrio econômico-financeiro. Precedentes. Recurso especial provido em parte.",
        "relatorio": "Recurso especial sobre revisão de contrato...",
        "voto": "Voto do relator: a revisão exige demonstração de desequilíbrio...",
        "dispositivo": "Recurso especial provido em parte para revisar o contrato.",
        "area": "Civil",
        "tema": "Revisão contratual - desequilíbrio econômico-financeiro",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "TJSP",
        "numero": "Apelação 1003456-78.2023.8.26.0100",
        "data_julgamento": "2024-04-10",
        "relator": "Des. Ricardo Mair Anafe",
        "ementa": "DIREITO CIVIL. RESPONSABILIDADE. ACIDENTE DE TRÂNSITO. A vítima de acidente de trânsito tem direito à indenização por danos materiais e morais. Apelação provida.",
        "relatorio": "Apelação sobre indenização por acidente de trânsito...",
        "voto": "Voto do relator: a vítima tem direito à indenização...",
        "dispositivo": "Apelação provida para condenar o réu.",
        "area": "Civil",
        "tema": "Indenização por acidente de trânsito",
        "url_origem": "https://www.tjsp.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 9.012.345/CE",
        "data_julgamento": "2024-03-12",
        "relator": "Min. Luis Felipe Salomão",
        "ementa": "DIREITO TRIBUTÁRIO. IPTU. BASE DE CÁLCULO. A base de cálculo do IPTU deve ser o valor venal do imóvel, não o valor de mercado. Precedentes. Recurso especial provido.",
        "relatorio": "Recurso especial sobre base de cálculo do IPTU...",
        "voto": "Voto do relator: a base de cálculo deve ser o valor venal...",
        "dispositivo": "Recurso especial provido para recalcular o IPTU.",
        "area": "Tributário",
        "tema": "Base de cálculo do IPTU - valor venal",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "STF",
        "numero": "RE 901.234/SP",
        "data_julgamento": "2024-02-05",
        "relator": "Min. Edson Fachin",
        "ementa": "DIREITO CONSTITUCIONAL. PRECATÓRIO. PAGAMENTO. O pagamento de precatórios deve observar a ordem cronológica. Precedentes. Recurso extraordinário provido.",
        "relatorio": "Recurso extraordinário sobre pagamento de precatórios...",
        "voto": "Voto do relator: o pagamento deve observar a ordem cronológica...",
        "dispositivo": "Recurso extraordinário provido para determinar o pagamento na ordem cronológica.",
        "area": "Constitucional",
        "tema": "Pagamento de precatórios - ordem cronológica",
        "url_origem": "https://www.stf.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 1.012.345/DF",
        "data_julgamento": "2023-09-20",
        "relator": "Min. Maria Isabel Gallotti",
        "ementa": "DIREITO CIVIL. FAMÍLIA. GUARDA. A guarda compartilhada é a regra, salvo exceções. Precedentes. Recurso especial provido.",
        "relatorio": "Recurso especial sobre guarda compartilhada...",
        "voto": "Voto do relator: a guarda compartilhada é a regra...",
        "dispositivo": "Recurso especial provido para estabelecer guarda compartilhada.",
        "area": "Civil",
        "tema": "Guarda compartilhada de filhos",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "TST",
        "numero": "RR 678.901/RJ",
        "data_julgamento": "2024-06-10",
        "relator": "Min. Maria Cristina Peduzzi",
        "ementa": "DIREITO DO TRABALHO. HORAS EXTRAS. INTERVALO INTRAJORNADA. O intervalo intrajornada não utilizado gera direito a horas extras. Precedentes. Recurso de revista provido.",
        "relatorio": "Recurso de revista sobre intervalo intrajornada...",
        "voto": "Voto do relator: o intervalo não utilizado gera horas extras...",
        "dispositivo": "Recurso de revista provido para reconhecer o direito a horas extras.",
        "area": "Trabalhista",
        "tema": "Intervalo intrajornada não utilizado",
        "url_origem": "https://www.tst.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 2.123.456/SP",
        "data_julgamento": "2024-01-08",
        "relator": "Min. Raul Araújo",
        "ementa": "DIREITO ADMINISTRATIVO. LICITAÇÃO. IMPUGNAÇÃO. A impugnação ao edital deve ser apresentada antes do encerramento da licitação. Precedentes. Recurso especial provido.",
        "relatorio": "Recurso especial sobre impugnação ao edital de licitação...",
        "voto": "Voto do relator: a impugnação deve ser apresentada antes do encerramento...",
        "dispositivo": "Recurso especial provido para reconhecer a tempestividade da impugnação.",
        "area": "Administrativo",
        "tema": "Impugnação ao edital de licitação - tempestividade",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 3.234.567/MG",
        "data_julgamento": "2023-11-05",
        "relator": "Min. Moura Ribeiro",
        "ementa": "DIREITO CIVIL. RESPONSABILIDADE. DANOS MORAIS. A indenização por dano moral deve ser fixada com razoabilidade, considerando as circunstâncias do caso. Precedentes. Recurso especial provido em parte.",
        "relatorio": "Recurso especial sobre fixação de indenização por dano moral...",
        "voto": "Voto do relator: a indenização deve ser razoável...",
        "dispositivo": "Recurso especial provido em parte para redimensionar a indenização.",
        "area": "Civil",
        "tema": "Fixação de indenização por dano moral - razoabilidade",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "TJSP",
        "numero": "Apelação 1004567-89.2023.8.26.0100",
        "data_julgamento": "2024-05-15",
        "relator": "Des. Eduardo Siqueira",
        "ementa": "DIREITO CIVIL. FAMÍLIA. DIVÓRCIO. A partilha de bens no divórcio deve observar o regime de comunhão parcial. Apelação provida.",
        "relatorio": "Apelação sobre partilha de bens no divórcio...",
        "voto": "Voto do relator: a partilha deve observar o regime...",
        "dispositivo": "Apelação provida para determinar a partilha.",
        "area": "Civil",
        "tema": "Partilha de bens no divórcio - comunhão parcial",
        "url_origem": "https://www.tjsp.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 4.345.678/BA",
        "data_julgamento": "2024-02-14",
        "relator": "Min. Nancy Andrighi",
        "ementa": "DIREITO DO CONSUMIDOR. BANCO. TARIFAS. A cobrança de tarifas bancárias não previstas em contrato é abusiva. Precedentes. Recurso especial provido.",
        "relatorio": "Recurso especial sobre cobrança de tarifas bancárias...",
        "voto": "Voto do relator: a cobrança de tarifas não previstas é abusiva...",
        "dispositivo": "Recurso especial provido para declarar a abusividade.",
        "area": "Civil",
        "tema": "Tarifas bancárias não previstas em contrato",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "STF",
        "numero": "RE 812.345/RS",
        "data_julgamento": "2023-12-08",
        "relator": "Min. Alexandre de Moraes",
        "ementa": "DIREITO CONSTITUCIONAL. HABEAS CORPUS. PRISÃO PREVENTIVA. A prisão preventiva exige fundamentação concreta e não pode ser baseada apenas na gravidade do crime. Precedentes. Recurso extraordinário provido.",
        "relatorio": "Recurso extraordinário sobre prisão preventiva...",
        "voto": "Voto do relator: a prisão preventiva exige fundamentação concreta...",
        "dispositivo": "Recurso extraordinário provido para relaxar a prisão.",
        "area": "Constitucional",
        "tema": "Prisão preventiva - fundamentação concreta",
        "url_origem": "https://www.stf.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 5.456.789/SC",
        "data_julgamento": "2024-04-22",
        "relator": "Min. João Otávio de Noronha",
        "ementa": "DIREITO ADMINISTRATIVO. SERVIDOR PÚBLICO. APOSENTADORIA. A aposentadoria por invalidez exige laudo médico pericial. Precedentes. Recurso especial provido.",
        "relatorio": "Recurso especial sobre aposentadoria por invalidez...",
        "voto": "Voto do relator: a aposentadoria por invalidez exige laudo pericial...",
        "dispositivo": "Recurso especial provido para reconhecer o direito à aposentadoria.",
        "area": "Administrativo",
        "tema": "Aposentadoria por invalidez - laudo pericial",
        "url_origem": "https://www.stj.jus.br/SCON/",
    },
    {
        "tribunal": "TST",
        "numero": "RR 789.012/PR",
        "data_julgamento": "2024-03-18",
        "relator": "Min. Maria Cristina Peduzzi",
        "ementa": "DIREITO DO TRABALHO. EQUIPARAÇÃO SALARIAL. A equiparação salarial exige identidade de função e condições de trabalho. Precedentes. Recurso de revista provido.",
        "relatorio": "Recurso de revista sobre equiparação salarial...",
        "voto": "Voto do relator: a equiparação exige identidade de função...",
        "dispositivo": "Recurso de revista provido para reconhecer a equiparação.",
        "area": "Trabalhista",
        "tema": "Equiparação salarial - identidade de função",
        "url_origem": "https://www.tst.jus.br/",
    },
    {
        "tribunal": "STJ",
        "numero": "REsp 6.567.890/CE",
        "data_julgamento": "2023-10-30",
        "relator": "Min. Ricardo Villas Bôas Cueva",
        "ementa": "DIREITO CIVIL. RESPONSABILIDADE. DANOS MORAIS. A indenização por dano moral deve ser proporcional ao dano sofrido. Precedentes. Recurso especial provido em parte.",
        "relatorio": "Recurso especial sobre proporcionalidade da indenização por dano moral...",
        "voto": "Voto do relator: a indenização deve ser proporcional...",
        "dispositivo": "Recurso especial provido em parte para redimensionar a indenização.",
        "area": "Civil",
        "tema": "Proporcionalidade da indenização por dano moral",
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
