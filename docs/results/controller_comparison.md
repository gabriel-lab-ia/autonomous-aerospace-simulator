# Controller Comparison

This table describes implementation and integration status. It does not claim
that any controller solves a high-fidelity landing task.

| Controller | Status | Integrated in simulator loop | Requires training | Benchmark included | Notes |
| --- | --- | --- | --- | --- | --- |
| Fixed throttle | Implemented | Yes | No | Yes | Open-loop baseline |
| Heuristic V1 | Implemented | Yes | No | Yes | Rule-based baseline |
| Heuristic V2 | Implemented | Yes | No | Yes | Known runaway ascent failure mode |
| PID | Implemented | Yes | No | Yes | Classical feedback baseline |
| Neural supervised controller | Experimental | Yes | Yes | Yes/Conditional | Uses trained checkpoint if available |
| Reinforcement learning | Future work | No | Yes | No | Planned simulator-in-the-loop learning |

The neural controller uses the same `compute_throttle(state)` contract as the
heuristic and PID controllers. Its labels are synthetic or extracted from
reproducible simulator telemetry. This is an engineering foundation, not
evidence of effective autonomous landing. See the
[real trajectory benchmark](controller_trajectory_comparison.md).
