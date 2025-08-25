from typing import Optional, Any

from pydantic import BaseModel
from crewai.flow.flow import (
    Flow,
    listen,
    router,
    start,
)

from ..crews import (
    create_assessing_crew,
    create_simple_crew,
)
from ..tools.retrievers import ToolsRetriever
from ..outputs import AssessmentOutput


class DefaultSimpleFlowState(BaseModel):
    user_query: str = ""
    assessment: Optional[AssessmentOutput] = None
    final_result: Any = None


class DefaultSimpleFlow(Flow[DefaultSimpleFlowState]):
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
    def assess_complexity(self):
        crew = create_assessing_crew(
            tools_retriever=self.tools_retriever,
            verbose=self.verbose,
        )
        assessment = crew.kickoff(inputs={"user_query": self.state.user_query})
        self.state.assessment = assessment.pydantic

    @router(assess_complexity)
    def run_if_simple(self):
        if not self.state.assessment:
            raise ValueError("assessment cannot be empty")

        if self.state.assessment.require_director:
            self.state.final_result = "user query is too complex to handle"

        else:
            crew = create_simple_crew(
                tools_retriever=self.tools_retriever,
                tools_names=self.state.assessment.required_tools,
                verbose=self.verbose,
            )
            result = crew.kickoff(inputs={"user_query": self.state.user_query})
            self.state.final_result = result.raw

        return self.state.final_result
