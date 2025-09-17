from typing import Optional, Any

from pydantic import BaseModel

from fivcadvisor.crews import (
    create_assessing_crew,
    create_simple_crew,
    # create_tooling_crew,
)
from fivcadvisor.models import TaskAssessment
from fivcadvisor.flows.utils.base import Flow, listen, start


class SimpleFlowState(BaseModel):
    user_query: str = ""
    assessment: Optional[TaskAssessment] = None
    final_result: Any = None


class SimpleFlow(Flow[SimpleFlowState]):
    """
    FivcAdvisor Flow implementation that:
    1) Accepts a user query
    2) Assesses the complexity
    3) Routes to a simple default crew or finishes if complex
    """

    name = "simple"

    @start()
    def accept_user_query(self):
        if not self.state.user_query:
            raise ValueError("user_query cannot be empty")

    @listen(accept_user_query)
    def assess_complexity(self):
        crew = create_assessing_crew(
            tools_retriever=self.tools_retriever,
            session_id=self.session_id,
            verbose=self.verbose,
        )
        assessment = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.assessment = TaskAssessment(**assessment.to_dict())

    @listen(assess_complexity)
    def run_if_simple(self):
        if not self.state.assessment:
            raise ValueError("assessment cannot be empty")

        if self.state.assessment.require_director:
            raise ValueError("complex task, need a director")

        tools = self.state.assessment.required_tools
        # crew = create_tooling_crew(
        #     tools_retriever=self.tools_retriever,
        #     verbose=self.verbose,
        # )
        # result = crew.kickoff(inputs={"user_query": self.state.user_query})
        # tools = result.pydantic.tools

        crew = create_simple_crew(
            tools_retriever=self.tools_retriever,
            tools_names=tools,
            session_id=self.session_id,
            verbose=self.verbose,
        )
        result = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.final_result = result

        return self.state.final_result
