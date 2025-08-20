def create_default_embedder(*args, **kwargs):
    """Create a default embedder for embedchain."""
    from .utils import create_default_kwargs
    from .settings import default_embedder_config

    kwargs = create_default_kwargs(kwargs, default_embedder_config)

    # FIXME: ignore provider only support openai compatible mode for now

    from embedchain.config import BaseEmbedderConfig
    from embedchain.embedder.openai import OpenAIEmbedder

    return OpenAIEmbedder(
        config=BaseEmbedderConfig(
            model=kwargs["model"],
            api_key=kwargs["api_key"],
            api_base=kwargs["base_url"],
            vector_dimension=kwargs["dimension"],
        )
    )


def create_default_db(*args, **kwargs):
    """Create a default database for embedchain."""
    from embedchain.config.vector_db.chroma import ChromaDbConfig
    from embedchain.vectordb.chroma import ChromaDB

    return ChromaDB(
        config=ChromaDbConfig(
            collection_name=kwargs.get(
                "collection_name",
                "crewai_tools",
            ),
            dir=kwargs.get("dir"),
            allow_reset=True,
        )
    )
