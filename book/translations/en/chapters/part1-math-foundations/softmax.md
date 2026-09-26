# Softmax: Turning Scores into Probabilities

When a model faces several candidates, it usually gives each one a real-valued score called a logit. An image classifier may score “cat,” “dog,” and “bird”; a language model scores every possible next token in its vocabulary. Scores can be negative or very large, and they do not add up to one, so they cannot be read as probabilities directly.

Softmax solves a specific problem: it turns competing scores into comparable weights. The weights are nonnegative, sum to one, and preserve the candidates’ ordering. The important idea is not merely the formula, but how Softmax turns **score differences** into **probability ratios**.

## What Do We Actually Need?

Let the final layer produce scores for $K$ candidates:

$$
z=(z_1,z_2,\ldots,z_K)\in\mathbb{R}^{K}
$$

We want to map them to a probability distribution $p$. At minimum, every $p_i$ must be nonnegative, all $p_i$ must sum to one, a larger $z_i$ should not receive a smaller weight, and the transformation must work for every real-valued input and permit backpropagation. This is more than independently rescaling each score: every candidate must compete for the same total probability.

## From Logits to Probabilities

Suppose a model produces three logits:

~~~text
logits = [2.0, 1.0, 0.1]   # “cat”, “dog”, and “bird”
~~~

Softmax has two steps: exponentiate every score, then divide by the sum of all exponentials.

$$
p_i = \operatorname{softmax}(z)_i
    = \frac{e^{z_i}}{\sum_{j=1}^{K}e^{z_j}}
$$

Here, $K$ is the number of candidates, $z_i$ is the $i$th logit, and $p_i$ is its resulting weight.

~~~text
exp(2.0) = 7.39      p_cat  = 7.39 / 11.22 ≈ 0.659
exp(1.0) = 2.72  →   p_dog  = 2.72 / 11.22 ≈ 0.242
exp(0.1) = 1.11      p_bird = 1.11 / 11.22 ≈ 0.099
                           sum = 1
~~~

### Why This Is a Distribution

For finite logits, Softmax’s properties follow directly from algebra:

- $e^{z_i}>0$, and the denominator is a sum of positive values, so every $p_i>0$.
- When there is more than one candidate, the denominator also contains other positive terms, so $p_i<1$.
- Summing all $p_i$ makes the total numerator equal the denominator, so $\sum_i p_i=1$.

The last point expands directly as:

$$
\sum_{i=1}^{K}p_i
=\sum_i\frac{e^{z_i}}{\sum_j e^{z_j}}
=\frac{\sum_i e^{z_i}}{\sum_j e^{z_j}}
=1
$$

Exponentiation is strictly increasing, so the largest logit has the largest exponential and therefore the largest weight. In other words, Softmax first turns arbitrary real scores into strictly positive relative weights, then applies L1 normalization. Normalization fixes the total; exponentiation determines how candidates compete.

### Why Not Normalize the Scores Directly?

Dividing logits by their sum appears simpler:

$$
\tilde p_i=\frac{z_i}{\sum_jz_j}
$$

But logits can be negative and their sum can be zero. For example, `[2,-1]` produces a negative “probability.” Applying ReLU first would turn every negative-score candidate into zero and give it no gradient at that point; squaring instead would give `-10` and `10` the same weight, losing the direction of preference in the score. This does not mean no other normalization exists. It shows that we need a transformation that handles every real score, preserves ordering, and keeps a positive weight for every finite candidate.

## Softmax Preserves Relative Differences

Softmax does not care about an absolute zero point for logits. It cares about differences between candidates. For any two candidates $i$ and $j$:

$$
\frac{p_i}{p_j}=\frac{e^{z_i}}{e^{z_j}}=e^{z_i-z_j}
$$

This has two immediate consequences:

- If $z_i-z_j=1$, then $p_i/p_j=e\approx2.72$; if the difference is 2, the ratio is about 7.39. These are **ratios between the two probabilities**, not a claim that either candidate has an absolute probability of 0.73 or 0.88.
- Adding the same constant $c$ to every logit changes no probability: $\operatorname{softmax}(z+c)=\operatorname{softmax}(z)$. A common upward shift changes no candidate’s advantage over another.

