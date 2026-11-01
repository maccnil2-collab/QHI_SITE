LEAD_TRANSITIONS = {
    "new": {"contacted", "qualified", "lost"},
    "contacted": {"qualified", "converted", "lost"},
    "qualified": {"contacted", "converted", "lost"},
    "converted": set(),
    "lost": set(),
}


def transition_lead(current: str, target: str) -> str:
    if target not in LEAD_TRANSITIONS.get(current, set()):
        raise ValueError(f"Lead cannot transition from {current} to {target}")
    return target
