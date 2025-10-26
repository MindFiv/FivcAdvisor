from typing import Any, List
from uuid import uuid4

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from fivcadvisor.agents import AgentsCreatorBase
from fivcadvisor.utils import Runnable


class TaskRunnable(Runnable):
    def __init__(
        self,
        task_query: str,
        task_output_model: BaseModel,
        task_tools: List[BaseTool],
        agents_creator: AgentsCreatorBase,
        task_id: str | None = None,
        task_name: str = "Default",
        **kwargs,
    ):
        self._id = task_id or str(uuid4())
        self._name = task_name
        self._query = task_query
        self._runnable = agents_creator(
            agent_id=task_id or str(uuid4()),
            agent_name=task_name,
            tools=task_tools,
            response_format=task_output_model,
            **kwargs,
        )

    def id(self) -> str:
        return self._runnable.id

    def run(self, *args: Any, **kwargs: Any) -> str:
        pass

    async def run_async(self, *args: Any, **kwargs: Any) -> str:
        pass
