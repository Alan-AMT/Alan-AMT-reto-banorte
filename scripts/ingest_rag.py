import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pinecone import Pinecone, ServerlessSpec

# 1. Cargar variables de entorno
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "banorte-rag-index")
RAG_DIR = os.getenv("RAG_CONTENT_DIR", "rag_content")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY no encontrada en las variables de entorno.")
if not PINECONE_KEY:
    raise ValueError("PINECONE_KEY no encontrada en las variables de entorno.")


def parse_markdown_file(file_path: str):
    """
    Parsea un archivo Markdown que contiene bloques de Metadata (JSON) y Contenido.
    Retorna una lista de diccionarios con {id, metadata, content, source_file}.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        file_text = f.read()

    chunks = []
    # Regex para capturar Metadata JSON y el Contenido subsiguiente
    pattern = re.compile(
        r"Metadata:\s*\n(\s*\{[\s\S]*?\})\s*\n+Contenido:\s*\n([\s\S]*?)(?=(?:\n*Metadata:|\Z))",
        re.MULTILINE,
    )

    matches = pattern.findall(file_text)
    source_file = os.path.basename(file_path)

    for idx, (json_str, content_str) in enumerate(matches, 1):
        content_clean = content_str.strip()
        # Remover comas flotantes al final de arreglos o diccionarios para mayor tolerancia
        json_clean = re.sub(r',\s*([\]}])', r'\1', json_str.strip())
        try:
            meta_json = json.loads(json_clean)
        except json.JSONDecodeError as e:
            print(f"⚠️ Error al parsear JSON en chunk {idx} de {source_file}: {e}")
            continue

        chunk_id = meta_json.get("id")
        if not chunk_id:
            chunk_id = f"{source_file}_{idx}"

        chunks.append(
            {
                "id": chunk_id,
                "metadata": meta_json,
                "content": content_clean,
                "source_file": source_file,
            }
        )

    return chunks


def build_enriched_text(meta: dict, content: str) -> str:
    """
    Construye una cadena de texto enriquecida en lenguaje natural para el embedding.
    Formato:
      Título: {title}
      Organización: {organization} | Rol: {role}
      Etiquetas: {tags}
      Contenido: {content}
    """
    title = meta.get("title", "")
    org = meta.get("organization", "")
    role = meta.get("role", "")
    tags = meta.get("tags", [])

    lines = []
    if title:
        lines.append(f"Título: {title}")

    org_role = []
    if org:
        org_role.append(f"Organización: {org}")
    if role:
        org_role.append(f"Rol: {role}")
    if org_role:
        lines.append(" | ".join(org_role))

    if tags:
        if isinstance(tags, list):
            tags_str = ", ".join([str(t) for t in tags])
        else:
            tags_str = str(tags)
        lines.append(f"Etiquetas: {tags_str}")

    lines.append(f"Contenido: {content}")
    return "\n".join(lines)


def flatten_metadata_for_pinecone(meta: dict, content: str, source_file: str) -> dict:
    """
    Aplana la metadata para Pinecone (Pinecone no soporta objetos anidados).
    Convierte None a "" y asegura que los tipos sean válidos (str, int, float, bool, List[str]).
    """
    flat = {
        "content": content,
        "source_file": source_file,
    }
    for key, val in meta.items():
        if val is None:
            flat[key] = ""
        elif isinstance(val, (str, int, float, bool)):
            flat[key] = val
        elif isinstance(val, list):
            flat[key] = [str(x) for x in val if x is not None]
        else:
            flat[key] = str(val)
    return flat


def main():
    print("🚀 Iniciando proceso de ingesta RAG...")

    # 2. Leer todos los archivos markdown en RAG_DIR
    if not os.path.exists(RAG_DIR):
        raise FileNotFoundError(f"El directorio '{RAG_DIR}' no existe.")

    md_files = [
        os.path.join(RAG_DIR, f)
        for f in os.listdir(RAG_DIR)
        if f.endswith(".md")
    ]
    md_files.sort()

    print(f"📁 Encontrados {len(md_files)} archivos .md en '{RAG_DIR}':")
    for f in md_files:
        print(f"  - {os.path.basename(f)}")

    all_chunks = []
    for fpath in md_files:
        file_chunks = parse_markdown_file(fpath)
        all_chunks.extend(file_chunks)
        print(f"  ✓ {os.path.basename(fpath)}: {len(file_chunks)} chunks parseados.")

    print(f"\n📊 Total de chunks extraídos: {len(all_chunks)}")

    # 3. Inicializar clientes de Gemini y Pinecone
    print("\n🔑 Conectando con Google Gemini API y Pinecone...")
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
    pc = Pinecone(api_key=PINECONE_KEY)

    # 4. Asegurar índice en Pinecone
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        print(f"🔨 Creando índice Pinecone '{INDEX_NAME}' (dim=768, metric=cosine)...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"✅ Índice '{INDEX_NAME}' creado exitosamente.")
    else:
        print(f"ℹ️ El índice Pinecone '{INDEX_NAME}' ya existe.")

    index = pc.Index(INDEX_NAME)

    # 5. Generar embeddings y preparar payload de Pinecone
    print("\n🧬 Generando embeddings con 'gemini-embedding-001' (dim=768, RETRIEVAL_DOCUMENT)...")
    vectors_to_upsert = []

    for idx, chunk in enumerate(all_chunks, 1):
        chunk_id = chunk["id"]
        enriched_text = build_enriched_text(chunk["metadata"], chunk["content"])
        flat_meta = flatten_metadata_for_pinecone(
            chunk["metadata"], chunk["content"], chunk["source_file"]
        )

        try:
            embed_response = genai_client.models.embed_content(
                model="gemini-embedding-001",
                contents=enriched_text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=768,
                ),
            )
            embedding_vector = embed_response.embeddings[0].values

            vectors_to_upsert.append(
                {
                    "id": chunk_id,
                    "values": embedding_vector,
                    "metadata": flat_meta,
                }
            )
            print(f"  [{idx}/{len(all_chunks)}] Embedding generado para '{chunk_id}'")
        except Exception as e:
            print(f"❌ Error generando embedding para chunk '{chunk_id}': {e}")

    # 6. Realizar Upsert a Pinecone
    print(f"\n⬆️ Subiendo {len(vectors_to_upsert)} vectores a Pinecone...")
    index.upsert(vectors=vectors_to_upsert)
    print("✅ Upsert completado con éxito.")

    # 7. Verificar estadísticas del índice
    stats = index.describe_index_stats()
    print(f"\n📈 Estadísticas del Índice Pinecone '{INDEX_NAME}':")
    print(f"  - Total de vectores: {stats.total_vector_count}")
    print(f"  - Dimensión: {stats.dimension}")

    # 8. Sanity Check / Prueba de Búsqueda RAG
    print("\n🔍 Ejecutando prueba de búsqueda RAG (RETRIEVAL_QUERY)...")
    query_text = "¿Qué experiencia en Flutter y desarrollo móvil de aplicaciones bancarias tiene Alan?"
    query_response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=query_text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768,
        ),
    )
    query_vector = query_response.embeddings[0].values

    search_res = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True,
    )

    print(f"\nQuery de prueba: '{query_text}'")
    print("Top 3 resultados encontrados:")
    for match in search_res.matches:
        score = match.score
        meta = match.metadata
        print(f"  • ID: {match.id} | Score: {score:.4f}")
        print(f"    Título: {meta.get('title', 'N/A')}")
        print(f"    Categoría: {meta.get('category', 'N/A')}")
        print(f"    Archivo: {meta.get('source_file', 'N/A')}")
        snippet = meta.get("content", "")[:120].replace("\n", " ")
        print(f"    Snippet: {snippet}...\n")


if __name__ == "__main__":
    main()
