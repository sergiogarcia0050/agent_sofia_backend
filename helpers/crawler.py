import sys
import uuid
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from openai import OpenAI
import os
from dotenv import load_dotenv


# ==========================
# CONFIGURACIÓN PRINCIPAL
# ==========================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

MAX_PAGES = 300
CHUNK_TOKENS = 400


# ==========================
# SCRAPER
# ==========================

def scrape_html(url: str) -> str:
    print(f"[SCRAPER] {url}")

    resp = requests.get(url, timeout=10, headers={
        "User-Agent": "Mozilla/5.0 HackatonBot"
    })
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    article = soup.find("article")
    if article:
        return article.get_text(" ", strip=True)

    return soup.get_text(" ", strip=True)


def is_internal_link(url: str, base_domain: str) -> bool:
    parsed = urlparse(url)
    return (not parsed.netloc) or (parsed.netloc == base_domain)


def crawl_docs(base_url: str, start_path: str, max_pages: int = MAX_PAGES):
    base_domain = urlparse(base_url).netloc

    queue = deque([urljoin(base_url, start_path)])
    visited = set()
    scraped = {}

    while queue and len(scraped) < max_pages:
        current = queue.popleft()
        if current in visited:
            continue

        visited.add(current)

        if any(current.endswith(ext) for ext in [".png", ".jpg", ".svg", ".pdf"]):
            continue

        try:
            text = scrape_html(current)
            scraped[current] = text
        except Exception as e:
            print(f"[ERROR] {current}: {e}")
            continue

        try:
            html = requests.get(current).text
            soup = BeautifulSoup(html, "lxml")

            for a in soup.find_all("a", href=True):
                href = a["href"]
                full = urljoin(current, href)

                if not is_internal_link(full, base_domain):
                    continue

                if not urlparse(full).path.startswith(start_path):
                    continue

                if full not in visited:
                    queue.append(full)

        except Exception as e:
            print(f"[ERROR LINKS] {current}: {e}")

    return scraped


# ==========================
# CHUNKING
# ==========================

def chunk_text(text: str, max_tokens: int = CHUNK_TOKENS):
    words = text.split()
    chunks = []
    current = []
    count = 0

    for w in words:
        current.append(w)
        count += 1

        if count >= max_tokens:
            chunks.append(" ".join(current))
            current = []
            count = 0

    if current:
        chunks.append(" ".join(current))

    return chunks


# ==========================
# 1) MODO TXT – GUARDAR EN ARCHIVO
# ==========================

def save_as_txt(scraped_pages: dict, filename="helpers/scraped_output.txt"):
    print("\n[INFO] Guardando contenido en archivo TXT...\n")

    with open(filename, "w", encoding="utf-8") as f:
        for url, content in scraped_pages.items():
            f.write(f"===== URL: {url} =====\n")
            f.write(content)
            f.write("\n\n")

    print(f"[DONE] Archivo generado: {filename}\n")


# ==========================
# 2) MODO QDRANT – EMBEDDINGS + VECTOR STORE
# ==========================

def save_to_qdrant(scraped_pages: dict, collection: str):
    print("\n[INFO] Inicializando OpenAI y Qdrant...\n")

    client = OpenAI(api_key=OPENAI_API_KEY)
    qdrant = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY,
                port=443,
                timeout=10.0
            )
    print("\n[INFO] Qdrant...\n", qdrant)
    try:
        qdrant.get_collection(collection)
        print(f"[INFO] Colección existente: {collection}")
    except:
        qdrant.create_collection(
            collection_name=collection,
            vectors_config=qmodels.VectorParams(
                size=1536,
                distance=qmodels.Distance.COSINE
            )
        )
        print(f"[INFO] Colección creada: {collection}")

    for url, text in scraped_pages.items():
        print(f"\n[PAGE] {url}")

        chunks = chunk_text(text)

        for chunk in chunks:
            emb = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            ).data[0].embedding

            point_id = str(uuid.uuid4())

            qdrant.upsert(
                collection_name=collection,
                points=[
                    qmodels.PointStruct(
                        id=point_id,
                        vector=emb,
                        payload={
                            "url": url,
                            "content": chunk
                        }
                    )
                ]
            )

    print("\n[DONE] Embeddings almacenados en Qdrant\n")

# ==========================
# LEER DESDE TXT
# ==========================

def load_from_txt(filename="scraped_output.txt"):
    print(f"\n[INFO] Leyendo contenido desde {filename}...\n")
    
    scraped_pages = {}
    current_url = None
    current_content = []
    
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("===== URL: "):
                # Si ya hay una URL previa, guardarla
                if current_url:
                    scraped_pages[current_url] = "\n".join(current_content).strip()
                
                # Extraer la nueva URL
                current_url = line.replace("===== URL: ", "").replace(" =====\n", "").strip()
                current_content = []
            else:
                # Acumular contenido
                current_content.append(line.rstrip())
        
        # Guardar la última URL
        if current_url:
            scraped_pages[current_url] = "\n".join(current_content).strip()
    
    print(f"[INFO] Páginas cargadas: {len(scraped_pages)}\n")
    return scraped_pages


# ==========================
# MAIN
# ==========================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python crawler_v2.py <base_url> <start_path> <txt|qdrant>")
        print("  python crawler_v2.py qdrant-txt")
        sys.exit(1)

    mode = sys.argv[-1].lower()  # El último argumento es siempre el modo

    if mode == "qdrant-txt":
        # Modo especial: solo leer del TXT y subir a Qdrant
        print(f"\n[INFO] Modo: {mode}\n")
        scraped_from_file = load_from_txt("scraped_output.txt")
        save_to_qdrant(scraped_from_file, "sofia_ai")
    
    elif mode in ["txt", "qdrant"]:
        # Modos que requieren scraping
        if len(sys.argv) < 4:
            print("Uso:")
            print("python crawler_v2.py <base_url> <start_path> <txt|qdrant>")
            sys.exit(1)
        
        base_url = sys.argv[1]
        start_path = sys.argv[2]
        
        print(f"\n[INFO] Iniciando crawler:\n- URL base: {base_url}\n- Ruta: {start_path}\n- Modo: {mode}\n")
        
        scraped = crawl_docs(base_url, start_path)
        
        print(f"[INFO] Páginas encontradas: {len(scraped)}\n")
        
        if mode == "txt":
            save_as_txt(scraped)
        elif mode == "qdrant":
            save_to_qdrant(scraped, "sofia_ai")
    
    else:
        print("[ERROR] Modo inválido. Use 'txt', 'qdrant' o 'qdrant-txt'.")