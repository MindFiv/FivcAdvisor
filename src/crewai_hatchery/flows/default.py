from typing import Optional, Any
import json

from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, router, start

from ..crews import (
    create_assessing_crew,
    create_planning_crew,
    create_executing_crew,
    create_simple_crew,
)
from ..tools.retrievers import ToolsRetriever
from ..outputs import (
    AssessmentOutput,
    PlanOutput,
)


class DefaultFlowState(BaseModel):
    user_query: str = ""
    assessment: Optional[AssessmentOutput] = None
    plan: Optional[PlanOutput] = None
    final_result: Any = None


class DefaultFlow(Flow[DefaultFlowState]):
    """
    CrewAI Flow implementation that:
    1) Accepts a user query
    2) Assesses the complexity
    3) Routes to either a simple default crew or a planning flow
    """

    def __init__(
        self,
        user_query: Optional[str] = None,
        tools_retriever: Optional[ToolsRetriever] = None,
        verbose: bool = False,
    ):
        super().__init__()
        self._initial_user_query = user_query
        self.verbose = verbose
        if tools_retriever is None:
            # Create a default retriever if not injected
            from ..tools import create_tools_retriever

            self.tools_retriever = create_tools_retriever()
        else:
            if not isinstance(tools_retriever, ToolsRetriever):
                raise TypeError("tools_retriever must be an instance of ToolsRetriever")
            self.tools_retriever = tools_retriever

    @start()
    def accept_user_query(self) -> str:
        # Prefer kickoff(inputs={"user_query": ...}) or constructor arg
        if self._initial_user_query:
            self.state.user_query = self._initial_user_query
        if not self.state.user_query:
            try:
                self.state.user_query = input("Please enter your request: ").strip()
            except EOFError:
                self.state.user_query = ""
        if not self.state.user_query:
            raise ValueError("User query is required to run the default flow")
        return self.state.user_query

    @listen(accept_user_query)
    def assess_complexity(self, _user_query: str):
        assessing_crew = create_assessing_crew(
            tools_retriever=self.tools_retriever, verbose=self.verbose
        )
        assessment = assessing_crew.kickoff(
            inputs={"user_query": self.state.user_query}
        )
        # Normalize to AssessmentOutput
        try:
            if isinstance(assessment, AssessmentOutput):
                self.state.assessment = assessment
            elif isinstance(assessment, dict):
                self.state.assessment = AssessmentOutput(**assessment)
            else:
                # Some runtimes return an object with a 'pydantic' attribute
                p = getattr(assessment, "pydantic", None)
                if p and isinstance(p, AssessmentOutput):
                    self.state.assessment = p
                elif p and isinstance(p, dict):
                    self.state.assessment = AssessmentOutput(**p)
                else:
                    # Last resort, try JSON
                    self.state.assessment = AssessmentOutput(
                        **json.loads(str(assessment))
                    )
        except Exception as e:
            raise TypeError("assessment must be an instance of AssessmentOutput") from e
        return self.state.assessment

    @router(assess_complexity)
    def route_by_complexity(self):
        if getattr(self.state.assessment, "require_director", False):
            return "complex"
        return "simple"

    @listen("simple")
    def run_simple_path(self):
        simple_crew = create_simple_crew(
            tools_retriever=self.tools_retriever,
            tools_names=self.state.assessment.required_tools,
            verbose=self.verbose,
        )
        result = simple_crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.final_result = result
        return result

    @listen("complex")
    def run_complex_path(self):
        planning_crew = create_planning_crew(
            tools_retriever=self.tools_retriever, verbose=self.verbose
        )
        plan = planning_crew.kickoff(inputs={"user_query": self.state.user_query})
        # Normalize to PlanOutput
        try:
            if isinstance(plan, PlanOutput):
                self.state.plan = plan
            elif isinstance(plan, dict):
                self.state.plan = PlanOutput(**plan)
            else:
                p = getattr(plan, "pydantic", None)
                if p and isinstance(p, PlanOutput):
                    self.state.plan = p
                elif p and isinstance(p, dict):
                    self.state.plan = PlanOutput(**p)
                else:
                    self.state.plan = PlanOutput(**json.loads(str(plan)))
        except Exception as e:
            raise TypeError("plan must be an instance of PlanOutput") from e

        try:
            executing_crew = create_executing_crew(
                plan=plan, tools_retriever=self.tools_retriever, verbose=self.verbose
            )
            final = executing_crew.kickoff(inputs={"user_query": self.state.user_query})
            self.state.final_result = final
            return final
        except Exception as e:
            print(f"Error executing planned crew: {e}")
            # If planned crew creation/execution fails, return the plan as the result
            self.state.final_result = plan
            return plan
