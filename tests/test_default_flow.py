import crewai_hatchery.flows.default as default_mod
from crewai_hatchery.flows import create_default_flow


class DummyRetriever:
    def to_tool(self):
        return object()

    def get_batch(self, names):
        # For tests, avoid passing invalid tool objects into Task
        return []

    def retrieve(self, query):
        return []


class FakeCrew:
    def __init__(self, result):
        self._result = result
        self.inputs_seen = None

    def kickoff(self, inputs=None):
        self.inputs_seen = inputs or {}
        return self._result


def test_default_flow_simple_path(monkeypatch):
    # Assessment returns simple path
    assessment_dict = {
        "task_complexity": "simple",
        "require_director": False,
        "required_tools": ["Basic Calculator"],
        "reasoning": "Trivial definition",
    }

    monkeypatch.setattr(
        default_mod,
        "create_assessing_crew",
        lambda *a, **k: FakeCrew(assessment_dict),
    )

    # Patch simple crew creation to avoid real crewai runtime
    simple_result = "SIMPLE_OK"
    monkeypatch.setattr(
        default_mod,
        "create_simple_crew",
        lambda *a, **k: FakeCrew(simple_result),
    )

    flow = create_default_flow(user_query="what is ml?")
    out = flow.kickoff()
    assert out == simple_result


def test_default_flow_complex_path(monkeypatch):
    # Assessment requires director
    assessment_dict = {
        "task_complexity": "complex",
        "require_director": True,
        "required_tools": [],
        "reasoning": "Needs planning",
    }

    monkeypatch.setattr(
        default_mod,
        "create_assessing_crew",
        lambda *a, **k: FakeCrew(assessment_dict),
    )

    # Planning crew returns a dummy plan dict shaped as PlanOutput
    plan_dict = {
        "agents": [],
        "tasks": [],
    }
    monkeypatch.setattr(
        default_mod,
        "create_planning_crew",
        lambda *a, **k: FakeCrew(plan_dict),
    )

    # Planned crew returns final result
    executing_result = "PLANNED_OK"
    monkeypatch.setattr(
        default_mod,
        "create_executing_crew",
        lambda *a, **k: FakeCrew(executing_result),
    )

    # No need to patch Crew directly in complex path

    flow = create_default_flow(user_query="analyze and create a plan")
    out = flow.kickoff()
    assert out == executing_result
