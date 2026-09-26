# Backpropagation: How Error Reaches Each Parameter

## The Problem This Section Addresses

Training needs to know how every parameter should change to lower final loss. A network contains many composed computations; perturbing each parameter separately to measure its effect would be slow and imprecise.

Backpropagation starts from final loss and uses the chain rule to calculate gradients for every intermediate quantity and parameter. A gradient is not an assignment of blame. It is the local rate at which loss changes under a small parameter change; an optimizer uses it to update parameters.

## How the Mechanism Works

### The Chain Rule: A Tool for Assigning Responsibility

The mathematical core is the chain rule. Suppose:

L = f(y), y = g(x)

Then the effect of x on L is the product of the effects along the two steps:

dL/dx = dL/dy × dy/dx
In the failure-tracing analogy:
- dL/dy measures your responsibility, as the owner of y, for the final loss.
- dy/dx measures the upstream component x’s responsibility for a change in y.
- Their product measures how much x influences the loss through y.

### A Complete Computational Graph

Consider a branching network:

```
            h2 = w2 · h1
          ↗
x ──→ h1                ──→ y = h2 + h3 ──→ L
          ↘
            h3 = w3 · h1
```

Its definition:

h₁ = w₁ · x
h₂ = w₂ · h₁
h₃ = w₃ · h₁
y  = h₂ + h₃
L  = (1/2) × (y − t)²
Use x=2, t=12, w1=1, w2=2, w3=3.

**Forward pass: compute loss**

```text
h1 = 1 × 2 = 2
h2 = 2 × 2 = 4
h3 = 3 × 2 = 6
y  = 4 + 6 = 10
L  = (1/2) × (10 - 12)² = 2     ← Loss
```

**Backward pass: trace responsibility**

```text
Step 1: ∂L/∂y = y - t = 10 - 12 = -2    ← Start at the endpoint

Step 2: Branch—the gradient propagates along both paths
  ∂L/∂h2 = ∂L/∂y × ∂y/∂h2 = -2 × 1 = -2
  ∂L/∂h3 = ∂L/∂y × ∂y/∂h3 = -2 × 1 = -2

Step 3: Reach w2 and w3
  ∂L/∂w2 = ∂L/∂h2 × ∂h2/∂w2 = -2 × 2 = -4
  ∂L/∂w3 = ∂L/∂h3 × ∂h3/∂w3 = -2 × 2 = -4

Step 4: Accumulate gradients—the crucial step
  h1 affects both h2 and h3, so add responsibility from both branches
  ∂L/∂h1 = ∂L/∂h2 × ∂h2/∂h1 + ∂L/∂h3 × ∂h3/∂h1
         = (-2) × 2 + (-2) × 3 = -10

Step 5: Reach w1
  ∂L/∂w1 = ∂L/∂h1 × ∂h1/∂w1 = -10 × 2 = -20
```

The resulting gradients:

| Parameter | Gradient | Interpretation |
|-----------|----------|----------------|
| w1 | -20 | Greatest sensitivity in this example, through the longest paths |
| w2 | -4 | Directly affects the output |
| w3 | -4 | Directly affects the output |

### Two Key Concepts

**Gradient distribution**: A backward traversal through a branching operation passes gradient contributions along all relevant branches.

**Gradient accumulation**: When backward paths meet at a shared node, their contributions add, because that node influences the result through multiple forward paths.

### Gradient Descent: Acting on the Result

Backpropagation computes gradients; gradient descent updates the parameters:

w ← w − η × dL/dw

- Negative gradient, as for w₁ here: increasing the parameter locally lowers loss → **increase w₁**.
- Positive gradient: decreasing the parameter locally lowers loss → **decrease w**.

**The chain rule is the tracing tool, backpropagation organizes the tracing process, and gradient descent acts on its findings.**

## Formalization

Chain rule across steps: ∂L/∂w₁ = (∂L/∂h₁) · (∂h₁/∂w₁)

Gradient descent:

```python
for _ in range(num_epochs):
    # Forward pass: compute loss
    loss = forward_pass(model, x, y)

    # Backward pass: compute gradients
    grads = backward_pass(loss, model)

    # Update parameters
    for param, grad in zip(model.parameters(), grads):
        param -= learning_rate * grad
```

## Section Summary

Backpropagation is not new mathematics. It systematically applies the chain rule and addition of derivative contributions to a complex computational graph. Beginning with the final loss, it traces each node and parameter’s responsibility layer by layer. Gradient descent then updates the parameters. Vanishing and exploding gradients arise when these chains become long.

## Further Reading

- [Vanishing and Exploding Gradients](./vanishing-exploding-gradients.md) — What happens when long chains multiply gradients, and how residual connections provide a direct path.
- [LayerNorm](../part2-llm-internal/layer-norm.md) — How normalization stabilizes numerical values during gradient propagation.
- [Cross-Entropy](./cross-entropy.md) — Softmax plus cross-entropy gives the especially simple logit gradient p_i - y_i.
