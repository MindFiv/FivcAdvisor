def create_tools_patch():
    """
    Create a patch for tools that need extra configuration.
    """
    # import embedchain
    import embedchain.app

    from crewai_hatchery.utils import create_output_dir
    from crewai_hatchery.embeddings import (
        create_default_db,
        create_default_embedder,
    )

    embedder = create_default_embedder()

    class _App(embedchain.App):
        def __init__(self, *args, **kwargs):
            if not kwargs.get("db"):
                output_dir = create_output_dir()
                output_dir = output_dir.subdir("db")
                db = create_default_db(dir=str(output_dir))
                kwargs["db"] = db
            kwargs.setdefault("embedding_model", embedder)
            super().__init__(*args, **kwargs)

    embedchain.App = _App
    embedchain.app.App = _App
