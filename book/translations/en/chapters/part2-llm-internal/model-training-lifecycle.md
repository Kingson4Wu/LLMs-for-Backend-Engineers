# How Models Acquire Their Capabilities Through Training

Whether a large language model can explain code, follow instructions, or reliably call tools does not come from a single black box called “training.” It comes from a causal chain: **what material the model sees, how it computes, what counts as good, how error flows backward, how parameters change, and how the result is checked.**

Cross-entropy measures prediction error, backpropagation assigns that error to parameters, and an optimizer turns gradients into actual updates. This chapter puts these components into one training system: how they turn regularities in material into parameters, and why those parameters create both capabilities and limits.

## Start with the Training Map

Training and inference must be separated. Inference uses existing parameters to generate the next token from the current context. Training repeatedly tests outputs against data and changes parameters. Producing text is not the boundary—training may generate candidate answers too. **The boundary is whether a training objective is used to update parameters.**

```text
raw material, demonstrations, or feedback
              │
              ▼
selection, cleaning, deduplication, mixing, tokenization
              │
              ▼
          training batch
              │
              ▼
Transformer forward pass ──→ vocabulary scores (logits)
              │                       │
              │                       ▼
              │               objective / loss
              │                       │
              │                       ▼
model architecture and parameters ← backpropagation ← gradients ← optimizer
                                                    │
                                                    ▼
                                          new checkpoint
                                                    │
                                                    ▼
                            independent validation and task evaluation
```

These components have different jobs.

| Component | What it determines | What it cannot guarantee alone |
| --- | --- | --- |
| Data | Which language, facts, tasks, and failure patterns recur | That the model learns the right rule |
| Architecture and parameters | How inputs can be represented, combined, and computed | That a desired behavior will emerge |
| Training objective | Which outputs are rewarded or penalized | That the objective equals what people value |
| Backpropagation and optimizer | How error becomes parameter changes | That a change generalizes to new tasks |
| Compute and training process | How much data and how many stable updates are possible | That more parameters mean a better model |
| Validation and evaluation | Which gains and regressions we can observe | That one score represents real-world performance |

Training does not insert documents one by one into a retrievable database. Parameters compress statistical structure that helps future prediction; they do not retain a primary-key index for every source document.

## What Happens in One Parameter Update

Consider: `A case contains 12 bottles of water; 3 cases contain 36 bottles.` In an autoregressive model, earlier tokens are conditions and later tokens are targets. The model does not output “correct” or “wrong”; at each position it assigns a score to every vocabulary token.

```text
input tokens:  A case contains 12 bottles ... 3 cases contain
target tokens:                                         36 bottles .

token IDs → embeddings + positions → Transformer → logits → Softmax probabilities
                                                        │
                                          probability of target too low?
                                                        │
                                                        ▼
                                                  cross-entropy loss
```

The tokenizer turns text into processable IDs. Embeddings and the Transformer turn IDs into contextual representations. The output layer turns representations into vocabulary scores. Cross-entropy measures whether the true next token received enough probability. Architecture determines the forward computation; the objective determines how its result is judged. They are different things.

Backpropagation then calculates each trainable parameter's local contribution to the loss. The optimizer uses those gradients and its own state to make an actual update. The updated parameters enter the next batch, over millions or more iterations.

```text
one batch
  → forward pass: parameters θ make a prediction
  → objective: prediction plus training signal gives loss L
  → backpropagation: obtain ∂L/∂θ
  → optimizer: θ ← θ - one controlled update
  → next batch: test the new θ again
```

One example need not “teach” multiplication. Numeric relations, language structure, program patterns, and factual associations expressed many ways repeatedly apply aligned or conflicting updates to overlapping parameters. Capability forms in the aggregate parameter state after many updates, not in one stored training example.

This also explains the training–inference boundary. During inference, generated tokens return to the context and change the next prediction, while parameters usually remain fixed. Asking a model to think longer generally adds inference steps, search, or tool use; it does not start a temporary training run.

## From Material to Checkpoint: A Continuing Loop

Parameters may begin randomly or from an existing checkpoint. Pretraining, continued pretraining, supervised fine-tuning, and preference optimization often use the latter. A checkpoint is a complete parameter state from a particular moment, not merely another name for the same model.

Raw material does not enter batches unchanged. Source selection, cleaning, deduplication, quality filtering, language and domain mixture, sequence segmentation, and sampling decide which patterns recur. Pretraining text supplies next-token targets itself; assistant behavior is normally organized as request–answer examples or request–candidate–judgment examples.

```text
material and task definition → processing and mixture → batches → updates → checkpoint
           ↑                                                               │
           └──── validation, task evaluation, data review, and monitoring ┘
```

Validation is not decoration outside training. Training loss moves parameters toward the current objective; independent validation and task evaluation reveal overfitting, select checkpoints, and indicate whether data or objectives should change. If test questions, answers, or close variants already appeared in training material, a score cannot separate generalization from repeated exposure.

Thus “the model learned X” contains at least three distinct questions: did training material cover X, did the objective encourage X, and did independent testing check X under unfamiliar conditions? Collapsing them into one loss or leaderboard score usually overstates the conclusion.

### Why Training Artifacts Need Provenance

