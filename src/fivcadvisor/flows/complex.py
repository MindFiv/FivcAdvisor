from typing import Optional, Any

from pydantic import BaseModel

from fivcadvisor.crews import (
    create_planning_crew,
    create_executing_crew,
    create_tooling_crew,
)
from fivcadvisor.models import CrewPlan
from fivcadvisor.flows.utils.base import Flow, listen, start


class ComplexFlowState(BaseModel):
    user_query: str = ""
    plan: Optional[CrewPlan] = None
    final_result: Any = None


class ComplexFlow(Flow[ComplexFlowState]):
    """
    FivcAdvisor Flow implementation that:
    1) Accepts a user query
    2) Builds a plan
    3) Executes the plan
    """

    name = "complex"

    @start()
    def accept_user_query(self):
        if not self.state.user_query:
            raise ValueError("user_query cannot be empty")

    @listen(accept_user_query)
    def build_plan(self):
        crew = create_planning_crew(
            tools_retriever=self.tools_retriever,
            verbose=self.verbose,
            session_id=self.session_id,
        )
        plan = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.plan = CrewPlan(**plan.to_dict())

    @listen(build_plan)
    def execute_plan(self):
        if not self.state.plan:
            raise ValueError("plan cannot be empty")

        # ensure tools for each agent
        agent_tool_retriever = create_tooling_crew(
            tools_retriever=self.tools_retriever,
            verbose=self.verbose,
            session_id=self.session_id,
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
            session_id=self.session_id,
        )
        result = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.final_result = result.to_dict()

        return self.state.final_result
