from typing import Optional

from fivcadvisor.tools.types.configs import ToolsConfig

from fivcadvisor.tools.types.retrievers import ToolsRetriever


class ToolsLoader(object):
    def __init__(
        self,
        retriever: Optional[ToolsRetriever] = None,
        config_file: Optional[str] = None,
        **kwargs,
    ):
        assert retriever is not None
        self.retriever = retriever
        self.config = ToolsConfig(config_file=config_file)
        self.clients = []

    async def load(self):
        for c in self.config.get_clients():
            c.start()

    def cleanup(self):
        raise NotImplementedError()
