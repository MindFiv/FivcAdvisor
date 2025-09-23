from typing import List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ToolsRetriever(object):
    def __init__(self, *args, **kwargs):
        self.max_num = 10  # top k
        self.min_score = 0.0  # min score
        self.tools: dict[str, BaseTool] = {}

        from fivcadvisor import embeddings

        self.app = embeddings.create_default_app(*args, **kwargs)
        # self.app.reset()

    def cleanup(self):
        self.max_num = 10  # top k
        self.min_score = 0.0  # min score
        self.tools.clear()
        self.app.reset()

    def add(self, tool: BaseTool, **kwargs):
        if tool.name in self.tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")

        self.app.add(
            tool.description,
            data_type="text",
            metadata={"__tool__": tool.name},
        )
        self.tools[tool.name] = tool

    def add_batch(self, tools: List[BaseTool]):
        for tool in tools:
            self.add(tool)

    def get(self, name: str) -> Optional[BaseTool]:
        return self.tools.get(name)

    def get_batch(self, names: List[str]) -> List[BaseTool]:
        return [self.get(name) for name in names]

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

    def retrieve(self, query: str, *args, **kwargs) -> List[BaseTool]:
        sources = self.app.search(
            query,
            num_documents=self.retrieve_max_num,
        )

        tool_names = set(
            src["metadata"]["__tool__"]
            for src in sources
            if src["metadata"]["score"] >= self.retrieve_min_score
        )
        return [self.get(name) for name in tool_names]

    def __call__(self, *args, **kwargs):
        tools = self.retrieve(*args, **kwargs)
        return [{"name": tool.name, "description": tool.description} for tool in tools]

    class _ToolSchema(BaseModel):
        query: str = Field(description="The task to find the best tool for")

    def to_tool(self):
        from crewai.tools.base_tool import Tool

        return Tool(
            name="Tools Retriever",
            description="Use this tool to retrieve the best tool for a given task",
            func=self,
            args_schema=self._ToolSchema,
            result_as_answer=False,
            # max_usage_count=0,
            # current_usage_count=0,
        )
