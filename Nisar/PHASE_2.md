# Nisar implementation

Nisar owns controller/orchestration, goal understanding, planning, decision-making,
coordination, and next-action selection. The internal workflow is:

```text
monitor -> detector -> recovery goal/plan -> Preethesh selector
        -> Pavan executor -> Mugil verifier -> success or bounded replan
```

`agent/contracts.py` defines the minimal typed state, disruption, goal, plan,
action, execution, and verification contracts. They stay internal to `Nisar/`
until the team agrees to promote them to `Shared/`.

Phase 3 adds a controller-owned `RecoveryContext` and structured lifecycle
events. This preserves the active goal, latest state snapshot identity, failed
action exclusions, and the reason for each recovery transition. Simultaneous
disruptions are ordered deterministically; one prioritized disruption is sent
through a recovery run at a time.

`agent/adapters.py` is protocol-only, not a substitute for teammate systems:

- Preethesh supplies `select_action(goal, plan, state, excluded_action_ids)`.
- Pavan supplies `execute(action, state)` and an `ExecutionResult`.
- Mugil supplies `verify(goal, plan, execution)` and a `VerificationResult`.

Failures exclude the attempted action and trigger a replan; a configurable retry
limit prevents infinite loops. `SampleStateSource` is deterministic development
data and is intended to be replaced by a real state-source adapter. `Monitor`
validates state structure before any detection or planning occurs.

## Test

From `Nisar/`:

```powershell
python -m unittest discover -s tests -v
```
