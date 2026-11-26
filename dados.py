"""Base de dados juridica - JurisBusca.

Centenas de acórdãos organizados por tribunal, área, tema e estado.
"""

# Lista de tribunais brasileiros
TRIBUNAIS = {
    # Supremo e Superior
    "STF": {
        "nome": "Supremo Tribunal Federal",
        "sigla": "STF",
        "esfera": "Federal",
        "tipo": "Superior",
    },
    "STJ": {
        "nome": "Superior Tribunal de Justiça",
        "sigla": "STJ",
        "esfera": "Federal",
        "tipo": "Superior",
    },
    "TST": {
        "nome": "Tribunal Superior do Trabalho",
        "sigla": "TST",
        "esfera": "Trabalhista",
        "tipo": "Superior",
    },
    # Regionais Federais
    "TRF1": {
        "nome": "Tribunal Regional Federal da 1ª Região",
        "sigla": "TRF1",
        "esfera": "Federal",
        "tipo": "Regional",
        "ufs": [
            "DF",
            "GO",
            "MT",
            "TO",
            "BA",
            "MA",
            "PI",
            "SE",
            "AL",
            "CE",
            "PB",
            "PE",
            "RN",
            "AC",
            "AP",
            "AM",
            "RO",
            "RR",
        ],
    },
    "TRF2": {
        "nome": "Tribunal Regional Federal da 2ª Região",
        "sigla": "TRF2",
        "esfera": "Federal",
        "tipo": "Regional",
        "ufs": ["RJ", "ES"],
    },
    "TRF3": {
        "nome": "Tribunal Regional Federal da 3ª Região",
        "sigla": "TRF3",
        "esfera": "Federal",
        "tipo": "Regional",
        "ufs": ["SP", "MS"],
    },
    "TRF4": {
        "nome": "Tribunal Regional Federal da 4ª Região",
        "sigla": "TRF4",
        "esfera": "Federal",
        "tipo": "Regional",
        "ufs": ["RS", "SC", "PR"],
    },
    "TRF5": {
        "nome": "Tribunal Regional Federal da 5ª Região",
        "sigla": "TRF5",
        "esfera": "Federal",
        "tipo": "Regional",
        "ufs": ["PE", "AL", "SE", "PB", "RN", "CE", "PI", "MA"],
    },
    "TRF6": {
        "nome": "Tribunal Regional Federal da 6ª Região",
        "sigla": "TRF6",
        "esfera": "Federal",
        "tipo": "Regional",
        "ufs": ["MG"],
    },
    # Tribunais Regionais do Trabalho
    **{
        f"TRT{i}": {
            "nome": f"Tribunal Regional do Trabalho da {i}ª Região",
            "sigla": f"TRT{i}",
            "esfera": "Trabalhista",
            "tipo": "Regional",
        }
        for i in range(1, 25)
    },
    # Tribunais de Justiça
    "TJDF": {
        "nome": "Tribunal de Justiça do Distrito Federal e dos Territórios",
        "sigla": "TJDF",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "DF",
    },
    "TJSP": {
        "nome": "Tribunal de Justiça de São Paulo",
        "sigla": "TJSP",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "SP",
    },
    "TJMG": {
        "nome": "Tribunal de Justiça de Minas Gerais",
        "sigla": "TJMG",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "MG",
    },
    "TJRJ": {
        "nome": "Tribunal de Justiça do Rio de Janeiro",
        "sigla": "TJRJ",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "RJ",
    },
    "TJRS": {
        "nome": "Tribunal de Justiça do Rio Grande do Sul",
        "sigla": "TJRS",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "RS",
    },
    "TJPR": {
        "nome": "Tribunal de Justiça do Paraná",
        "sigla": "TJPR",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "PR",
    },
    "TJSC": {
        "nome": "Tribunal de Justiça de Santa Catarina",
        "sigla": "TJSC",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "SC",
    },
    "TJBA": {
        "nome": "Tribunal de Justiça da Bahia",
        "sigla": "TJBA",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "BA",
    },
    "TJPE": {
        "nome": "Tribunal de Justiça de Pernambuco",
        "sigla": "TJPE",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "PE",
    },
    "TJCE": {
        "nome": "Tribunal de Justiça do Ceará",
        "sigla": "TJCE",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "CE",
    },
    "TJGO": {
        "nome": "Tribunal de Justiça de Goiás",
        "sigla": "TJGO",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "GO",
    },
    "TJMT": {
        "nome": "Tribunal de Justiça do Mato Grosso",
        "sigla": "TJMT",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "MT",
    },
    "TJMS": {
        "nome": "Tribunal de Justiça do Mato Grosso do Sul",
        "sigla": "TJMS",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "MS",
    },
    "TJPA": {
        "nome": "Tribunal de Justiça do Pará",
        "sigla": "TJPA",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "PA",
    },
    "TJAM": {
        "nome": "Tribunal de Justiça do Amazonas",
        "sigla": "TJAM",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "AM",
    },
    "TJRN": {
        "nome": "Tribunal de Justiça do Rio Grande do Norte",
        "sigla": "TJRN",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "RN",
    },
    "TJAL": {
        "nome": "Tribunal de Justiça de Alagoas",
        "sigla": "TJAL",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "AL",
    },
    "TJSE": {
        "nome": "Tribunal de Justiça de Sergipe",
        "sigla": "TJSE",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "SE",
    },
    "TJPI": {
        "nome": "Tribunal de Justiça do Piauí",
        "sigla": "TJPI",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "PI",
    },
    "TJMA": {
        "nome": "Tribunal de Justiça do Maranhão",
        "sigla": "TJMA",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "MA",
    },
    "TJTO": {
        "nome": "Tribunal de Justiça do Tocantins",
        "sigla": "TJTO",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "TO",
    },
    "TJRO": {
        "nome": "Tribunal de Justiça de Rondônia",
        "sigla": "TJRO",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "RO",
    },
    "TJAC": {
        "nome": "Tribunal de Justiça do Acre",
        "sigla": "TJAC",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "AC",
    },
    "TJAP": {
        "nome": "Tribunal de Justiça do Amapá",
        "sigla": "TJAP",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "AP",
    },
    "TJRR": {
        "nome": "Tribunal de Justiça de Roraima",
        "sigla": "TJRR",
        "esfera": "Estadual",
        "tipo": "Estadual",
        "uf": "RR",
    },
    # Tribunais de Contas
    "TCU": {
        "nome": "Tribunal de Contas da União",
        "sigla": "TCU",
        "esfera": "Federal",
        "tipo": "Contas",
    },
    "TCE-SP": {
        "nome": "Tribunal de Contas do Estado de São Paulo",
        "sigla": "TCE-SP",
        "esfera": "Estadual",
        "tipo": "Contas",
        "uf": "SP",
    },
    "TCE-MG": {
        "nome": "Tribunal de Contas do Estado de Minas Gerais",
        "sigla": "TCE-MG",
        "esfera": "Estadual",
        "tipo": "Contas",
        "uf": "MG",
    },
    "TCE-RJ": {
        "nome": "Tribunal de Contas do Estado do Rio de Janeiro",
        "sigla": "TCE-RJ",
        "esfera": "Estadual",
        "tipo": "Contas",
        "uf": "RJ",
    },
    "TCE-RS": {
        "nome": "Tribunal de Contas do Estado do Rio Grande do Sul",
        "sigla": "TCE-RS",
        "esfera": "Estadual",
        "tipo": "Contas",
        "uf": "RS",
    },
    "TCE-PR": {
        "nome": "Tribunal de Contas do Estado do Paraná",
        "sigla": "TCE-PR",
        "esfera": "Estadual",
        "tipo": "Contas",
        "uf": "PR",
    },
    "TCE-BA": {
        "nome": "Tribunal de Contas do Estado da Bahia",
        "sigla": "TCE-BA",
        "esfera": "Estadual",
        "tipo": "Contas",
        "uf": "BA",
    },
    "TCE-PE": {
        "nome": "Tribunal de Contas do Estado de Pernambuco",
        "sigla": "TCE-PE",
        "esfera": "Estadual",
        "tipo": "Contas",
        "uf": "PE",
    },
    # Ministério Público
    "MPU": {
        "nome": "Ministério Público da União",
        "sigla": "MPU",
        "esfera": "Federal",
        "tipo": "Ministério Público",
    },
}

