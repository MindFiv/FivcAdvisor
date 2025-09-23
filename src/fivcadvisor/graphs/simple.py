__all__ = [
    "create_simple_graph",
]

from typing import Optional
from langgraph.graph import StateGraph, START, END

from fivcadvisor.crews import (
    create_assessing_crew,
    create_simple_crew,
)
from fivcadvisor.models import (
    QueryResponse,
    TaskAssessment,
)
from fivcadvisor.graphs.utils import (
    Graph,
    GraphState,
)


class SimpleGraphState(GraphState):
    """State for SimpleGraph."""

    assessment: Optional[TaskAssessment] = None


def create_simple_graph(*args, **kwargs):
    """Create a SimpleGraph instance.

    Args:
        *args: Additional arguments passed to SimpleGraph
        **kwargs: Additional keyword arguments passed to SimpleGraph

    Returns:
        SimpleGraph: A configured SimpleGraph instance
    """

    def check_prerequisite(state: SimpleGraphState) -> SimpleGraphState:
        """Validate user query."""
        if not state.user_query:
            state.error = "user_query cannot be empty"
            raise RuntimeError(state.error)

        if not state.tools_retriever:
            state.error = "tools_retriever cannot be empty"
            raise RuntimeError(state.error)

        if not state.session_id:
            state.error = "session_id cannot be empty"
            raise RuntimeError(state.error)

        return state

    def assess_complexity(state: SimpleGraphState) -> SimpleGraphState:
        """Assess task complexity."""
        try:
            crew = create_assessing_crew(
                tools_retriever=state.tools_retriever,
                session_id=state.session_id,
                verbose=state.verbose,
            )
            assessment = crew.kickoff(inputs={"user_query": state.user_query})
            state.assessment = TaskAssessment(**assessment.to_dict())
            if (
                not state.assessment.require_director
                and not state.assessment.required_tools
                and state.answer
            ):
                state.final_result = QueryResponse(
                    answer=state.assessment.answer,
                    reasoning=state.assessment.reasoning,
                )
        except Exception as e:
            state.error = str(e)

        return state

    def run_if_simple(state: SimpleGraphState) -> SimpleGraphState:
        """Run simple crew if task is simple."""
        if state.final_result:
            # Already have a final result, no need to run
            return state

        try:
            assessment = state.assessment

            if not assessment:
                raise RuntimeError("assessment cannot be empty")

            if assessment.require_director:
                raise RuntimeError("assessment requires director")

            crew_tools = assessment.required_tools
            # TODO: ensure tools are available

            crew = create_simple_crew(
                tools_retriever=state.tools_retriever,
                tools_names=crew_tools,
                session_id=state.session_id,
                verbose=state.verbose,
            )
            crew_result = crew.kickoff(inputs={"user_query": state.user_query})
            crew_result = crew_result.to_dict()
            state.final_result = crew_result
        except Exception as e:
            state.error = f"Simple execution failed: {str(e)}"

        return state

    graph = StateGraph(SimpleGraphState)

    # Add nodes
    graph.add_node("check_prerequisite", check_prerequisite)
    graph.add_node("assess_complexity", assess_complexity)
    graph.add_node("run_if_simple", run_if_simple)

    # Add edges
    graph.add_edge(START, "check_prerequisite")
    graph.add_edge("check_prerequisite", "assess_complexity")
    graph.add_edge("assess_complexity", "run_if_simple")
    graph.add_edge("run_if_simple", END)

    return Graph(
        name="simple",
        description=(
            "Simple task processing graph\n"
            "LangGraph implementation that:\n"
            "1) Accepts a user query\n"
            "2) Assesses the complexity\n"
            "3) Routes to a simple default crew or finishes if complex"
        ),
        builder=graph,
    )