An exponential satisfies the preceding requirements: $e^z$ is always positive, strictly increases with $z$, and turns score differences into ratios. With a difference of 5, the probability ratio is already $e^5\approx148$; this explains why Softmax emphasizes a leading candidate more than the raw scores do.

At a deeper level, a classifier’s output layer is often written as $z_i=w_i^\mathsf{T}h+b_i$. Contributions from the dimensions of hidden representation $h$ add into the score for candidate $i$; when candidates compete, the meaningful quantity is the net advantage $z_i-z_j$. If an additional advantage of $a$ followed by $b$ should correspond to multiplying one probability-ratio factor and then another, the mapping needs $g(a+b)=g(a)g(b)$. Under common conditions such as positivity and continuity, the solutions are the exponential family, $g(d)=e^{cd}$; $c$ merely rescales logits and is the inverse of temperature. Exponentiation is not the only conceivable way to turn scores into weights, but it preserves this consistency between additive differences and multiplicative ratios.

Using the natural base $e$ is mainly a convenient scale convention: any base $a>1$ can be written as $a^z=e^{(\ln a)z}$, which changes temperature or logit scale. Since the derivative of $e^z$ is also $e^z$, later gradient expressions are especially compact. It is not the case that only base $e$ can represent this kind of preference.

### What Role Does $e$ Play Here?

$e\approx2.71828$ is the natural base of continuous growth. For example, it can be written as the limit of continuously compounded growth:

$$
e=\lim_{n\to\infty}\left(1+\frac{1}{n}\right)^n
$$

Understanding Softmax does not require calculating this limit or evaluating exponentials from a series. It matters here because $e^{a+b}=e^ae^b$ turns additive score differences into multiplicative ratios, and because $\frac{d}{dz}e^z=e^z$ lets the cross-entropy derivative simplify cleanly. Programs use stable library functions for these calculations.

A logit is therefore an unnormalized score of relative preference. Softmax turns those preferences into a distribution with a fixed total. It does not add information the model lacks or guarantee that its probabilities are calibrated frequencies in the real world.

## Temperature: How Concentrated Is the Distribution?

Generation often introduces a positive temperature $T$ before Softmax:

$$
p_i(T)=\frac{\exp(z_i/T)}{\sum_j\exp(z_j/T)}
$$

Temperature does not introduce another kind of randomness. It rescales logit differences:

- $0<T<1$: differences become larger, the distribution becomes sharper, and the highest-score candidate dominates more.
- $T>1$: differences become smaller, the distribution becomes flatter, and lower-score candidates gain more weight.
- $T\to0^+$: if there is one unique largest logit, the distribution approaches a one-hot distribution on that candidate.

Many APIs interpret a temperature of zero as greedy decoding, but $T=0$ cannot be substituted directly into this equation; it is special API behavior. Temperature only changes how the model selects among existing scores. It cannot add evidence or guarantee a correct answer.

## Numerical Stability: Why Subtract the Maximum?

For logits such as `[1000, 999, 998]`, directly calculating $e^{1000}$ overflows in common floating-point formats. Translation invariance lets us instead compute:

$$
\operatorname{softmax}(z)_i=
\frac{e^{z_i-m}}{\sum_j e^{z_j-m}},
\qquad m=\max_j z_j
$$

The largest exponent input is then zero, so $e^0=1$; every other input is at most zero and cannot overflow positively. For the example, compute `[0,-1,-2]`. Very small terms can still underflow to zero, usually meaning they are negligible at the chosen precision. Inputs that already contain `NaN` or `Inf` still need explicit handling.

Frameworks generally provide stable `softmax` or `log_softmax` operations. Training code should not exponentiate large values itself and then normalize them.

## How Softmax Connects to Cross-Entropy Training

In classifier or language-model training, write the true label as the one-hot vector $y$: when the correct class is $c$, $y_c=1$ and all other $y_i=0$. The full cross-entropy form is:

$$
L=-\sum_i y_i\log p_i
$$

Because only $y_c$ is 1, this is the loss that penalizes the probability assigned to the correct class:

$$
L=-\log p_c
=-\log\frac{e^{z_c}}{\sum_j e^{z_j}}
=-z_c+\log\sum_j e^{z_j}
$$

The first term encourages the correct logit to increase; the second makes every candidate compete. The expression also shows why the gradient is simple. For any $z_i$, the derivative of the first term is $-y_i$; the second is LogSumExp, whose derivative is exactly Softmax:

