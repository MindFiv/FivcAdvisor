from typing import Optional, Any

from pydantic import BaseModel
from crewai.flow.flow import (
    Flow,
    listen,
    router,
    start,
)

from ..crews import (
    create_planning_crew,
    create_executing_crew,
    create_tooling_crew,
)
from ..tools.retrievers import ToolsRetriever
from ..outputs import PlanOutput


class ComplexFlowState(BaseModel):
    user_query: str = ""
    plan: Optional[PlanOutput] = None
    final_result: Any = None


class ComplexFlow(Flow[ComplexFlowState]):
    def __init__(
        self,
        tools_retriever: Optional[ToolsRetriever] = None,
        verbose: bool = False,
    ):
        if not isinstance(tools_retriever, ToolsRetriever):
            raise TypeError("tools_retriever must be an instance of ToolsRetriever")

        self.tools_retriever = tools_retriever
        self.verbose = verbose

        super().__init__()

    @start()
    def accept_user_query(self):
        if not self.state.user_query:
            raise ValueError("user_query cannot be empty")

    @listen(accept_user_query)
    def build_plan(self):
        crew = create_planning_crew(
            tools_retriever=self.tools_retriever,
            verbose=self.verbose,
        )
        plan = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.plan = plan.pydantic

    @router(build_plan)
    def execute_plan(self):
        if not self.state.plan:
            raise ValueError("plan cannot be empty")

        # ensure tools for each agent
        agent_tool_retriever = create_tooling_crew(
            tools_retriever=self.tools_retriever,
            verbose=self.verbose,
        )
        for agent in self.state.plan.agents:
            agent_tool_result = agent_tool_retriever.kickoff(
                inputs={"user_query": agent.goal}
            )
            agent.tools = agent_tool_result.pydantic.tools

        crew = create_executing_crew(
            tools_retriever=self.tools_retriever,
            plan=self.state.plan,
            verbose=self.verbose,
        )
        result = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.final_result = result

        return self.state.final_result