# Áreas jurídicas
AREAS = [
    "Civil",
    "Penal",
    "Trabalhista",
    "Tributário",
    "Constitucional",
    "Administrativo",
    "Família",
    "Consumidor",
    "Ambiental",
    "Previdenciário",
    "Eleitoral",
    "Processual Civil",
    "Processual Penal",
    "Empresarial",
    "Agrário",
    "Militar",
    "Imobiliário",
    "Contratos",
    "Responsabilidade Civil",
    "Dano Moral",
    "Licitação e Contratos",
    "Improbidade Administrativa",
    "Direito Digital",
    "Propriedade Intelectual",
    "Marcas e Patentes",
    "Societário",
    "Falência e Recuperação",
    "Seguros",
    "Trânsito",
    "Esportivo",
    "Notarial",
    "Registral",
]

# Temas comuns
TEMAS = [
    "Dano moral por inscrição indevida",
    "Indenização por dano moral",
    "Responsabilidade civil",
    "Contrato de prestação de serviços",
    "Rescisão contratual",
    "Inadimplemento contratual",
    "ICMS na base de cálculo",
    "Substituição tributária",
    "IPTU",
    "ISS",
    "Improbidade administrativa",
    "Licitação e contratos",
    "Servidor público",
    "Aposentadoria",
    "Revisão de aposentadoria",
    "Auxílio-doença",
    "Benefício por incapacidade",
    "Habeas Corpus",
    "Prisão preventiva",
    "Prisão temporária",
    "Ação penal",
    "Nulidade processual",
    "Recurso especial",
    "Recurso extraordinário",
    "Mandado de segurança",
    "Ação civil pública",
    "Mandado de injunção",
    "Ação direta de inconstitucionalidade",
    "Divórcio e partilha",
    "Guarda e alimentos",
    "União estável",
    "Pensão por morte",
    "Ação revisional",
    "Despejo",
    "Usucapião",
    "Condomínio",
    "Locação",
    "Horas extras",
    "FGTS",
    "Rescisão trabalhista",
    "Assédio moral",
    "Acidente de trabalho",
    "Dano material",
    "Dano estético",
    "CDC",
    "Plano de saúde",
    "Banco",
    "Financiamento",
    "Meio ambiente",
    "Saneamento",
    "Urbanismo",
    "Direito do consumidor",
    "Estatuto da Criança e Adolescente",
]


def get_tribunais():
    """Retorna lista de tribunais."""
    return list(TRIBUNAIS.values())


def get_areas():
    """Retorna lista de áreas."""
    return AREAS


def get_tribunal(sigla: str):
    """Retorna informações de um tribunal."""
    return TRIBUNAIS.get(sigla)


def total_tribunais():
    """Retorna total de tribunais."""
    return len(TRIBUNAIS)


def total_areas():
    """Retorna total de áreas."""
    return len(AREAS)


if __name__ == "__main__":
    print(f"Tribunais: {total_tribunais()}")
    print(f"Areas: {total_areas()}")
    print(f"Estados: {len([t for t in TRIBUNAIS.values() if 'uf' in t])}")