$$
\frac{\partial}{\partial z_i}\log\sum_j e^{z_j}
=\frac{e^{z_i}}{\sum_j e^{z_j}}
=p_i
$$

Adding the two terms gives:

$$
\frac{\partial L}{\partial z_i}=p_i-y_i
$$

The more probability the model assigns to a wrong candidate, the more it needs to lower that candidate; the less it assigns to the correct one, the more it needs to raise it. Many frameworks fuse these operations so logits go directly into cross-entropy, avoiding numerical problems from first computing probabilities and then taking logarithms. [Cross-Entropy Loss](cross-entropy.md) develops the statistical meaning of this objective.

Numerically, a correct-class probability of 0.9 gives a loss of about 0.105; 0.1 gives about 2.303; and 0.01 gives about 4.605. The negative logarithm makes a model pay much more for confidently assigning probability to the wrong candidate than merely checking whether the highest-score candidate was correct.

## An Optional Statistical View: Maximum Entropy

There is another way to understand the exponential form. Suppose only that candidate probabilities must normalize, and that their expected value under a score is constrained:

$$
\sum_i p_i=1,\qquad \sum_i p_i z_i=\mu
$$

Maximizing entropy $H(p)=-\sum_i p_i\log p_i$ subject to these constraints with Lagrange multipliers gives:

$$
p_i\propto e^{\beta z_i}
$$

After normalization this is Softmax with temperature, where $\beta=1/T$. The derivation shows why an exponential family naturally appears when a model fixes an expectation and otherwise adds as little preference as possible. It does not prove Softmax is the only correct normalization for every task, and Transformer training does not require this derivation. Treat it as an additional perspective.

## In Attention: Turn Match Scores into Read Weights

A standard Transformer uses scaled dot-product Attention:

$$
\operatorname{Attention}(Q,K,V)=
\operatorname{softmax}\left(\frac{QK^\mathsf{T}}{\sqrt{d_k}}\right)V
$$

For a Query, $QK^\mathsf{T}$ gives each Key a match score. Softmax normalizes scores over readable positions into nonnegative weights that sum to one, and those weights combine the Values. A causal language model first masks future-position scores to a very small value, making their weights numerically zero.

These weights say where a head reads information from in this layer and context. They are not fixed semantic similarities between tokens, and they should not be treated directly as evidence of the model’s causal reason. Standard Transformers use Softmax because it supplies competitive, differentiable normalized weights; it is not the only possible normalization for every attention variant. The [original Transformer paper](https://arxiv.org/abs/1706.03762) defines scaled dot-product Attention.

## In Generation: A Distribution Still Needs a Token Choice

At every step, a language model produces vocabulary-wide logits. Softmax turns them into a next-token distribution. Greedy decoding chooses the highest-score token, while random sampling draws according to the weights; Top-K and Top-P first discard some candidates and then renormalize.

~~~text
current context → model → vocabulary logits → temperature / filtering → Softmax → choose one token
                                                                            ↓
                                                                append it and continue
~~~

Softmax describes the model’s output preference under its current conditions. A high-probability token can still cause a factual error, reasoning error, or an answer that misses the user’s intent. Those problems require separate work on evidence, training, tools, and system constraints.

## Section Summary

Softmax turns competing logits into weights that sum to one. It preserves ordering and, more precisely, the probability ratios determined by logit differences. Temperature rescales those differences, while subtracting the maximum enables stable computation. In training, Softmax and cross-entropy turn the gap between a prediction and its label into gradients; in inference, Softmax produces both Attention read weights and a distribution from which the next token is selected.

## Further Reading

- [Activation Functions](./activation-functions.md) — Softmax and hidden-layer activations have different roles.
- [Dot Products and Cosine Similarity: How Vectors Express Relationships](dot-product-angle.md) — Distinguish scores, directions, and lengths.
- [Cross-Entropy Loss](cross-entropy.md) — How probabilities become training signals.
- [Transformer Architecture Through Data Flow](../part2-llm-internal/transformer-architecture.md) — The full data flow through Query, Key, and Value.
- [LLM Generation: From Input to the Next Token](../part2-llm-internal/llm-generation.md) — How temperature, filtering, and sampling affect generation.
