# Controller Comparison

This table describes implementation and integration status. It does not claim
that any controller solves a high-fidelity landing task.

| Controller | Status | Integrated in simulator loop | Requires training | Notes |
| --- | --- | --- | --- | --- |
| Fixed throttle | Implemented | Yes | No | Baseline open-loop control |
| Heuristic V1 | Implemented | Yes | No | Rule-based landing policy |
| Heuristic V2 | Implemented | Yes | No | Shows runaway ascent failure mode |
| PID | Planned | No | No | Classical control baseline planned |
| Neural supervised controller | Experimental initial implementation | Yes, experimental | Yes | Supervised pretraining on synthetic telemetry |
| Reinforcement learning | Future work | No | Yes | Future simulator-in-the-loop RL |

The neural controller can execute through the same `compute_throttle(state)`
contract as the heuristic controllers. Its present training labels are
synthetic, and its simulator-loop integration is an engineering foundation for
future evaluation rather than evidence of effective autonomous landing.
