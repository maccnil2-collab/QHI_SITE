TRANSITIONS = {
    "requested": {"confirmed", "cancelled"},
    "confirmed": {"sourcing", "cancelled"},
    "sourcing": {"purchased", "cancelled"},
    "purchased": {"in_transit"},
    "in_transit": {"customs"},
    "customs": {"ready_for_delivery"},
    "ready_for_delivery": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


def transition_order(current: str, target: str) -> str:
    allowed = TRANSITIONS.get(current)
    if allowed is None or target not in allowed:
        raise ValueError(f"Order cannot transition from {current} to {target}")
    return target
