# Softmax: How Scores Become Probabilities

Softmax appears in classification outputs and attention weights. It receives unnormalized scores, or logits, and produces relative weights whose sum is 1. Raising one score also changes the weights of every other candidate. This chapter explains why this mapping satisfies probability constraints, why it uses exponentials, and how it connects to cross-entropy.

---

## From Logits to Probabilities: The Problem Setup

### What Are Logits?

The last layer of a neural network usually outputs a group of real numbers:

$$z = (z_1, z_2, \dots, z_K) \in \mathbb{R}^K$$

These $z_i$ values are called **logits**, or unnormalized scores.

### What Must This Mapping Satisfy?

We need a function that maps any real-valued vector to the probability simplex:

$$f: \mathbb{R}^K \to \Delta^{K-1}$$

The probability simplex is:

$$\Delta^{K-1} = \{p \mid p_i > 0, \sum_i p_i = 1\}$$

### Necessary Constraints

- **Nonnegativity**: every output must be > 0.
- **Normalization**: their sum must be 1.
- **Defined everywhere**: it must be defined for every real input.
- **Order preservation**: $z_i > z_j \Rightarrow p_i > p_j$.

  **Example**: if logits are $[2.0, 1.5, 0.8]$, Softmax preserves the order $p_1 > p_2 > p_3$.
- **Differentiability**: it must be smooth and differentiable, with stable gradients for backpropagation.

---

## Definition of Softmax

### Standard Form

$$\text{Softmax}(z_i) = \frac{e^{z_i}}{\sum_{j=1}^K e^{z_j}}, \quad i = 1, \dots, K$$

Where:
- $K$: the number of classes.
- $z_i$: the logit for class $i$.
- The denominator: the sum of exponentials over all classes, used for normalization.

### Vector Form

$$\text{Softmax}(z) = \frac{\exp(z)}{\mathbf{1}^\top \exp(z)}$$

### Numerically Stable Form

$$\text{Softmax}(z_i) = \frac{e^{z_i - \max(z)}}{\sum_{j=1}^K e^{z_j - \max(z)}}$$

**Why subtract $\max(z)$?**

When a $z_i$ is very large, for example 1000, $e^{1000}$ overflows to Inf. After subtracting $\max(z)$:
- The largest logit becomes 0, so $e^0 = 1$.
- Other logits are negative; $e^{\text{negative}}$ can underflow to 0 but cannot become NaN.
- The mathematical result is identical, because numerator and denominator are both divided by $e^{\max(z)}$.

**Example**:
- Original: $z = [1000, 999, 998]$ → $e^{1000}$ overflows.
- Stable form: $z - 1000 = [0, -1, -2]$ → $e^0=1, e^{-1}≈0.37, e^{-2}≈0.14$ ✓

---

## Why Every Output Is Between Zero and One and Their Sum Is One

This is a purely algebraic result and needs no probability intuition.

Let $p_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$.

### Why Is Every Probability Positive?

- For every real $z_i$, $e^{z_i} > 0$.
- The denominator is a sum of positive numbers, so it is > 0.
- Therefore $p_i > 0$.

### Why Is Every Probability Less Than One?

The denominator includes the numerator itself:

$$\sum_j e^{z_j} \ge e^{z_i} \Rightarrow p_i = \frac{e^{z_i}}{\sum_j e^{z_j}} \le 1$$

(It is strictly < 1 unless $K=1$.)

### Why Do All Probabilities Sum to One?

$$\sum_{i=1}^K p_i = \sum_i \frac{e^{z_i}}{\sum_j e^{z_j}} = \frac{\sum_i e^{z_i}}{\sum_j e^{z_j}} = 1$$

### The Algebraic Meaning

**Softmax = L1 normalization of a group of positive numbers.**

The role of the exponential is to turn arbitrary real values into strictly positive weights.

---

## Why Use Exponentials?

### Why Direct Normalization Fails

$$p_i = \frac{z_i}{\sum_j z_j}$$

**Problems**:
- $z_i$ can be negative, yielding a negative “probability.”
- The denominator can be 0.
- Meaning is destroyed when signs change.

**Conclusion**: it does not satisfy the basic constraints.

### Why Normalizing After ReLU Fails

$$p_i = \frac{\max(0, z_i)}{\sum_j \max(0, z_j)}$$

**Problems**:
- It is not differentiable at 0, making training harder.
- Many classes can become 0 and retain zero gradients for a long time.
- Relative differences are distorted.

### Why Squared Normalization Fails

$$p_i = \frac{z_i^2}{\sum_j z_j^2}$$

**Problems**:
- $(-10)$ and $(+10)$ receive the same weight.
- The direction of logit preference is lost.
- Classification semantics collapse.

---

## What Properties Do Exponentials Provide?

The exponential function $e^x$ satisfies all of these requirements:

1. **Strict positivity**: $e^x > 0$, with no zeros, negative values, or discontinuities.
2. **Strict monotonicity**: it preserves order.
3. **Difference amplification**: a linear difference becomes a multiplicative difference.
   $$\frac{e^{z_i}}{e^{z_j}} = e^{z_i - z_j}$$

   **Example**:
   - If $z_1 - z_2 = 2$, then $p_1/p_2 = e^2 ≈ 7.4$.
   - If $z_1 - z_2 = 5$, then $p_1/p_2 = e^5 ≈ 148$.
   - A larger logit gap produces a more disparate probability ratio.

4. **An additive-to-multiplicative homomorphism**:
   $$e^{a+b} = e^a \cdot e^b$$

The fourth property turns additive scores into multiplicative relative weights. It is also central to Softmax's connection to probability modeling.

---

## Where Does the Natural Constant e Come From?

### The Limit of Continuous Compounding

**Background**: suppose that you deposit 1 unit of money at a 100% annual interest rate.
- Compounded once a year: $(1 + 1)^1 = 2$.
- Compounded twice a year: $(1 + 0.5)^2 = 2.25$.
- Compounded daily: $(1 + \frac{1}{365})^{365} ≈ 2.7146$.
- Compounded every second: $(1 + \frac{1}{31536000})^{31536000} ≈ 2.71828$.

As compounding frequency approaches infinity, or **continuous compounding**, the limit is $e$:

$$e = \lim_{n \to \infty} \left(1 + \frac{1}{n}\right)^n \approx 2.718281828...$$

### Series Definition

$$e = \sum_{k=0}^{\infty} \frac{1}{k!} = 1 + 1 + \frac{1}{2} + \frac{1}{6} + \frac{1}{24} + \cdots$$

Computing through $1/9!$ already gets very close to 2.71828.

### Key Property: It Is Its Own Derivative

$$\frac{d}{dx} e^x = e^x$$

This is the fundamental reason that Softmax plus cross-entropy has a simple gradient.

---

## Why Use the Natural Constant e Rather Than Another Base?

### Can Another Base Work?

Suppose we use a base $a > 0$:

$$p_i = \frac{a^{z_i}}{\sum_j a^{z_j}}$$

Its derivative is:

$$\frac{d}{dz} a^z = a^z \ln a$$

### Why Does the Gradient Scale Change?

With cross-entropy, the gradient becomes:

$$\frac{\partial L}{\partial z_i} = \ln(a) \cdot (p_i - y_i)$$

With $e$:

$$\ln(e) = 1 \Rightarrow \frac{\partial L}{\partial z_i} = p_i - y_i$$

### Why Does This Matter?

- The learning rate should directly control step size.
- Changing the base introduces a meaningless constant $\ln a$.
- In deep networks, scale is difficult to control.
- It adds no expressive power and is only interference.

**Conclusion**: using $e$ removes this extra constant scale and keeps the system simplest.

---

## Why Softmax and Cross-Entropy Work Well Together

### What Is Cross-Entropy?

In classification, the true label is represented with **one-hot encoding**:
- If an example belongs to class 2 among three classes, $y = [0, 1, 0]$.
- Only the correct class is 1; all others are 0.

**Cross-entropy loss** measures the difference between predicted distribution $p$ and true distribution $y$:

$$L = -\sum_i y_i \log p_i$$

Because $y$ is one-hot and only $y_{true}$ is 1, it becomes:

$$L = -\log p_{true}$$

Meaning:
- If $p_{true} = 1$, the prediction is completely correct and $L = 0$.
- If $p_{true} = 0.1$, the prediction is uncertain and $L = 2.3$.
- If $p_{true} = 0.01$, the prediction is wrong and $L = 4.6$.

**Objective**: minimizing cross-entropy maximizes the predicted probability of the correct class.

### The Full Form of Cross-Entropy Loss

With one-hot labels $y$, cross-entropy, also called negative log-likelihood, is:

$$L = -\sum_i y_i \log p_i$$

### Substitute Softmax

$$L = -z_y + \log \sum_j e^{z_j}$$

### The Simple Gradient Form

$$\frac{\partial L}{\partial z_i} = p_i - y_i$$

This remarkably clean form comes from:

$$\frac{d}{dx} e^x = e^x$$

If another positive function $g(x)$ replaces the exponential, its gradient generally contains a $g^{\prime}(x)/g(x)$ term and does not retain the simple cross-entropy form $p_i-y_i$. This does not mean another normalization can never be optimized.

---

## From Additive Scores to Probability Ratios

This is an important structural clue for Softmax, not a claim that it is the sole choice in every task.

### The Additive Structure of Logits

The typical final-layer form is:

$$z_i = w_i^\top x + b_i$$

