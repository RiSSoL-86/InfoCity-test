from unittest.mock import MagicMock, patch

import numpy as np

from services.rag.embeddings import EmbeddingService


async def test_embedding_service_caches_and_encodes() -> None:
    """Cache one model and encode queries and passages in worker threads."""
    model = MagicMock()
    model.encode.side_effect = [
        np.array([0.1, 0.2]),
        np.array([[0.3, 0.4], [0.5, 0.6]]),
    ]
    EmbeddingService._load_model.cache_clear()

    with patch(
        "services.rag.embeddings.SentenceTransformer",
        return_value=model,
    ) as transformer:
        service = EmbeddingService(model_name="test-model")
        service.initialize()
        service.initialize()
        query = await service.embed_query(text="question")
        passages = await service.embed_passages(texts=["one", "two"])

    EmbeddingService._load_model.cache_clear()
    transformer.assert_called_once_with(model_name_or_path="test-model")
    assert query == [0.1, 0.2]
    assert passages == [[0.3, 0.4], [0.5, 0.6]]
    assert model.encode.call_args_list[0].args[0] == "query: question"
    assert model.encode.call_args_list[1].args[0] == [
        "passage: one",
        "passage: two",
    ]
    for call in model.encode.call_args_list:
        assert call.kwargs == {
            "normalize_embeddings": True,
            "convert_to_numpy": True,
        }
