import logging
import os
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types
from pinecone import Pinecone

from domain.ports.tool_port import ToolPort
from infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

SEARCH_CV_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": (
                "Reformula la pregunta del usuario como una consulta de búsqueda semántica clara y "
                "autocontenida, en español. No copies la pregunta literal si tiene ambigüedad — "
                "reescríbela como si describieras el tema a buscar (ej. 'experiencia liderando equipos' "
                "en vez de 'cuéntame de una vez que lideraste algo')."
            ),
        },
        "category": {
            "type": "string",
            "enum": ["experiencia_laboral", "freelance", "educacion", "faq", "skill_summary"],
            "description": (
                "Úsalo SOLO cuando la pregunta apunte claramente a un tipo de información (ej. 'cuéntame "
                "de tu educación' → educacion). Si la pregunta es general o ambigua, omite este campo."
            ),
        },
        "tech_filter": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Nombres de tecnologías específicas mencionadas en la pregunta, en minúsculas y forma "
                "normalizada (ej. 'python', 'react', 'postgresql'). Úsalo solo cuando el usuario nombre una "
                "tecnología explícitamente."
            ),
        },
        "topic_filter": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Temas o habilidades transversales mencionados (ej. 'liderazgo', 'pagos', 'rendimiento', "
                "'trabajo-en-equipo'). Úsalo cuando la pregunta sea sobre un tema/habilidad en vez de una "
                "tecnología concreta."
            ),
        },
    },
    "required": ["query"],
}


class SearchCVTool(ToolPort):
    name: str = "search_cv"
    description: str = (
        "Busca información específica y verificada sobre la trayectoria profesional de Alan: "
        "experiencia laboral, proyectos freelance, educación, habilidades técnicas o preguntas "
        "frecuentes de comportamiento. Úsala SIEMPRE que el usuario pregunte por detalles concretos "
        "(empresas, fechas, tecnologías, proyectos, historias personales) que no estén ya en tus "
        "instrucciones base. No inventes información que esta herramienta no te devuelva.\n\n"
        "Ejemplos:\n"
        "- '¿Qué hiciste en Tecnoalfa?' → query='experiencia en Tecnoalfa', category='experiencia_laboral'\n"
        "- '¿Sabes Python?' → query='experiencia con Python', tech_filter=['python']\n"
        "- '¿Cuál ha sido tu mayor reto?' → query='mayor reto profesional', category='faq'\n"
        "- 'Cuéntame de un momento en que hayas liderado algo' → query='ejemplo de liderazgo', topic_filter=['liderazgo']"
    )
    args_schema: Dict[str, Any] = SEARCH_CV_SCHEMA

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        pinecone_api_key: Optional[str] = None,
        pinecone_index_name: Optional[str] = None,
        genai_client: Optional[Any] = None,
        pinecone_index: Optional[Any] = None,
    ):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_KEY") or settings.PINECONE_KEY
        self.pinecone_index_name = (
            pinecone_index_name or os.getenv("PINECONE_INDEX_NAME") or settings.PINECONE_INDEX_NAME
        )

        self._genai_client = genai_client
        self._pinecone_index = pinecone_index

    @property
    def genai_client(self):
        if self._genai_client is None:
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY no configurada.")
            self._genai_client = genai.Client(api_key=self.gemini_api_key)
        return self._genai_client

    @property
    def pinecone_index(self):
        if self._pinecone_index is None:
            if not self.pinecone_api_key:
                raise ValueError("PINECONE_KEY no configurada.")
            pc = Pinecone(api_key=self.pinecone_api_key)
            self._pinecone_index = pc.Index(self.pinecone_index_name)
        return self._pinecone_index

    async def run(
        self,
        query: str,
        category: Optional[str] = None,
        tech_filter: Optional[List[str]] = None,
        topic_filter: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Executes the search_cv tool by running RAG retrieval on Pinecone index.
        """
        logger.info(f"[SearchCVTool] Ejecutando búsqueda con query='{query}'")
        logger.info(
            f"[SearchCVTool] Filtros recibidos - category: {category}, tech_filter: {tech_filter}, topic_filter: {topic_filter}"
        )

        # 1. Generar embedding de query con gemini-embedding-001
        embed_response = await self.genai_client.aio.models.embed_content(
            model="gemini-embedding-001",
            contents=query,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=768,
            ),
        )
        query_vector = embed_response.embeddings[0].values

        # 2. Query A: Búsqueda semántica pura contra Pinecone (sin filtro), top_k=5
        res_a = self.pinecone_index.query(
            vector=query_vector,
            top_k=5,
            include_metadata=True,
        )
        matches_a = getattr(res_a, "matches", []) or []
        ids_a = [m.id for m in matches_a]
        logger.info(f"[SearchCVTool] Query A (Sin filtro) IDs devueltos: {ids_a}")

        # 3. Query B: Si category, tech_filter o topic_filter vienen poblados, ejecutar Query B con filtro $or
        has_category = bool(category)
        has_tech = bool(tech_filter and len(tech_filter) > 0)
        has_topic = bool(topic_filter and len(topic_filter) > 0)

        matches_b = []
        ids_b = []

        if has_category or has_tech or has_topic:
            conditions = []
            if has_category:
                conditions.append({"category": {"$eq": category}})
            if has_tech:
                conditions.append({"tech_stack": {"$in": tech_filter}})
            if has_topic:
                conditions.append({"tags": {"$in": topic_filter}})

            if len(conditions) == 1:
                meta_filter = conditions[0]
            else:
                meta_filter = {"$or": conditions}

            res_b = self.pinecone_index.query(
                vector=query_vector,
                filter=meta_filter,
                top_k=5,
                include_metadata=True,
            )
            matches_b = getattr(res_b, "matches", []) or []
            ids_b = [m.id for m in matches_b]
            logger.info(f"[SearchCVTool] Query B (Filtro aplicado: {meta_filter}) IDs devueltos: {ids_b}")
        else:
            logger.info("[SearchCVTool] Query B omitida (Sin filtros aplicados).")

        # 4. Fusionar resultados: unión por id sin duplicados, priorizando Query B y completando con Query A hasta top_k=5
        selected_matches = []
        seen_ids = set()

        for match in matches_b:
            if match.id not in seen_ids:
                seen_ids.add(match.id)
                selected_matches.append(match)

        for match in matches_a:
            if match.id not in seen_ids:
                seen_ids.add(match.id)
                selected_matches.append(match)
                if len(selected_matches) == 5:
                    break

        survived_ids = [m.id for m in selected_matches]
        logger.info(f"[SearchCVTool] IDs sobrevivientes tras la fusión final: {survived_ids}")

        # 5. Formatear payload de respuesta al LLM (incluyendo SOLO las 6 llaves especificadas)
        allowed_keys = ["title", "organization", "date_start", "date_end", "category", "content"]
        formatted_results = []

        for match in selected_matches:
            meta = match.metadata or {}
            item = {k: meta[k] for k in allowed_keys if k in meta and meta[k] is not None}
            formatted_results.append(item)

        return {"results": formatted_results}
