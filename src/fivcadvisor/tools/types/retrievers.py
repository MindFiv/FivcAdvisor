from typing import List, Optional, Dict

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, tool as make_tool
from fivcadvisor import embeddings


class ToolsRetriever(object):
    """
    A retriever for tools.
    """

    def __init__(
        self,
        db: Optional[embeddings.EmbeddingDB] = None,
        **kwargs,
    ):
        self.max_num = 10  # top k
        self.min_score = 0.0  # min score
        self.tools: dict[str, BaseTool] = {}
        db = db or embeddings.default_embedding_db
        self.collection = db.get_collection("tools")
        self.collection.clear()  # clean up any old data

    def __str__(self):
        return f"ToolsRetriever(num_tools={len(self.tools)})"

    def cleanup(self):
        self.max_num = 10  # top k
        self.min_score = 1.0  # min score
        self.tools.clear()
        self.collection.clear()

    def add(self, tool: BaseTool, **kwargs):
        """
        Add a tool to the retriever.

        Args:
            tool: The tool to add
        """

        if not tool.handle_tool_error:
            tool.handle_tool_error = True

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

        print(f"Total Docs {self.collection.count()} in ToolsRetriever")

    def add_batch(self, tools: List[BaseTool], **kwargs):
        """Add multiple tools."""
        for tool in tools:
            self.add(tool)

    def get(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    def get_batch(self, names: List[str]) -> List[BaseTool]:
        return [self.get(name) for name in names]

    def get_all(self) -> List[BaseTool]:
        return list(self.tools.values())

    def remove(self, name: str):
        """
        Remove a tool from the retriever.

        Removes the tool from:
        - self.tools dictionary
        - embedding collection (by metadata)

        Args:
            name: The name of the tool to remove

        Raises:
            ValueError: If the tool doesn't exist
        """
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")

        # Remove from tools dictionary
        del self.tools[name]

        # Remove from embedding collection by searching and deleting
        # We need to find all documents with this tool's metadata and delete them
        all_docs = self.collection.collection.get()
        ids_to_delete = [
            doc_id
            for doc_id, metadata in zip(all_docs["ids"], all_docs["metadatas"])
            if metadata and metadata.get("__tool__") == name
        ]

        if ids_to_delete:
            self.collection.collection.delete(ids=ids_to_delete)

        print(
            f"Removed tool '{name}'. Total Docs {self.collection.count()} in ToolsRetriever"
        )

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
        *args,
        **kwargs,
    ) -> List[BaseTool]:
        """
        Retrieve tools for a query.

        Args:
            query: The query string
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
