"""
Monkey-patch qdrant-client 1.17+ to add search()/search_batch()
for compatibility with llama-index-vector-stores-qdrant 0.3.3
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from typing import List, Union
import warnings

# Only patch if search is missing
if not hasattr(QdrantClient, "search") or not callable(getattr(QdrantClient, "search", None)):

    def _search_request_to_query_request(req: rest.SearchRequest) -> rest.QueryRequest:
        """Convert old SearchRequest to new QueryRequest."""
        kwargs = {
            "query": None,
            "using": None,
        }

        # Handle vector field
        vector = getattr(req, "vector", None)
        if vector is not None:
            if isinstance(vector, rest.NamedVector):
                kwargs["query"] = vector.vector
                kwargs["using"] = vector.name
            elif isinstance(vector, rest.NamedSparseVector):
                kwargs["query"] = vector.vector
                kwargs["using"] = vector.name
            elif isinstance(vector, list):
                kwargs["query"] = vector
            else:
                kwargs["query"] = vector

        # Map remaining fields
        if req.limit is not None:
            kwargs["limit"] = req.limit
        if req.filter is not None:
            kwargs["filter"] = req.filter
        if req.with_payload is not None:
            kwargs["with_payload"] = req.with_payload
        if req.with_vector is not None:
            kwargs["with_vectors"] = req.with_vector
        if req.score_threshold is not None:
            kwargs["score_threshold"] = req.score_threshold
        if req.offset is not None:
            kwargs["offset"] = req.offset
        if req.params is not None:
            kwargs["search_params"] = req.params

        return rest.QueryRequest(**kwargs)

    def search(
        self,
        collection_name: str,
        query_vector: Union[List[float], rest.NamedVector, rest.NamedSparseVector],
        query_filter=None,
        search_params=None,
        limit: int = 10,
        offset=None,
        with_payload=True,
        with_vector=False,
        score_threshold=None,
        **kwargs,
    ):
        """Compatibility wrapper around query_points."""
        query = query_vector
        using = None
        if isinstance(query_vector, rest.NamedVector):
            query = query_vector.vector
            using = query_vector.name
        elif isinstance(query_vector, rest.NamedSparseVector):
            query = query_vector.vector
            using = query_vector.name

        result = self.query_points(
            collection_name=collection_name,
            query=query,
            using=using,
            query_filter=query_filter,
            search_params=search_params,
            limit=limit,
            offset=offset,
            with_payload=with_payload,
            with_vectors=with_vector,
            score_threshold=score_threshold,
            **kwargs,
        )
        return result.points

    def search_batch(
        self,
        collection_name: str,
        requests: List[rest.SearchRequest],
        **kwargs,
    ):
        """Compatibility wrapper around query_batch_points."""
        query_requests = [_search_request_to_query_request(r) for r in requests]
        results = self.query_batch_points(
            collection_name=collection_name,
            requests=query_requests,
            **kwargs,
        )
        # query_batch_points returns List[QueryResponse]
        # search_batch should return List[List[ScoredPoint]]
        return [r.points for r in results]

    QdrantClient.search = search
    QdrantClient.search_batch = search_batch
    warnings.warn(
        "Monkey-patched qdrant-client 1.17+ with search/search_batch compatibility layer for llama-index",
        RuntimeWarning,
        stacklevel=2,
    )
