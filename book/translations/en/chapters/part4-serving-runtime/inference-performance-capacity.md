# Inference Performance and Capacity: How Latency, Throughput, and KV Cache Constrain One Another

Serving problems often arrive as a short complaint: “the first token is slow,” “a conversation slows down,” “GPU memory is always full,” or “tokens per second are high but users are queued.” A single QPS number or GPU-utilization graph cannot explain these symptoms. They arise from the same constraints: when requests arrive, how long their inputs and outputs are, how much memory their state consumes, and how the scheduler makes them share a model.

This chapter concerns online inference after a model has been loaded. The Transformer architecture defines what computation the model performs; an inference engine arranges that computation within finite resources.

## Separate the meanings of “fast”

A streaming request has at least four time components:

```text
arrival ── queue ── prefill ── first token ── decode ── final token
              │                    │              │
        waiting for resources     TTFT         output pace
```

- **Queueing latency** is time spent waiting for an instance, memory, or a scheduling opportunity.
- **Time to first token (TTFT)** is time from arrival to the first visible generated token; it includes queueing, input processing, and prefill.
- **Time per output token (TPOT)** is the interval between generated tokens and approximates sustained output speed.
- **End-to-end latency** is total completion time and is strongly affected by output length.

Lower average response time therefore does not necessarily improve an interactive experience. A larger batch can increase total throughput while increasing TTFT. Offline summarization and batch extraction often optimize throughput and unit cost; chat, code completion, and voice interaction usually constrain TTFT and TPOT first. State the service objective before choosing an optimization.

## Why capacity is not QPS

Ten short questions per second and ten requests carrying long documents and generating thousands of tokens are different workloads. Capacity depends at least on the following dimensions:

| Workload dimension | What it changes |
| --- | --- |
| Arrival rate and bursts | Whether a queue grows and how much headroom is required |
| Input-token length | Prefill work, first-token time, and initial KV state |
| Output-token length | Decode time, connection lifetime, and state lifetime |
| Context length | KV-cache use per active sequence and achievable concurrency |
| Shared prefixes and session continuity | Whether computed state can be reused and where traffic should go |
| Cancellation, timeout, and streaming consumption | Whether useless generation stops and returns resources promptly |

Memory must first hold model weights and runtime workspace. The remainder holds KV cache for active requests. Each sequence grows as processed context and generated output grow, so feasible concurrency changes with the length distribution; it is not a fixed number. Input, output, concurrency, and queue limits turn that uncertainty into an explicit service contract.

## KV Cache: a speed optimization and a capacity constraint

To generate the next token, attention still reads keys and values from prior tokens. KV cache preserves those intermediate states, so each step does not recompute the whole prefix; the new token’s query must still be computed. It is neither an application’s conversation-history store nor a cure for overly long context.

```text
one request: K/V for processed tokens ── retained ──→ reused by next attention step
many requests: K/V for an identical prefix ── hit ──→ skip repeated prefill for that prefix
```

The latter is **prefix caching**. Requests with an actually identical system instruction, long document, or tool definition can reuse the associated KV state and avoid repeated prefill. Similar-looking text, a different order, or an unaligned partial match may not hit. Cache space is finite, so a system chooses what to retain, evict, or recompute. Sharing across tenants also requires isolation because timing behavior can reveal whether cached content exists; hit rate is not the only goal.

Moving KV state to host memory, disk, or another machine can temporarily free scarce accelerator memory, but introduces transfer and recovery delay. It helps only when that cost is lower than recomputation or remains within the service objective. The useful question is not which paging algorithm an engine uses: where is state, when is it needed next, and is moving it cheaper than recomputing it?

## How batching improves and harms experience

Model weights are large. Executing multiple requests together can amortize weight reads and device-launch overhead, increasing tokens per second. But requests have different lengths, and fixed batches can be held by the longest sequence. Online engines commonly add and remove sequences between generation steps so a completed short request frees its slot immediately.

The trade-off remains. Aggressive batching makes short interactive requests wait; aggressive TTFT optimization can leave devices underfilled. Scheduling should follow the service objective: queue interactive, batch, and high-priority traffic separately; cap input and output per request; stop decode promptly after cancellation; and observe queue depth and tail latency.

## Why Long Prefill Can Freeze Requests That Are Already Answering

Continuous batching prevents empty slots after short requests finish, but introduces a finer trade-off. A newly arrived long-document request needs substantial prefill. If a scheduler processes that input in one uninterrupted pass, conversations already in decode must wait for it to finish, and users see output pause abruptly.

```text
un-chunked:       decode ───────── wait for long prefill ───────── decode
chunked/interleaved: decode ─ prefill chunk ─ decode ─ prefill chunk ─ decode
```

