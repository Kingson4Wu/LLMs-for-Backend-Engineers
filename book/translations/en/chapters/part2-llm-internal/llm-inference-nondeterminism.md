# Why LLM Inference Is Not Fully Deterministic

The same prompt, weights, and `temperature=0` can sometimes produce different output. To understand why, separate three questions: whether decoding samples randomly, whether one forward pass is deterministic, and whether an online service gives one request the same computational conditions each time.

This is usually not a model changing its mind. A throughput-oriented service can place a request in different batches, choose kernels for different shapes, or split a sequence differently. Finite-precision arithmetic can then move very close logits across a decision boundary; autoregressive generation carries that first difference forward.

## Sampling randomness and system nondeterminism

A model produces logits and a decoder selects a token.

- **Sampling** intentionally selects from a probability distribution.
- **Greedy decoding** usually selects the largest logit; many APIs implement `temperature=0` this way.
- **Temperature, top-k, and top-p** change a distribution or candidate set; randomness still depends on whether sampling occurs.

Temperature zero removes intentional sampling randomness. It does not, by itself, guarantee a stable response from a changing serving system.

## How serving conditions affect a token

Floating-point addition is not strictly associative because each step rounds. A parallel reduction can use different accumulation layouts and create tiny numerical differences. With fixed hardware, software, input shape, and execution path, many common forward operators reproduce the same result. An online request, however, is not the whole input: co-batched requests, batch size, chunked prefill, and KV-cache layout can change the numerical path.

```text
load changes → batching or chunking changes → tiny logit difference
             → argmax flips near a tie → later tokens diverge
```

## Batch invariance

A kernel is **batch-invariant** when one sample's numerical result does not depend on the number or position of other samples in its batch. Thinking Machines shows that a forward pass may be deterministic for an identical complete batch while not being batch-invariant. Dynamic batching can therefore look nondeterministic to an individual user.

In that work, RMSNorm, matrix multiplication, and attention are important reduction computations to make batch-invariant. This is a property of a particular implementation and deployment problem, not proof that every kernel or inference server is nondeterministic.

## Reproducibility is a system property

A tiny logit change matters only when candidates are close enough to change the selected token. Strong reproducibility requires recording weights, tokenizer, decoding parameters, quantization, hardware, drivers, runtime, batching behavior, tool environment, and traces. Batch-invariant kernels are one solution: they trade some dynamic performance for more stable numerics across batching conditions.

The reported Qwen3-235B-A22B experiment found 80 distinct greedy completions in 1,000 runs under one default setup and identical completions after enabling its batch-invariant kernels. It demonstrates a viable approach under those conditions; it is not a universal performance or determinism guarantee.

## Takeaway

`temperature=0` removes deliberate sampling randomness. It does not make a changing online service fully deterministic. Treat decoding, numerical behavior, and serving policy as separate, observable parts of the system.

**Reference:** [Defeating Nondeterminism in LLM Inference](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)
