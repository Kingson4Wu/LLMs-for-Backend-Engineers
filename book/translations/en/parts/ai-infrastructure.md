# Part IV: LLM Infrastructure

LLM infrastructure is not merely a set of GPUs. It is the runtime system that loads, calls, scales, observes, and reliably delivers a model. This part first follows one request to establish the map from model computation to hardware and clusters, then examines common performance-and-capacity problems and the control plane that turns a model into an operable service.

On [the book’s main map](../index.md#the-books-main-map), this part carries earlier model calls and external systems into a runtime constrained jointly by capacity, latency, cost, and reliability.

| Reading order | Question answered |
| --- | --- |
| [LLM Infrastructure: How a Model Becomes a Reliable Service](../chapters/part4-serving-runtime/llm-infrastructure.md) | What layers does one call cross, and what jointly sets latency, cost, and reliability? |
| [Inference Performance and Capacity: How Latency, Throughput, and KV Cache Constrain One Another](../chapters/part4-serving-runtime/inference-performance-capacity.md) | Why is a service slow, queued, or out of memory, and how should capacity be judged? |
| [Serving Control Plane: Routing, Scaling, and Reliable Delivery](../chapters/part4-serving-runtime/serving-control-plane.md) | How does traffic find a suitable instance, and how does a service scale, roll out, roll back, and recover? |
