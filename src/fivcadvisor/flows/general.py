from typing import Optional, Any

from pydantic import BaseModel

from fivcadvisor.crews import (
    create_assessing_crew,
    create_planning_crew,
    create_executing_crew,
    create_simple_crew,
)
from fivcadvisor.models import TaskAssessment, CrewPlan
from fivcadvisor.flows.utils.base import Flow, listen, router, start


class GeneralFlowState(BaseModel):
    user_query: str = ""
    assessment: Optional[TaskAssessment] = None
    plan: Optional[CrewPlan] = None
    final_result: Any = None


class GeneralFlow(Flow[GeneralFlowState]):
    """
    FivcAdvisor Flow implementation that:
    1) Accepts a user query
    2) Assesses the complexity
    3) Routes to either a simple default crew or a planning crew
    4) Executes the plan for complex tasks or finishes for simple tasks
    """

    name = "general"

    @start()
    def accept_user_query(self):
        if not self.state.user_query:
            raise ValueError("user_query cannot be empty")

    @router(accept_user_query)
    def assess_complexity(self):
        crew = create_assessing_crew(
            tools_retriever=self.tools_retriever,
            session_id=self.session_id,
            verbose=self.verbose,
        )
        crew_result = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.assessment = TaskAssessment(**crew_result.to_dict())
        return (
            "run_simple"
            if not self.state.assessment.require_director
            else "plan_complex"
        )

    @listen(assess_complexity)
    def run_simple(self):
        crew = create_simple_crew(
            tools_retriever=self.tools_retriever,
            tools_names=self.state.assessment.required_tools,
            session_id=self.session_id,
            verbose=self.verbose,
        )
        crew_result = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.final_result = crew_result.to_dict()
        return self.state.final_result

    @listen(assess_complexity)
    def plan_complex(self):
        crew = create_planning_crew(
            tools_retriever=self.tools_retriever,
            session_id=self.session_id,
            verbose=self.verbose,
        )
        crew_result = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.plan = CrewPlan(**crew_result.to_dict())

    @listen(plan_complex)
    def run_complex(self):
        if not self.state.plan:
            raise ValueError("plan cannot be empty")

        crew = create_executing_crew(
            tools_retriever=self.tools_retriever,
            plan=self.state.plan,
            session_id=self.session_id,
            verbose=self.verbose,
        )
        crew_result = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.final_result = crew_result.to_dict()
        return self.state.final_result