**Chunked prefill** divides a long input into segments and interleaves them with decode steps of existing requests. It does not reduce total work for the input and may add modest launch and weight-read overhead. It changes the shape of waiting: existing sessions avoid one very long output gap, while the new request gradually leaves the queue.

Smaller chunks are not always better. Larger chunks finish the new input sooner but can damage other requests’ TPOT; smaller chunks smooth streaming output but add scheduling and execution overhead. A sensible limit comes from a service objective: first define the longest acceptable output gap for existing streams, then use the remaining time for the largest useful prefill chunk. The point is not a fixed token count, but a scheduling time slice that serves interaction.

| Symptom | Causal chain to inspect first |
| --- | --- |
| First token becomes slow | Burst queueing, long-input prefill, prefix-cache hits |
| First token is normal but later output slows | Decode memory bandwidth, active sequences, batching policy |
| Out of memory or sudden loss of concurrency | Weights and workspace, KV cache, context and output limits |
| Total throughput rises but interaction worsens | Batch waiting, queue isolation, and whether TTFT was sacrificed |
| Scaling has little effect | Model load and warm-up time; traffic still concentrated on old instances |

These are starting points, not recipes. Validate them with metrics segmented by request length, model version, priority, and time period; averages often hide bursts and tail behavior.

## Pausing Is Not Free When Memory Is Tight

KV cache grows with a request while device memory is finite. An engine can reserve maximum-length space for each request, but wastes capacity when many requests end early. It can instead allocate fixed KV blocks as a sequence grows. This separates a sequence’s logical order from its physical locations and reduces fragmentation from reserving one large contiguous range. It is an inference-state allocation strategy, not another attention algorithm.

When memory runs out, a scheduler can also **preempt** a request: pause it, free its private KV state, and resume later. There are three recovery paths, with different costs:

| Recovery path | What it saves | Cost paid |
| --- | --- | --- |
| State remains in local device memory | Almost no recovery work | Keeps scarce capacity occupied |
| Restore state from slower storage | Frees some device memory | Transfer delay and bandwidth contention |
| Re-prefill from input and generated output | Retains no KV state | Recomputation, worse TTFT, or a later output pause |

Preemption does not make concurrency free. It converts memory pressure into recovery cost and can worsen the preempted request’s tail latency. Use it according to priority, expected waiting time, state size, cancellability, and whether the resumed request can still meet its deadline. Frequent preemption of interactive streams is often worse than rejection or queueing.

## When to separate Prefill from Decode

Long inputs chiefly pressure prefill. Long outputs and high concurrency keep decode and KV state busy. Some high-load systems give the two phases separate resource pools: after prefill, the system transfers KV state to a decode pool for generation.

```text
long-context request → prefill pool ── transfer KV state ──→ decode pool → streamed output
```

This **prefill/decode disaggregation** lets the two resource types scale with different workloads and prevents long prefills from disrupting existing streams. It also adds state transfer, routing logic, and failure boundaries. With short inputs, low traffic, or a single machine that already meets objectives, it usually adds complexity without benefit. It is an architecture for a measured bottleneck, not a required inference shape.

## Speculative Decoding: Parallel Proposals to Reduce Serial Steps

Decode is limited because the target model determines one next token at a time. **Speculative decoding** has a faster draft model or draft mechanism propose several consecutive tokens, then asks the target model to validate that segment in one pass. A consecutive accepted prefix is kept; at the first disagreement, the target model takes over.

```text
draft:            a ─ b ─ c ─ d
target validation: a ─ b ─ c ─ ×
output:           accept a, b, c; target model determines later tokens
```

It trades one larger validation calculation for several output tokens and can reduce serial rounds of user waiting. With correct validation and sampling rules, the final distribution remains governed by the target model; the draft only guesses a prefix the target may accept. Benefit requires a sufficiently fast draft, a sufficiently high acceptance rate, and validation that does not crowd out scarce memory and batch capacity. If drafts are often wrong, the target is already fast, or the system is saturated, the extra draft work may not help.

## Decide from workload, not peak specifications

Capacity planning needs a target model, real or conservative input/output-length distributions, burst arrival behavior, TTFT/TPOT/completion targets, acceptable degradation, and failure headroom. Benchmark under those conditions before choosing model size, instance count, cache budget, queue policy, or scaling threshold. Raw token throughput is not service capacity: useful work is work completed within quality, deadline, and cost constraints. Raising tokens per second while letting interactive requests time out does not create effective capacity.

Every performance issue reduces to one question: which requests occupy finite compute, bandwidth, and state space? Separating time into queueing, prefill, and decode; memory into weights, workspace, and KV state; and traffic into length and priority makes performance decisions explainable.
