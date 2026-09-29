# Residual Connections: Why Deep Networks Remain Trainable

## Why More Depth Does Not Necessarily Make Fitting Easier

In deep learning, a natural intuition is:

> The deeper a neural network is, the greater its expressive capacity, so its performance should be better.

Yet extensive experiments show a counterintuitive phenomenon as networks become deeper—for example, from tens to hundreds of layers:

- **Training error increases.**
- Even on the training set, the model cannot match a shallower network's performance.

This is called the **deep-network degradation problem**.

Importantly, this is neither caused by overfitting nor merely vanishing or exploding gradients. It is a problem in which a deep model becomes difficult to optimize.

---

## Why a Plain Deep Stack Can Degrade

In theory, a deeper network should at least be able to simulate a shallow network:

- provided that added layers learn an **identity mapping**;
- the network's performance should not decline.

In practice:

> **Ordinary neural networks are not good at learning an identity transformation.**

Making several layers keep their output equal to their input ($y=x$) is not numerically easy to optimize.

This reveals the nature of degradation:

- it is not that the model is insufficiently powerful;
- **the optimization target itself is unfriendly.**

---

## The Intuition Behind Residual Connections

The core idea of a residual connection can be understood with an everyday analogy.

- A traditional network:

  > learns one complete mapping from scratch.

- The residual idea:

  > learns only the part that needs correcting on top of the original input.

In other words, rather than learning the target function $H(x)$ directly, learn its deviation from the input.

---

## The Form of a Residual Connection

Mathematically, residual learning is implemented by a reparameterization.

The traditional form is:

$$
y = H(x)
$$

The residual form is:

$$
F(x) = H(x) - x
$$

$$
y = F(x) + x
$$

Here:

- $x$: the input.
- $F(x)$: the residual function.
- The path directly adding $x$ to the output is the **residual connection** (or skip connection).

---

## Why Residual Connections Work

### 5.1 Identity Mapping Becomes Easy

If certain layers make no contribution to the task:

- A plain network has difficulty approximating an identity mapping.
- A residual network need only set $F(x)=0$.

This makes:

> **“Zero correction” a stable solution.**

It makes adding layers without destroying an existing representation possible in function form, and usually makes deep networks easier to optimize; actual training performance still depends on initialization, normalization, optimizer, and data, and cannot be guaranteed by residual connections alone.

---

### 5.2 Gradient Propagation Is Smoother

For a residual structure:

$$
y = F(x) + x
$$

During backpropagation:

$$
\frac{\partial y}{\partial x} = \frac{\partial F(x)}{\partial x} + 1
$$

The constant “+1”:

- provides a direct route for gradients;
- significantly eases the vanishing-gradient problem.

---

### 5.3 Optimization Becomes More Friendly

Empirical and theoretical analysis suggest:

- residual structure makes the loss landscape smoother;
- gradient-descent methods converge more easily.

This is key to successfully training extremely deep networks.

---

## The Boundary of Residual Connections

The answer is no.

Modern neural networks do not use residual connections around **every layer**, but rather:

> **at the module (block) level.**

This is because:

- residuals on every layer can weaken nonlinear expressiveness;
- some layers aim to change the representation space and are unsuitable for residuals.

---

## Where Residual Connections Appear in Classic Models

### ResNet

ResNet's basic unit is not one layer but a residual block:

- two or three convolutional layers plus nonlinearities;
- a shortcut wrapped around the outside.

The residual connection acts on the whole module rather than every layer.

---

### Transformer

In a Transformer:

- the Attention sublayer;
- the Feed-Forward sublayer.

Each sublayer is surrounded by a residual connection, while its interior remains a conventional structure.

This shows that:

> Residuals are a **structural design principle**, not a particular operator.

---

## When Residual Connections Are Unsuitable

Places that usually do not use residual connections include:

- input embedding layers;
- layers with downsampling or sharp dimensional changes;
- output layers such as classification or regression heads;
- very shallow networks.

Residuals are better suited to:

> **progressively refining features within the same representation space.**

---

## Summary

The core value of residual connections is:

1. reparameterizing the learning target to make optimization easier;
2. providing a stable route for gradients;
3. reducing the risk of optimization degradation in deep models.

Thus, a modern deep-learning design paradigm can be summarized as:

> **Use network layers to construct representations; use residual connections to give deep optimization more direct paths.**

This is why residual connections have become a basic component of deep models from ResNet to Transformer.
