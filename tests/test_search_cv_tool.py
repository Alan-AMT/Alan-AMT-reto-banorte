from unittest.mock import AsyncMock, MagicMock
import pytest
from infrastructure.adapters.tools.search_cv_tool import SearchCVTool


@pytest.fixture
def mock_genai_client():
    client = MagicMock()
    mock_embed_res = MagicMock()
    mock_embedding = MagicMock()
    mock_embedding.values = [0.1] * 768
    mock_embed_res.embeddings = [mock_embedding]

    client.aio.models.embed_content = AsyncMock(return_value=mock_embed_res)
    return client


@pytest.fixture
def mock_pinecone_index():
    index = MagicMock()
    return index


def create_mock_match(match_id: str, score: float, metadata: dict):
    match = MagicMock()
    match.id = match_id
    match.score = score
    match.metadata = metadata
    return match


@pytest.mark.anyio
async def test_search_cv_tool_query_a_only(mock_genai_client, mock_pinecone_index):
    # Mock Pinecone Query A matches
    match1 = create_mock_match(
        "id_1",
        0.9,
        {
            "title": "Senior Dev",
            "organization": "Tecnoalfa",
            "date_start": "2020",
            "date_end": "2022",
            "category": "experiencia_laboral",
            "content": "Desarrollo en Python",
            "id": "id_1",
            "tech_stack": ["python"],
            "tags": ["backend"],
        },
    )
    match2 = create_mock_match(
        "id_2",
        0.8,
        {
            "title": "Lead Engineer",
            "organization": "Banorte",
            "date_start": "2022",
            "date_end": "2024",
            "category": "experiencia_laboral",
            "content": "Liderazgo de proyectos",
            "id": "id_2",
            "parent_id": "parent_2",
        },
    )
    res_a = MagicMock()
    res_a.matches = [match1, match2]
    mock_pinecone_index.query.return_value = res_a

    tool = SearchCVTool(
        genai_client=mock_genai_client,
        pinecone_index=mock_pinecone_index,
    )

    result = await tool.run(query="Experiencia laboral general")

    assert "results" in result
    assert len(result["results"]) == 2

    # Check allowed keys only
    item1 = result["results"][0]
    assert item1["title"] == "Senior Dev"
    assert item1["organization"] == "Tecnoalfa"
    assert "id" not in item1
    assert "tech_stack" not in item1
    assert "tags" not in item1

    # Verify query was called once without filter
    mock_pinecone_index.query.assert_called_once()
    _, kwargs = mock_pinecone_index.query.call_args
    assert "filter" not in kwargs


@pytest.mark.anyio
async def test_search_cv_tool_query_b_with_or_filter_and_fusion(mock_genai_client, mock_pinecone_index):
    # Match in Query B
    match_b1 = create_mock_match("id_b1", 0.95, {"title": "Python Specialist", "category": "experiencia_laboral", "content": "Python experience"})
    match_b2 = create_mock_match("id_b2", 0.92, {"title": "Backend Dev", "category": "experiencia_laboral", "content": "Django and Fastapi"})

    # Matches in Query A (one duplicate of B, some new ones)
    match_a1 = create_mock_match("id_b1", 0.95, {"title": "Python Specialist", "category": "experiencia_laboral", "content": "Python experience"})
    match_a2 = create_mock_match("id_a2", 0.88, {"title": "Data Engineer", "category": "experiencia_laboral", "content": "Data analysis"})
    match_a3 = create_mock_match("id_a3", 0.85, {"title": "Fullstack Dev", "category": "experiencia_laboral", "content": "React and Node"})

    res_a = MagicMock()
    res_a.matches = [match_a1, match_a2, match_a3]

    res_b = MagicMock()
    res_b.matches = [match_b1, match_b2]

    # Side effect for query: first call is Query A (no filter), second call is Query B (with filter)
    def query_side_effect(**kwargs):
        if "filter" in kwargs:
            return res_b
        return res_a

    mock_pinecone_index.query.side_effect = query_side_effect

    tool = SearchCVTool(
        genai_client=mock_genai_client,
        pinecone_index=mock_pinecone_index,
    )

    result = await tool.run(
        query="Experiencia con Python y liderazgo",
        category="experiencia_laboral",
        tech_filter=["python"],
        topic_filter=["liderazgo"],
    )

    assert "results" in result
    # Order: match_b1, match_b2, match_a2, match_a3 (match_a1 skipped as duplicate of match_b1)
    assert len(result["results"]) == 4
    titles = [res["title"] for res in result["results"]]
    assert titles == ["Python Specialist", "Backend Dev", "Data Engineer", "Fullstack Dev"]

    # Verify Pinecone calls
    assert mock_pinecone_index.query.call_count == 2
    # Verify Query B received $or filter
    filter_arg = mock_pinecone_index.query.call_args_list[1].kwargs["filter"]
    assert "$or" in filter_arg
    assert len(filter_arg["$or"]) == 3