For backend engineers, a checkpoint can first be compared with a release artifact that needs provenance, but training is not a deterministic compilation process. Changes in data versions or cleaning rules, the starting checkpoint, tokenizer, or training code—and even batch order, randomness, numerical precision, or hardware execution paths—can change the resulting parameters and behavior. A weight file alone is usually not enough to explain why a model improved or regressed on a task.

When comparing or releasing a training result, it should therefore be possible to associate it with its data manifest and processing, starting checkpoint and tokenizer, code and training configuration, optimization and numerical settings, and the independent evaluation suite and results. The aim is not always bit-for-bit reproduction of weights on different hardware. More importantly, a team should be able to explain the conditions that produced a candidate, identify plausible sources of behavioral change, and return to comparable versions and evidence when a regression appears.

## One Skeleton, Three Kinds of Training Signal

Pretraining, supervised fine-tuning, and preference optimization are not three different machines. Each uses the same skeleton—forward computation, objective, gradients, update—but organizes inputs differently and defines “better” differently.

### Pretraining: Forming Broad Predictive Ability

Autoregressive pretraining predicts later tokens from earlier ones. To do this across books, code, questions, documentation, and languages, a model must increasingly use meaning, contextual structure, factual associations, and some problem-solving patterns. Large-scale language modeling can support broad capabilities because better continuation prediction requires reusable information across contexts. The [GPT-3 paper](https://arxiv.org/abs/2005.14165) documents this connection across tasks.

The implication does not run backward. Lower training loss does not mean complete, correct world knowledge or reliable arithmetic every time. It only means the model assigns higher probability to actual subsequent tokens on this training distribution.

A pretrained model may continue an exercise or answer a question, but it first learns what continuation is often plausible, not necessarily how a helpful assistant should respond to a user. That is why post-training matters.

### Supervised Fine-Tuning: Demonstrating the Intended Answer

Supervised fine-tuning (SFT) organizes data as explicit tasks. For “12 bottles per case, how many in 3 cases?”, a demonstration might be “$12 \times 3 = 36$, so there are 36 bottles.” Training still raises the probability of target tokens, usually computing loss mainly over the answer portion.

A demonstration says more than “these words appeared”: it says “respond this way to this request.” It can stabilize output formats, teach the model to explain evidence or ask for missing information, and produce structured tool-call requests. Human demonstrations in [InstructGPT](https://arxiv.org/abs/2203.02155) are this kind of signal.

SFT is not simply answer memorization. Updates affect expression, task tendency, and how existing knowledge is invoked; narrow coverage can also overfit the model to the demonstration distribution. Integer arithmetic examples alone do not establish performance on shortages, unit conversion, or incomplete questions.

### Preferences and Rewards: When There Is More Than One Good Answer

Some tasks cannot provide one standard text for each input. Two answers may both give 36, while only one explains units and avoids irrelevant content. A more natural signal is then “for this question, A is better than B.” Preference is a relative judgment, not automatically factual truth: a fluent wrong answer can be preferred.

One traditional route trains a reward model from comparisons, generates candidates from the language model, and uses reinforcement learning to increase reward. InstructGPT uses the concrete sequence of demonstrations, comparisons, reward model, and PPO. Other rewards come from verifiable outcomes, such as a program passing tests or a numerical result being correct. They still check only properties that the verifier covers.

Direct Preference Optimization (DPO) takes another route. It trains directly on preferred/rejected answer pairs, adjusting their relative tendency against a reference model; it neither requires a separate reward model nor online candidate generation within its training loop. Preference optimization should therefore not all be called online reinforcement learning. The [DPO paper](https://arxiv.org/abs/2305.18290) develops this alternative.

| Signal | Data shape | What it mainly changes | Typical risk |
| --- | --- | --- | --- |
| Pretraining | Large token sequences | Broad representations, associations, and predictive patterns | Data bias, false statements, repeated exposure |
| SFT | Requests and desired answers | Instruction following, format, and task behavior | Narrow coverage and over-adaptation |
| Preference or reward | Answer comparisons, or candidates plus scores | Selection among feasible answers | Reward hacking, evaluator bias, missing checks |

Synthetic data can enter any of these flows, but model-generated does not itself mean reliable. Human review, independent rules, or verifiable results must still decide whether it deserves to become a training signal.

## Read Capability, Scale, and Limits Together

Capability cannot be attributed to data alone. Architecture and parameter count define a range of representations and computations; data distribution determines which associations are encountered; objectives specify encouraged behavior; optimization and compute budget determine how far signals can drive useful updates; evaluation determines whether progress is visible at all.

More parameters do not automatically mean more complete training. Under a fixed compute budget, model size and training-token count must be traded together. Chinchilla found many contemporary models undertrained relative to their data; it is a scaling result under particular settings, not a universal fixed recipe. See the [Chinchilla paper](https://arxiv.org/abs/2203.15556).

Post-training is not merely a cosmetic tone adjustment. It can substantially change whether and how a model invokes existing capabilities for a user request, but it is usually much smaller in scale than pretraining and cannot naturally fill gaps in unseen knowledge, tool environments, or evaluation criteria. Pretraining likewise does not by itself make a system reliable in a real task.

Training ends here; system reliability does not. Once model output enters tools, retrieval, permissions, and evaluation loops, new failure modes appear. Part three explains how those external systems add evidence, action, and control boundaries. Continue with [fine-tuning and distillation](fine-tuning-and-distillation.md) to see how an already capable model can be adapted with less training cost, or how a teacher model can shape another model's behavior.
