__all__ = [
    "Flow",
    "start",
    "listen",
    "router",
    "and_",
    "or_",
]

from typing import Any, Optional
from uuid import uuid4

from crewai.flow import start, listen, router, and_, or_, Flow as _Flow


class Flow(_Flow):
    def __init__(
        self,
        tools_retriever: Optional[Any] = None,
        session_id: Optional[str] = None,
        verbose: bool = False,
        **kwargs,
    ):
        from fivcadvisor.tools.utils import retrievers

        if not isinstance(tools_retriever, retrievers.ToolsRetriever):
            raise TypeError("tools_retriever must be an instance of ToolsRetriever")

        self.tools_retriever = tools_retriever
        self.verbose = verbose
        self.session_id = session_id or str(uuid4())

        super().__init__(**kwargs)

    def flow_id(self) -> str:
        return self.session_id