Its meaning is “evidence accumulation”:
- Supporting features increase $z_i$.
- Contrary evidence decreases $z_i$.
- Multiple pieces of evidence add their scores.

**Example** (image classification):
- Detecting “fur” → cat score +2.
- Detecting “pointed ears” → cat score +1.5.
- Detecting “round face” → cat score +1.
- Final: $z_{\text{cat}} = 2 + 1.5 + 1 = 4.5$.

When comparing two classes, the natural quantity is their **difference**:

$$z_i - z_j$$

It is the net advantage of $i$ over $j$, an additive structure.

### The Multiplicative Structure of Probabilities

In classification, the quantity of interest is relative likelihood, or a **ratio**:

$$\frac{p_i}{p_j}$$

**Example**:
- If $p_{\text{cat}} = 0.7, p_{\text{dog}} = 0.2$.
- The ratio $p_{\text{cat}}/p_{\text{dog}} = 3.5$ says that cat is 3.5 times as likely as dog.
- This is an odds ratio, fundamentally a multiplicative structure.

### How Can a Difference Control a Ratio?

We want a monotonic function $g$ such that:

$$\frac{p_i}{p_j} = g(z_i - z_j)$$

**Left side**: proportional probability structure, the multiplicative world.
**Right side**: logit-difference structure, the additive world.

**We need a bridge that turns a difference into a ratio.**

### Why Does the Consistency Constraint Lead to Exponentials?

We want transitivity:
- If $i$ is stronger than $j$ by $\Delta_1$, and $j$ is stronger than $k$ by $\Delta_2$.
- Then $i$ should be stronger than $k$ by $\Delta_1 + \Delta_2$.

That is:

$$(z_i - z_j) + (z_j - z_k) = z_i - z_k$$

The corresponding probability ratios multiply:

$$\frac{p_i}{p_k} = \frac{p_i}{p_j} \cdot \frac{p_j}{p_k}$$

Combining them gives the functional equation:

$$g(\Delta_1 + \Delta_2) = g(\Delta_1) \cdot g(\Delta_2)$$

When $g$ is positive, continuous, and satisfies this multiplicative consistency, its solution is exponential:

$$g(\Delta) = e^{c\Delta}$$

Therefore:

$$\frac{p_i}{p_j} = e^{c(z_i - z_j)} \Rightarrow p_i \propto e^{cz_i}$$

After normalization:

$$p_i = \frac{e^{cz_i}}{\sum_j e^{cz_j}}$$

($c$ is a temperature parameter, commonly $c = 1/T$.)

**Conclusion**: under these consistency conditions, exponentials turn additive logit differences into multiplicative probability ratios. This makes them well suited to log-odds models, without excluding other normalizations for other tasks.

### Effect on Training

Training uses log-likelihood, and logarithms turn multiplication back into addition:
- **Exponential**: addition → multiplication.
- **Logarithm**: multiplication → addition.

The system is closed: logit differences are linear, log probability ratios are linear, and gradients are simple and stable.

---

## Information-Theoretic View: A Maximum-Entropy Derivation

### Problem Setup

Under the constraints:

$$\sum_i p_i = 1, \quad \sum_i p_i z_i = c$$

maximize entropy:

$$H = -\sum_i p_i \log p_i$$

### Lagrange Method

Solving with Lagrange multipliers gives:

$$p_i \propto e^{z_i}$$

After normalization, this is Softmax.

### What Does This Derivation Show?

With the constraints that probabilities sum to 1 and expected score is fixed, the maximum-entropy distribution has exponential form. This is an information-theoretic derivation of Softmax; its constraints come from modeling assumptions and do not prove Softmax is the only correct normalization in every probability-modeling task.

---

## Summary: The Role and Boundary of Softmax

Softmax is common in classification and autoregressive generation because it has all of these properties:

**Basic requirements**:
- Arbitrary real inputs → positive outputs → sum of 1.
- Larger logits → larger probabilities, preserving order.
- Differentiable everywhere, with a simple gradient when paired with cross-entropy.

**Core mechanism**:
- It uses exponentials to turn additive evidence into multiplicative likelihood ratios.
- A logit difference of 2 gives probability ratio $e^2 ≈ 7$; a difference of 5 gives about $e^5 ≈ 150$.

**Training convenience**:
- With cross-entropy, the gradient is $p_i - y_i$.
- The exponential base changes only scale, which can be represented by temperature or logit scaling.

**Numerical stability**:
- Subtracting $\max(z)$ prevents overflow; underflow to 0 also matches the intended semantics.

**Theoretical view**:
- Exponential form follows under particular maximum-entropy constraints.
- It is one natural form in the exponential family of distributions.

**In one sentence**: Softmax uses exponentials to turn comparable scores into normalized probabilities and forms a simple training interface with cross-entropy. It is widely used, but not the only possible normalization design.
