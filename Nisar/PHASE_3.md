# Phase 3: integration readiness

Phase 3 strengthens Nisar's orchestration without implementing teammate-owned
systems. The controller records a structured `RecoveryContext` across attempts:
the active disruption and goal, action exclusions, the latest state snapshot,
and lifecycle events from monitoring through termination.

## Intended lifecycle

```text
monitor and validate state
  -> detect and deterministically prioritize disruptions
  -> create a recovery goal and state-bound plan
  -> Preethesh selects an eligible action
  -> Pavan executes it and may return updated state
  -> Mugil verifies the recovery goal
  -> recover, or record the failed action and replan within the retry limit
```

The controller consumes `ExecutionResult.updated_state` on the next attempt;
when it is absent, it asks the monitor for a fresh snapshot. An unavailable
action is recorded explicitly and excluded just like another failed action.

## Deferred integration decisions

- Actual action payload fields, alternative candidates, and optimization scores
  await Preethesh and Pavan's published interfaces.
- Full-state or multi-disruption verification scope awaits Mugil's interface.
- These internal contracts stay in `Nisar/` until the team agrees on `Shared/`
  ownership and schema compatibility.
