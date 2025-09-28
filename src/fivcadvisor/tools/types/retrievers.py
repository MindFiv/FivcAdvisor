from typing import List, Optional, Dict

from pydantic import BaseModel, Field
from strands.types.tools import AgentTool
from strands.tools import tool as make_tool
from fivcadvisor import embeddings


class ToolsRetriever(object):
    def __init__(self, db: Optional[embeddings.EmbeddingDB] = None, **kwargs):
        self.max_num = 10  # top k
        self.min_score = 0.0  # min score
        self.tools: dict[str, AgentTool] = {}
        db = db or embeddings.default_embedding_db
        self.collection = db.get_collection("tools")

    def __str__(self):
        return f"ToolsRetriever(num_tools={len(self.tools)})"

    def cleanup(self):
        self.max_num = 10  # top k
        self.min_score = 0.0  # min score
        self.tools.clear()
        self.collection.delete()

    def add(self, tool: AgentTool, **kwargs):
        tool_name = tool.tool_name
        if tool_name in self.tools:
            raise ValueError(f"Duplicate tool name: {tool_name}")

        tool_desc = tool.tool_spec.get("description")
        if not tool_desc:
            raise ValueError(f"Tool description is empty: {tool_name}")

        self.collection.add(
            tool_desc,
            metadata={"__tool__": tool_name},
        )
        self.tools[tool_name] = tool

    def add_batch(self, tools: List[AgentTool]):
        for tool in tools:
            self.add(tool)

    def get(self, name: str) -> Optional[AgentTool]:
        return self.tools.get(name)

    def get_batch(self, names: List[str]) -> List[AgentTool]:
        return [self.get(name) for name in names]

    def get_all(self) -> List[AgentTool]:
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

    def retrieve(self, query: str, *args, **kwargs) -> List[AgentTool]:
        sources = self.collection.search(
            query,
            num_documents=self.retrieve_max_num,
        )

        tool_names = set(
            src["metadata"]["__tool__"]
            for src in sources
            if src["metadata"]["score"] >= self.retrieve_min_score
        )
        return [self.get(name) for name in tool_names]

    def __call__(self, *args, **kwargs) -> List[Dict]:
        tools = self.retrieve(*args, **kwargs)
        return [
            {"name": t.tool_name, "description": t.tool_spec["description"]}
            for t in tools
        ]

    class _ToolSchema(BaseModel):
        query: str = Field(description="The task to find the best tool for")

    def to_tool(self):
        """Convert the retriever to a tool."""
        return make_tool(
            name="Tools Retriever",
            description="Use this tool to retrieve the best tools for a given task",
            inputSchema=self._ToolSchema.model_json_schema(),
            context=False,
        )(self.__call__)
