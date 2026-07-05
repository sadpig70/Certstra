#!/usr/bin/env python3
"""Staged release schedule (machine M12 — the NEW machine for this cluster).

Generalizes ReleaseMesh/LazarettoStage staged rollout: each stage rolls out to a
cohort, observes incidents over a window, and gates go/no-go. Rollout halts on the
first gate failure. Deterministic; `now` injected.
"""


def plan_stages(release, schedule, now=""):
    """Plan a staged rollout. Each stage: {name, cohort_pct, observation_window,
    observed_incidents, incident_threshold}. Returns the plan + halt/complete state."""
    plan = []
    cumulative = 0.0
    halted = False
    for i, st in enumerate(schedule):
        cohort = st.get("cohort_pct", 0)
        cumulative += cohort
        observed = st.get("observed_incidents", 0)
        threshold = st.get("incident_threshold", 0)
        gate = "go" if observed <= threshold else "halt"
        plan.append({
            "stage": st.get("name", f"stage-{i}"),
            "cohort_pct": cohort, "cumulative_pct": cumulative,
            "observation_window": st.get("observation_window"),
            "observed_incidents": observed, "incident_threshold": threshold,
            "gate": gate,
        })
        if gate == "halt":
            halted = True
            break
    complete = (not halted) and bool(plan) and abs(cumulative - 100.0) < 1e-6
    return {"release": release, "stages": plan, "halted": halted,
            "rollout_complete": complete, "planned_at": now}
