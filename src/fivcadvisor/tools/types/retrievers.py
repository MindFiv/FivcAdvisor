from typing import List, Optional, Dict, Callable

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, tool as make_tool
from fivcadvisor import embeddings
from fivcadvisor.tools.types.bundles import ToolsBundleManager, ToolsBundle


class ToolsRetriever(object):
    """
    A retriever for tools with optional bundle expansion support.
    """

    def __init__(
        self,
        db: Optional[embeddings.EmbeddingDB] = None,
        bundle_manager: Optional[ToolsBundleManager] = None,
        **kwargs,
    ):
        self.max_num = 10  # top k
        self.min_score = 0.0  # min score
        self.tools: dict[str, BaseTool] = {}
        db = db or embeddings.default_embedding_db
        self.collection = db.get_collection("tools")
        self.collection.clear()  # clean up any old data

        # Bundle manager for tool expansion
        self.bundle_manager = bundle_manager or ToolsBundleManager()

    def __str__(self):
        return f"ToolsRetriever(num_tools={len(self.tools)})"

    def cleanup(self):
        self.max_num = 10  # top k
        self.min_score = 0.0  # min score
        self.tools.clear()
        self.collection.clear()
        self.bundle_manager.cleanup()

    def add(self, tool: BaseTool, tool_bundle: str = "", **kwargs):
        """
        Add a tool to the retriever.

        Args:
            tool: The tool to add
            tool_bundle: Optional bundle name for this tool
        """
        tool_name = tool.name
        if tool_name in self.tools:
            raise ValueError(f"Duplicate tool name: {tool_name}")

        tool_desc = tool.description
        if not tool_desc:
            raise ValueError(f"Tool description is empty: {tool_name}")

        self.collection.add(
            tool_desc,
            metadata={"__tool__": tool_name},
        )
        self.tools[tool_name] = tool

        # Register tool in bundle if bundle is specified
        if tool_bundle:
            bundle = self.bundle_manager.get_bundle(tool_bundle)
            if bundle is None:
                # Auto-create bundle if it doesn't exist
                self.bundle_manager.create_bundle(tool_bundle)
            # Use the manager's method to add tool and update mapping
            self.bundle_manager.add_tool_to_bundle(tool_bundle, tool)

        print(f"Total Docs {self.collection.count()} in ToolsRetriever")

    def add_batch(self, tools: List[BaseTool], tool_bundle: str = ""):
        """Add multiple tools, optionally to the same bundle."""
        for tool in tools:
            self.add(tool, tool_bundle=tool_bundle)

    def get(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    def get_batch(self, names: List[str]) -> List[BaseTool]:
        return [self.get(name) for name in names]

    def get_all(self) -> List[BaseTool]:
        return list(self.tools.values())

    @property
    def retrieve_min_score(self):
        return self.min_score

    @retrieve_min_score.setter
    def retrieve_min_score(self, value: float):
        self.min_score = value

    @property
    def retrieve_max_num(self):
        return self.max_num

    @retrieve_max_num.setter
    def retrieve_max_num(self, value: int):
        self.max_num = value

    def retrieve(
        self,
        query: str,
        include_bundles: bool = False,
        bundle_filter: Optional[Callable[[ToolsBundle], bool]] = None,
        *args,
        **kwargs,
    ) -> List[BaseTool]:
        """
        Retrieve tools for a query.

        Args:
            query: The query string
            include_bundles: Whether to expand results to include related bundle tools
            bundle_filter: Optional filter for bundle expansion
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            List of relevant tools
        """
        sources = self.collection.search(
            query,
            num_documents=self.retrieve_max_num,
        )

        tool_names = set(
            src["metadata"]["__tool__"]
            for src in sources
            if src["score"] >= self.retrieve_min_score
        )
        tools = [self.get(name) for name in tool_names]

        # Expand with bundle tools if requested
        if include_bundles:
            tools = self.bundle_manager.expand_tools(
                tools, include_bundles=True, bundle_filter=bundle_filter
            )

        return tools

    def __call__(self, *args, **kwargs) -> List[Dict]:
        tools = self.retrieve(*args, **kwargs)
        return [{"name": t.name, "description": t.description} for t in tools]

    class _ToolSchema(BaseModel):
        query: str = Field(description="The task to find the best tool for")

    def to_tool(self):
        """Convert the retriever to a tool."""

        @make_tool
        def tools_retriever(query: str) -> str:
            """Use this tool to retrieve the best tools for a given task"""
            return str(self.retrieve(query))

        return tools_retriever
