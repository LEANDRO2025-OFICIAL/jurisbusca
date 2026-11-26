# Dockerfile para JurisBusca
FROM python:3.12-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema (necessárias para algumas bibliotecas Python)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baixa o modelo de embeddings (para evitar download na execução)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Copia todo o código da aplicação
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["python", "api.py"]