__all__ = [
    "create_general_graph",
]

from typing import Optional
from langgraph.graph import StateGraph, START, END

from fivcadvisor.crews import (
    create_assessing_crew,
    create_planning_crew,
    create_executing_crew,
    create_simple_crew,
)
from fivcadvisor.models import (
    TaskAssessment,
    TaskPlan,
)
from fivcadvisor.graphs.utils import (
    Graph,
    GraphState,
)


class GeneralGraphState(GraphState):
    """State for GeneralGraph."""

    assessment: Optional[TaskAssessment] = None
    plan: Optional[TaskPlan] = None


def create_general_graph(*args, **kwargs):
    """Create a GeneralGraph instance.

    Args:
        *args: Additional arguments passed to GeneralGraph
        **kwargs: Additional keyword arguments passed to GeneralGraph

    Returns:
        GeneralGraph: A configured GeneralGraph instance
    """

    def check_prerequisite(state: GeneralGraphState) -> GeneralGraphState:
        """Validate user query."""
        if not state.user_query:
            state.error = "user_query cannot be empty"
            raise RuntimeError(state.error)

        if not state.tools_retriever:
            state.error = "tools_retriever cannot be empty"
            raise RuntimeError(state.error)

        if not state.run_id:
            state.error = "run_id cannot be empty"
            raise RuntimeError(state.error)

        return state

    def assess_complexity(state: GeneralGraphState) -> GeneralGraphState:
        """Assess task complexity."""
        try:
            crew = create_assessing_crew(
                tools_retriever=state.tools_retriever,
                run_id=state.run_id,
                verbose=state.verbose,
            )
            assessment = crew.kickoff(inputs={"user_query": state.user_query})
            state.assessment = TaskAssessment(**assessment.to_dict())
            if (
                not state.assessment.require_director
                and not state.assessment.required_tools
                and state.answer
            ):
                state.final_result = state.assessment.answer
        except Exception as e:
            state.error = f"Assessment failed: {str(e)}"

        return state

    def route_after_assessment(state: GeneralGraphState) -> str:
        """Route based on assessment result."""
        if state.error or state.final_result:
            return "run_simple"  # Default fallback

        assessment = state.assessment
        if not assessment:
            return "run_simple"  # Default fallback

        return "run_simple" if not assessment.require_director else "plan_complex"

    def run_simple(state: GeneralGraphState) -> GeneralGraphState:
        """Run simple crew for simple tasks."""
        if state.final_result:
            # Already have a final result, no need to run
            return state

        try:
            assessment = state.assessment
            if not assessment:
                raise RuntimeError("assessment cannot be empty")

            crew_tools = assessment.required_tools
            # TODO: ensure tools are available

            crew = create_simple_crew(
                tools_retriever=state.tools_retriever,
                tools_names=crew_tools,
                run_id=state.run_id,
                verbose=state.verbose,
            )
            crew_result = crew.kickoff(inputs={"user_query": state.user_query})
            state.final_result = str(crew_result)
        except Exception as e:
            state.error = f"Simple execution failed: {str(e)}"

        return state

    def plan_complex(state: GeneralGraphState) -> GeneralGraphState:
        """Plan complex tasks."""
        try:
            crew = create_planning_crew(
                tools_retriever=state.tools_retriever,
                run_id=state.run_id,
                verbose=state.verbose,
            )
            plan = crew.kickoff(inputs={"user_query": state.user_query})
            state.plan = TaskPlan(**plan.to_dict())
        except Exception as e:
            state.error = f"Planning failed: {str(e)}"

        return state

    def run_complex(state: GeneralGraphState) -> GeneralGraphState:
        """Execute complex tasks based on plan."""
        try:
            plan = state.plan
            if not plan:
                raise RuntimeError("plan cannot be empty")

            crew = create_executing_crew(
                tools_retriever=state.tools_retriever,
                plan=plan,
                run_id=state.run_id,
                verbose=state.verbose,
            )
            crew_result = crew.kickoff(inputs={"user_query": state.user_query})
            state.final_result = str(crew_result)
        except Exception as e:
            state.error = f"Complex execution failed: {str(e)}"

        return state

    graph = StateGraph(GeneralGraphState)

    # Add nodes
    graph.add_node("check_prerequisite", check_prerequisite)
    graph.add_node("assess_complexity", assess_complexity)
    graph.add_node("run_simple", run_simple)
    graph.add_node("plan_complex", plan_complex)
    graph.add_node("run_complex", run_complex)

    # Add edges
    graph.add_edge(START, "check_prerequisite")
    graph.add_edge("check_prerequisite", "assess_complexity")

    # Add conditional edge for routing
    graph.add_conditional_edges(
        "assess_complexity",
        route_after_assessment,
        {
            "run_simple": "run_simple",
            "plan_complex": "plan_complex",
        },
    )

    graph.add_edge("run_simple", END)
    graph.add_edge("plan_complex", "run_complex")
    graph.add_edge("run_complex", END)

    return Graph(
        name="general",
        description=(
            "General task processing graph\n"
            "LangGraph implementation that:\n"
            "1) Accepts a user query\n"
            "2) Assesses the complexity\n"
            "3) Routes to either a simple default crew or a planning crew\n"
            "4) Executes the plan for complex tasks or finishes for simple tasks"
        ),
        builder=graph,
    )
