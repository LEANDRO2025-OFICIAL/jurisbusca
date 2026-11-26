"""Fixtures de teste.

`import api` dispara seed do SQLite e indexacao ChromaDB. Aqui o banco
aponta para um arquivo temporario e a indexacao vetorial e neutralizada
apenas durante o import, sem alterar o codigo de producao.
"""

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    from fastapi.testclient import TestClient

    import db
    import busca_vetorial

    db.DB_PATH = str(tmp_path_factory.mktemp("db") / "teste.db")
    original = busca_vetorial.indexar_todos
    busca_vetorial.indexar_todos = lambda *a, **k: {"status": "ignorado nos testes"}
    try:
        import api
    finally:
        busca_vetorial.indexar_todos = original

    return TestClient(api.app)
