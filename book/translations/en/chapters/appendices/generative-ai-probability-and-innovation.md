# Generative AI: Probability, Constraints, and Verification

Large language models generate the next token from current context. This mechanism lets them continue, rewrite, and combine a great many language patterns; it also means that strict, global, or unusual constraints need additional structure. Understanding that is more reliable than inferring a fundamental difference between humans and AI from one test of whether a model can produce an odd sentence.

## What probability generation answers

Given context $x$, a language model represents the conditional distribution of the next token:

$$
P(t_{next}\mid x)
$$

Training makes the model estimate this distribution better under its training objective and data; during generation, a decoding strategy chooses or samples a token from it. Temperature and top-p change the relative opportunity of candidates and the degree of randomness. They do not automatically give the model an external dictionary, formal rules, or a factual verifier.

This produces two common effects. Models often prefer continuations that are common in training and coherent in the current context. Requirements such as “avoid every two-character word in a dictionary,” “output must satisfy a JSON Schema,” or “the conclusion must be supported by experiments” constrain a complete output or the external world. Local, step-by-step selection alone cannot reliably guarantee them.

```text
context → next-token distribution → decoding → candidate output
                                                │
                               rules, tools, or evaluators verify it
                                                │
                                  accept, revise, or regenerate
```

## What an unusual-constraint experiment can show

Consider a task that asks for a passage made only of common Chinese characters, globally incoherent, and with as few common two-character words as possible. Direct generation often produces frequent collocations. Adding explicit forbidden items and examples may lead the model to a noun-list strategy that more easily satisfies the surface constraint.

This demonstrates the difference between **following a constraint** and **verifying it**: a prompt can change the conditional distribution and the model’s preferred strategy, but cannot replace an explicit scorer. It cannot by itself prove that a model cannot “think in reverse,” that people always find the task easier, or that the two have a fixed cognitive gap. Results depend on model version, tokenizer, prompt, decoding parameters, allowed tools, dictionary, and scoring rule.

To turn this into a meaningful evaluation, at least the following must be fixed:

| Element | Why it must be fixed |
| --- | --- |
| Set of common characters and dictionary | “Common” and “meaningful” have no natural boundary |
| Output length and allowed exceptions | Otherwise samples cannot be compared |
| Decoding and retry budget | Repeated sampling and temperature substantially change pass rates |
| Automatic scorer and human review | Local dictionary matches do not establish whether an output is globally meaningful or meaningless |
| Whether tools are allowed | Retrieval and programmatic checking change system capability |

## What prompts, structured output, and verification each do

Prompts express task goals, context, examples, and preferences. Structured output constrains syntax and fields. Validators test computable global constraints. Tools query facts or run experiments. Collapsing them into “is the prompt good enough?” hides the capability a system actually lacks.

```text
objective and background → prompt
output shape             → schema / grammar
testable conditions      → program, dictionary, test, or retrieval
failure handling         → revise, retry, reject, or hand over to a person
```

For example, if every adjacent pair of characters must not appear in a dictionary, a program can check every pair. If content must be true, retrieval and domain evidence matter more than a model’s self-report. If a style must be “strange,” people or calibrated evaluation criteria must still judge it. A model can propose candidates and revisions, but the verification loop determines whether a system can deliver reliably.

## Probability is not a verdict on capability or value

“The model generates probabilistically” describes a mechanism; it does not imply that a model can only copy or cannot innovate. A low-probability sequence may be noise or a valuable new candidate. A high-probability sequence may be reliable or merely clichéd. Novelty, correctness, and value require different evidence.

Likewise, failure on one task can arise from an ambiguous prompt, a decoding choice, insufficient context, no external tools, or an unsuitable scorer. It does not necessarily reveal the full boundary of capability. A good evaluation makes the task, tool budget, verification standard, and success condition explicit so that failures can be located and successes reproduced.

## A model’s explanation of itself also needs verification

A model can fluently explain why it answered a certain way or which reasoning steps it used, but that text is first a generated output, not a diagnostic report that directly reads internal state. It may reflect technical material in training, a role requested by the prompt, post-hoc rationalization, or pattern matching to the current context. Fluent language does not establish that it describes the true causal process.

Rather than asking whether humans can introspect and models cannot, ask whether an explanation can be independently observed, intervened on, or reproduced. Architecture and implementation documents explain how computation is defined; activation measurements, probes, and controlled interventions can study representations; input ablations, tool traces, and version records can help explain an output; benchmarks, real-task evaluation, and error analysis address system reliability. Model explanations remain useful because they can propose reasons to check and suggest a next validation step. In high-impact settings, however, “the model said it checked” cannot count as a completed check.

```text
model explanation → testable claim → external evidence and tools verify it → decide whether to rely on it
```

## Summary

The core of generative AI is conditional probability modeling and decoding. This explains why it can generate candidates efficiently and why strict global constraints need structured output and external verification. An output’s self-explanation is also a claim to verify. Considering probability generation, prompt constraints, and the evidence loop together avoids misreading one interesting failed experiment as a final conclusion about intelligence, creativity, or consciousness.
