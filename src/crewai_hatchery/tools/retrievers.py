from typing import List, Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ToolsRetriever(object):
    def __init__(self, *args, **kwargs):
        self.max_num = 5  # top k
        self.min_score = 1.5  # min score
        self.tools: dict[str, BaseTool] = {}
        self.app = self._init_app(**kwargs)
        self.app.reset()

    @staticmethod
    def _init_app(
        db=None,
        embedder=None,
        reset=True,
        **kwargs,
    ):
        # create embedchain app
        if not db:
            from crewai_hatchery.utils import create_output_dir
            from crewai_hatchery.embeddings import create_default_db

            output_dir = create_output_dir()
            output_dir = output_dir.subdir("db")
            db = create_default_db(dir=str(output_dir))  # reset db each time

        if not embedder:
            from crewai_hatchery.embeddings import create_default_embedder

            embedder = create_default_embedder()

        from embedchain import App

        return App(db=db, embedding_model=embedder)

    def cleanup(self):
        self.max_num = 5  # top k
        self.min_score = 1.5  # min score
        self.tools.clear()
        self.app.reset()

    def add(self, tool: BaseTool, **kwargs):
        if tool.name in self.tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")

        from embedchain.models.data_type import DataType

        self.app.add(
            tool.description,
            data_type=DataType.TEXT.value,
            metadata={"__tool__": tool.name},
        )
        self.tools[tool.name] = tool

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

        # import json
        # print(json.dumps(sources))

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
