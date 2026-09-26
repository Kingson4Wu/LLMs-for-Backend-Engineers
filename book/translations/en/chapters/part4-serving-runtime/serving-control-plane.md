# Serving Control Plane: Routing, Scaling, and Reliable Delivery

An inference engine executes a model on one device or a group of devices. It does not automatically decide which model should serve a request, when overload traffic should be rejected, when a new replica should start, or how to reverse a bad release. Those decisions form the **serving control plane**. It turns model computation into a service with objectives, boundaries, and operations.

A control plane is not a particular gateway or Kubernetes product. It is a set of responsibilities: recognize what a request needs, select executable resources, limit work the system cannot sustain, change resource scale, and maintain a service promise with versions, metrics, and recovery.

## What data plane and control plane do

An online service has two cooperating paths:

```text
request → gateway / router → queue and policy → inference engine / model replica → streaming response
                │                 │                       │
                └── control plane: selection, limits, scaling, release, observation ──┘

data plane: tokenization, prefill, decode, KV-cache management, and output
control plane: selection of model and resources, plus long-lived capacity and version state
```

The boundary need not be a process boundary: a small service can perform all responsibilities in one program, while a large platform separates gateways, schedulers, model servers, and cluster managers. Throughput optimization inside a model server does not replace traffic isolation, release policy, or quota management.

Two time scales must also be distinguished. A **cluster scheduler** assigns a group of machines and accelerators to a model service or training job; it considers placement, quotas, and failure domains and commonly changes on a seconds-to-minutes scale. An **inference scheduler** works within a device group it already owns, deciding which request, batch, or decode step runs next while managing KV cache in millisecond-scale iterations. The former cannot replace the latter: even after a cluster assigns enough GPUs, an inference engine must still handle online requests of different length and state.

## Routing is not choosing a random machine

Routing must first match model and capability: the destination must support the required model version, modality, context length, adapter, and safety policy. It then chooses among capable instances:

| Routing signal | Purpose |
| --- | --- |
| Queue, active sequences, and remaining KV space | Avoid an instance without execution capacity |
| Model, version, and hardware capability | Ensure the request can execute correctly |
| Priority, tenant quota, and cost policy | Protect important traffic and prevent one user exhausting resources |
| Session, shared prefix, or cache placement | Reduce state movement and repeated prefill |
| Region, data boundary, and availability zone | Meet latency, compliance, and fault-isolation requirements |

Routing on average CPU or GPU utilization alone often misses the pressure that matters. A device can have low compute utilization while its KV cache is full of long contexts; a newly created replica may still be loading a model. Routing needs inference-workload state, not the assumptions of a stateless web service.

### Where Should a Request Go When Cache Exists?

For services with long context, multi-turn conversations, or fixed tool definitions, a router often chooses among three paths:

| Path | Suitable when | Main cost |
| --- | --- | --- |
| Route to an instance with a local cache hit | Saved prefill exceeds additional queueing | Can sacrifice load balance |
| Transfer state to a less busy instance | State is small or the link is fast enough | Uses network capacity and adds failure boundaries |
| Route to an idle instance and re-prefill | Recomputation is faster than waiting or movement, or state should not be shared | Repeated computation and higher TTFT |

Cache affinity is never universally correct. Compare a hit with queue time, state size, network path, tenant isolation, and failure recovery. Permanently binding a session to one machine weakens elasticity; ignoring cache location repeats long prefixes. State-aware routing makes this trade-off measurable.

## How to Organize a Serving Unit

A control plane manages more than a machine count: it must define what a routable serving unit is. Three common shapes are:

| Shape | How a request executes | Suitable for | Main cost |
| --- | --- | --- | --- |
| Complete replica | One device group holds a complete model and independently handles requests | The model fits on one machine or fixed device group and horizontal scale is needed | Weights are replicated and caches can fragment |
| Sharded inference instance | Multiple cards or machines jointly hold a model and execute one request | One card cannot hold the model or one request needs greater resources | Communication enters the critical path; topology and failure matter more |
| Stage pools | Separate instances process prefill and decode | Long inputs and sustained generation have distinctly different load | KV state must transfer and the two pools need coordinated capacity |

These shapes can be combined. A service can have many complete replicas, each internally made of several cards; stage pools become worthwhile only when measured prefill/decode interference calls for them. A control plane must know these boundaries so that scaling a replica, enlarging a device group, and adding capacity to one stage are different actions rather than one generic “scale out.”

## Why scaling is slower than web-service scaling

A normal stateless replica can accept traffic soon after it starts. A model replica may need to fetch weights, initialize its runtime, allocate accelerator memory, and warm up. Effective scale-out can therefore take much longer than creating a process. Scaling only after a queue is already long leaves users waiting through that delay.

```text
load rises → confirmation window → allocate device → load and warm model → health check → accept traffic
```

A useful capacity policy combines baseline resident capacity, queues and rate limits for bursts, scale-out triggers, degradation or fallback during loading, and draining rules for scale-in. Scale-in should not kill a replica that is generating: stop assigning new requests, let existing ones finish or cancel them according to an explicit contract, then release their KV state. High availability also needs fault-domain separation among replicas, routers, and dependencies.

## Release, rollback, and reproducible behavior

Results are not determined by weights alone. Model version, tokenizer, prompt template, tool schema, retrieval index, sampling parameters, inference-engine version, and routing rules together define a deliverable behavior. Changing any one can change quality, latency, cost, or a safety boundary.

Define the comparison and stop conditions before expanding traffic:

```text
candidate configuration → offline evaluation → small traffic → more traffic → full rollout
                                           │                  │
                                           └─ quality, errors, TTFT, or cost breach → rollback
```

Rollback needs the same granularity as release; reverting weights alone is insufficient. Systems with sessions and caches also need rules for old sessions, cache reuse, and in-flight requests. Without these boundaries, “one-click rollback” is incomplete.

## What to protect under overload and failure

Timeouts, client disconnects, slow tool calls, and failed instances are normal. Reliability starts by asking whether a request still has value, may already have executed, and whether retry would amplify load—not by retrying indefinitely.

| Situation | Control point to consider |
| --- | --- |
| Client cancellation or disconnect | Stop decode promptly and release KV cache and quota |
| Queue keeps growing | Rate limits, queue bounds, priority, degradation, or fast failure |
| Instance failure | Health checks, stop routing, retry boundary, and remaining capacity |
| Downstream dependency slows | Total time budget, circuit breaking, and isolation to avoid occupying model resources |
| Release regresses quality or cost | Comparable metrics, traffic gates, and complete configuration rollback |

Generated requests should not be retried blindly: the same semantic request can yield different text, and tool calls can create duplicate side effects. Retry depends on an idempotency key, execution stage, and business meaning. Timeout is also not one number; queueing, model generation, and downstream calls must share an explicit total time budget.

## Observability makes control possible

Control needs observable state. At minimum, group request volume, rejection rate, queues, TTFT, TPOT, completion time, active sequences, KV cache, device memory, cancellation, errors, and token cost by model, version, tenant, length range, and priority. Averages cannot characterize interactive experience; examine tail latency and behavior under bursts.

Metrics show that a target has been missed; traces explain which components a request crossed; logs help reconstruct failure. Inputs and outputs often contain sensitive data, so logs need redaction, minimal retention, and access control. Recording every prompt verbatim is not automatically better observability.

The serving control plane continually answers three questions: who should execute now, who should be protected when resources are scarce, and how do we know a changed configuration still meets its promise? Answering them makes model computation an operable product capability.
