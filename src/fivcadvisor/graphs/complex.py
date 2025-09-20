__all__ = [
    "create_complex_graph",
]

from typing import Optional
from langgraph.graph import StateGraph, START, END

from fivcadvisor.crews import (
    create_planning_crew,
    create_executing_crew,
    create_tooling_crew,
)
from fivcadvisor.models import CrewPlan
from fivcadvisor.graphs.utils import (
    Graph,
    GraphState,
)


class ComplexGraphState(GraphState):
    """State for ComplexGraph."""

    plan: Optional[CrewPlan] = None


def create_complex_graph(*args, **kwargs):
    """Create a ComplexGraph instance.

    Args:
        *args: Additional arguments passed to ComplexGraph
        **kwargs: Additional keyword arguments passed to ComplexGraph

    Returns:
        ComplexGraph: A configured ComplexGraph instance
    """

    def check_prerequisite(state: ComplexGraphState) -> ComplexGraphState:
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

    def build_plan(state: ComplexGraphState) -> ComplexGraphState:
        """Build execution plan."""
        try:
            crew = create_planning_crew(
                tools_retriever=state.tools_retriever,
                session_id=state.session_id,
                verbose=state.verbose,
            )
            plan = crew.kickoff(inputs={"user_query": state.user_query})
            state.plan = CrewPlan(**plan.to_dict())
        except Exception as e:
            state.error = f"Planning failed: {str(e)}"

        return state

    def execute_plan(state: ComplexGraphState) -> ComplexGraphState:
        """Execute the plan."""
        try:
            plan = state.plan
            if not plan:
                raise RuntimeError("plan cannot be empty")

            # Ensure tools for each agent
            agent_tool_retriever = create_tooling_crew(
                tools_retriever=state.tools_retriever,
                session_id=state.session_id,
                verbose=state.verbose,
            )
            for agent in plan.agents:
                agent_tool_result = agent_tool_retriever.kickoff(
                    inputs={"user_query": agent.goal}
                )
                agent.tools = agent_tool_result.pydantic.tools

            crew = create_executing_crew(
                tools_retriever=state.tools_retriever,
                plan=plan,
                session_id=state.session_id,
                verbose=state.verbose,
            )
            crew_result = crew.kickoff(inputs={"user_query": state.user_query})
            crew_result = crew_result.to_dict()
            state.final_result = crew_result
        except Exception as e:
            state.error = f"Execution failed: {str(e)}"

        return state

    graph = StateGraph(ComplexGraphState)

    # Add nodes
    graph.add_node("check_prerequisite", check_prerequisite)
    graph.add_node("build_plan", build_plan)
    graph.add_node("execute_plan", execute_plan)

    # Add edges
    graph.add_edge(START, "check_prerequisite")
    graph.add_edge("check_prerequisite", "build_plan")
    graph.add_edge("build_plan", "execute_plan")
    graph.add_edge("execute_plan", END)

    return Graph(
        name="complex",
        description=(
            "Complex task processing graph\n"
            "LangGraph implementation that:\n"
            "1) Accepts a user query\n"
            "2) Builds a plan\n"
            "3) Executes the plan"
        ),
        builder=graph,
    )
