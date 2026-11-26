"""Smoke tests de rotas leves, sem rede externa."""


def test_home_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_stats_reports_seeded_acordaos(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["total_acordaos"] > 0
    assert isinstance(body["tribunais"], list)


def test_text_search_returns_envelope(client):
    r = client.get("/api/search", params={"q": "dano", "limit": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["query"] == "dano"
    assert body["total"] == len(body["results"]) <= 5


def test_search_requires_query(client):
    assert client.get("/api/search").status_code == 422


def test_unknown_acordao_returns_404(client):
    assert client.get("/api/acordao/999999").status_code == 404


def test_prompts_listing(client):
    r = client.get("/api/prompts")
    assert r.status_code == 200
    assert "prompts" in r.json()
