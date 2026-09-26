# Cross-Entropy: Measuring Prediction Error

## The Problem This Section Addresses

A model assigns probabilities to candidate outputs, and training needs to measure whether it assigns enough probability to the correct answer. Cross-entropy turns this into an optimizable scalar: the lower the probability of the correct answer, the larger the loss.

It is not an arbitrary penalty. Minimizing cross-entropy is equivalent to maximizing the conditional likelihood of training data under the model, which makes it natural for probabilistic modeling tasks such as classification and next-token prediction. It is common, but the appropriate objective still depends on task and training design.

## How the Mechanism Works

### The Intuition Behind -log(p)

Suppose a model assigns probability 0.8 to “this image is a cat,” and the correct answer is indeed cat. How good is that prediction?

A loss should satisfy: **the higher the probability assigned to the correct answer, the lower the loss**. The negative logarithm has this property:

| Probability p of the correct class | -log(p) | Interpretation |
|-----------------------------------|---------|----------------|
| 0.99 | 0.01 | Almost perfect |
| 0.8 | 0.22 | Fairly good |
| 0.5 | 0.69 | A coin-flip level of confidence |
| 0.1 | 2.30 | Strongly incorrect |

Key properties of -log(p):
- At p = 1, loss is zero: a completely correct prediction incurs no penalty.
- As p → 0, loss → infinity: assigning almost no probability to the answer is severely penalized.
- Growth is nonlinear: moving from p=0.9 to p=0.1 increases loss more than twentyfold.

### Maximum Likelihood: Why -log(p) Makes Sense

You flip a coin five times and obtain heads, heads, heads, heads, tails. What is your estimate of the probability of heads?

Intuitively, 4/5 = 0.8. Maximum likelihood estimation formalizes that intuition.

**Likelihood** is the probability of the observed data under a particular parameter assumption.

```
If the probability of heads is θ, the likelihood of the observed sequence is:
L(θ) = θ⁴ × (1-θ)
```

**MLE seeks the value of θ that maximizes L(θ).**

Differentiate L(θ) = θ^4(1-θ), set the derivative to zero, and obtain θ = 0.8.

This agrees with the intuitive estimate.

### From Coins to Neural Networks

For a neural-network classifier:

- **The coin’s θ** corresponds to the model parameters θ.
- **Coin-flip outcomes** correspond to the true training labels.
- **The likelihood function** measures how likely those labels are under the model parameters.

MLE asks us to **choose parameters that maximize the joint probability of the observed labels under the current model**.

Neural networks commonly optimize by minimizing with gradient descent, so we take the negative logarithm of the likelihood:

L_i = −log P_θ(y_i | x_i)
**This is the core of cross-entropy: for each example, loss equals the negative log of the probability assigned to its correct answer.**

### The Full Process for Three Classes

```
1. Model logits:       [2.0, 1.0, 0.1]
2. Softmax:            [0.66, 0.24, 0.10]  ← Model favors class 1
3. True label:         [0, 1, 0]           ← Class 2 is actually correct
4. Cross-entropy loss: -log(0.24) ≈ 1.43   ← Incorrect prediction, relatively high loss
```

**With a one-hot label, only the correct class has value 1. Every other term vanishes from L = -Σ y_i log(p_i), leaving only the correct-class term.**

## Formalization

### Entropy, Cross-Entropy, and One-Hot Targets

Entropy measures uncertainty in a distribution \(P\):

$$
H(P)=-\sum_xP(x)\log P(x).
$$

Cross-entropy asks what it costs to encode events that actually follow \(P\) with a model distribution \(Q\):

$$
H(P,Q)=-\sum_xP(x)\log Q(x).
$$

The “cross” is literal: weights come from the true distribution \(P\), while the logarithm comes from the model distribution \(Q\). With a one-hot class label, every term but the true class vanishes, which is why per-example multiclass loss becomes \(-\log p_{\text{true}}\).

### Binary and Multiclass Forms

For binary classification, where \(p=P(y=1\mid x)\) and \(y\in\{0,1\}\), binary cross-entropy is

$$
L=-[y\log p+(1-y)\log(1-p)].
$$

When \(y=1\), this is \(-\log p\); when \(y=0\), it is \(-\log(1-p)\). For a multiclass model, logits are normalized with Softmax and the one-hot target selects the correct class. For example, logits \([2.0,1.0,0.1]\) give approximately \([0.659,0.242,0.099]\); if the second class is correct, loss is \(-\log(0.242)\approx1.418\).

### Why Take a Logarithm?

For independent observations, likelihood multiplies probabilities. With four heads and one tail, \(L(\theta)=\theta^4(1-\theta)\). The logarithm turns products into sums, avoids numerical underflow, and simplifies differentiation, while preserving the maximizer because it is strictly increasing. For supervised data,

$$
\hat\theta=\arg\max_\theta\sum_i\log P_\theta(y_i\mid x_i).
$$

Negating this expression produces negative log-likelihood, the form optimized by gradient descent. With one-hot targets, it is cross-entropy.

### Equivalent Views and the Softmax Gradient

```text
maximum likelihood → log likelihood → negative log-likelihood → cross-entropy
```

These names emphasize statistical estimation, an engineering loss, and information-theoretic coding cost. The same relationship can be written as

$$
H(P,Q)=H(P)+\operatorname{KL}(P\Vert Q).
$$

With fixed \(P\), minimizing cross-entropy minimizes the KL divergence between model and target distributions. For Softmax logits \(z_i\) and one-hot targets \(y_i\), the combined derivative is \(\partial L/\partial z_i=p_i-y_i\). This is computationally convenient, but it does not by itself guarantee stable training; implementations should compute from logits and still depend on sound numerical and optimization design.

Cross-entropy loss:

L = −Σ(i=1, K) y_i · log(p_i)

Here y_i is the one-hot target and p_i is the Softmax probability.

For one-hot labels:

L = −log(p_true)
Minimizing cross-entropy is equivalent to maximizing log-likelihood, and therefore to maximum likelihood estimation.

## Section Summary

Cross-entropy reconciles predictions with targets by measuring how little probability the model assigns to the correct answer. Statistically, minimizing it maximizes the likelihood of the training data. It follows naturally from a statistical principle rather than an arbitrary penalty design.

## Further Reading

- [Softmax](./softmax.md) — Softmax turns logits into probabilities; cross-entropy evaluates those probabilities.
- [Backpropagation](./backpropagation.md) — Softmax plus cross-entropy has the elegant logit gradient p_i - y_i, making gradient computation particularly simple.
