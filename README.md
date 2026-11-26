# JurisBusca — Sistema de Busca de Jurisprudência com IA

Protótipo MVP de busca de jurisprudência, acórdãos e normas, com:
- Busca full-text (FTS5) via SQLite
- Busca semântica (vetorial) via ChromaDB + sentence-transformers
- RAG (Retrieval-Augmented Generation) com prompts de IA jurídica
- Parser de PDF de acórdãos (PyMuPDF)
- Scrapers para múltiplos tribunais
- 13 agentes MCP do curso "IA Jurídico" (Jusbrasil, STJ, TCU, TCEs, etc.)
- 6 métodos do curso (Leitura Profunda, Contraditório Simulado, etc.)

## Estrutura

```
jurisbusca/
├── api.py              # API FastAPI (18+ endpoints)
├── db.py               # Banco SQLite + FTS5
├── scraper.py          # Seed + scraper STJ
├── prompts.py          # 8 prompts jurídicos
├── ia.py               # 10 agentes MCP + 6 métodos
├── parser_acordao.py   # Parser de PDF de acórdãos
├── busca_vetorial.py   # Busca semântica (ChromaDB)
├── scrapers.py         # Scrapers TJSP, TST, DOU, TCE-SP
├── rag.py              # RAG com prompts de IA
├── static/index.html   # Frontend web
├── requirements.txt    # Dependências
├── Dockerfile          # Container Docker
├── docker-compose.yml  # Orquestração Docker
├── Procfile            # Deploy Railway/Heroku
├── runtime.txt         # Versão do Python
└── .gitignore          # Arquivos ignorados pelo git
```

## Endpoints principais

| Endpoint | Descrição |
|----------|-----------|
| `GET /` | Frontend web |
| `GET /api/search` | Busca full-text |
| `GET /api/search-semantico` | Busca semântica (vetorial) |
| `GET /api/rag` | RAG com resposta em linguagem natural |
| `POST /api/parser/upload` | Upload de PDF de acórdão |
| `GET /api/scraper/buscar-todos` | Busca em múltiplos tribunais |
| `GET /api/prompts` | Lista de prompts jurídicos |
| `GET /api/agentes-mcp` | Lista de agentes MCP do curso IA Jurídico |
| `GET /api/metodos` | Lista de métodos do curso |
| `GET /api/stats` | Estatísticas do banco |
| `GET /api/estatisticas-vetor` | Estatísticas da base vetorial |

## Como rodar localmente

```bash
cd jurisbusca
pip install -r requirements.txt
python db.py
python scraper.py
python api.py
# Acesse http://localhost:8000
```

## Deploy com Docker

```bash
cd jurisbusca
docker-compose up --build
# Acesse http://localhost:8000
```

## Deploy no Railway

1. Conecte seu repositório GitHub ao Railway
2. Selecione a pasta `jurisbusca` como root do projeto
3. O Railway detectará automaticamente o `Procfile` e o `runtime.txt`
4. Defina a porta 8000 no Railway
5. Faça deploy

## Tecnologias

- FastAPI (API)
- SQLite + FTS5 (busca full-text)
- ChromaDB + sentence-transformers (busca vetorial)
- PyMuPDF (parser de PDF)
- BeautifulSoup (scraping)

> **Nota:** Muitos portais de tribunais exigem login, CAPTCHA ou têm proteção anti-bot. Os scrapers retornam 0 resultados nesses casos — isso é esperado.