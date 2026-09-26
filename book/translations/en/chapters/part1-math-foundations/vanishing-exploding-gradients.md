# Vanishing and Exploding Gradients: Why Deep Networks Are Hard to Train

## The Problem This Section Addresses

In a deep network, a gradient in backpropagation passes through many local derivatives and parameter matrices. Their product can approach zero or grow rapidly.

Vanishing gradients leave early layers with almost no update signal. Exploding gradients make updates unstable and can create numerical problems. This is one training difficulty in deep networks, not a matter of how far model information travels.

## How the Mechanism Works

### Vanishing Gradients: A Weakening Signal

Backpropagation multiplies derivatives according to the chain rule. If each factor is smaller than one, the product decays exponentially:

```text
Suppose each layer contributes a factor of approximately 0.5:

After 5 layers:   0.5⁵  ≈ 0.03    ← Getting small
After 10 layers:  0.5¹⁰ ≈ 0.001   ← Near zero
After 50 layers:  0.5⁵⁰ ≈ 10⁻¹⁵  ← Effectively gone
```

**Consequence**: Parameters near the input can receive very small updates, making learning slow. This depends on the whole computational path; it is not one layer becoming permanently disconnected.

### Exploding Gradients: Uncontrolled Amplification

Conversely, factors larger than one can produce exponential growth:

```text
Suppose each layer contributes a factor of approximately 1.5:

After 5 layers:   1.5⁵  ≈ 7.6    ← Growing
After 10 layers:  1.5¹⁰ ≈ 57.7   ← Strong amplification
After 50 layers:  1.5⁵⁰ ≈ 10⁸    ← Numerical explosion
```

**Consequence**: Parameter updates become enormous, loss may become NaN or Inf, and training diverges.

### Activations as Gradient-Propagation Factors

At each layer, backpropagation multiplies by the activation derivative. Those derivatives differ substantially:

| Activation | Positive-side derivative | Negative-side derivative | Effect on gradients |
|------------|--------------------------|--------------------------|---------------------|
| Sigmoid | Maximum 0.25 at x=0 | Approaches 0 in saturation | Nearly blocks gradients at both extremes |
| Tanh | Maximum 1 | Approaches 0 in saturation | Better than Sigmoid, but still saturates |
| ReLU | Always 1 | Always 0 | Preserves positive-side gradients but can kill neurons |
| GELU | Approximately 1 for large positive inputs | Smooth transition | Balances gradient propagation with smoothness |

### Residual Connections: A Direct Gradient Path

Residual connections are a central structural response to vanishing gradients. An extra direct path from input to output lets gradients bypass intermediate transformations.

**Without a residual connection**:

y = F(x), derivative = ∂F/∂x

A very small ∂F/∂x attenuates the gradient.

**With a residual connection**:

y = x + F(x), derivative = 1 + ∂F/∂x

The identity term provides a shorter gradient path. When ∂F/∂x is small, the total derivative is close to 1. It does not guarantee that every gradient direction avoids vanishing or explosion, because a matrix Jacobian can still amplify, shrink, or cancel in particular directions.

```
Traditional deep network:
x → Layer1 → Layer2 → ... → Layer100 → output
(The gradient passes through 100 multiplicative factors.)

Residual network:
x ──────────────────────────────────→ + ──→ output
    → Layer1 → Layer2 → ... → Layer100 ──┘
(The direct gradient path contributes an identity factor.)
```

### Combining Pre-LN and LayerNorm

Residual paths improve training conditions, but activation scale, initialization, learning rate, and normalization placement still affect stability. Designs such as Pre-LN normalize a sublayer's input and are common stable arrangements; architectures need not share one fixed residual-and-normalization form.

## Formalization

**Residual formulas** in a Pre-LN structure, as used in GPT-style models and related normalization variants in models such as LLaMA:

```python
y = x + Attention(LayerNorm(x))      # Self-attention sublayer
z = y + FFN(LayerNorm(y))            # Feed-forward sublayer
```

**Local derivative**: in the scalar case, ∂(x + F(x))/∂x = 1 + ∂F/∂x. In a vector network this becomes the identity matrix plus the sublayer Jacobian. The identity term helps create short paths, but does not guarantee global gradient stability.

## Section Summary

Vanishing and exploding gradients can arise from the spectral scale of deep derivative chains and activation saturation: some directions keep shrinking while others keep growing. Residual connections add an identity path and shorten the chain that information and gradients must cross. They are an important condition for training deep models, alongside initialization, normalization, and optimization design.

## Further Reading

- [LayerNorm](../part2-llm-internal/layer-norm.md) — How normalization controls activation scale alongside residual connections.
- [Backpropagation](./backpropagation.md) — The chain rule explains both gradient instability and why residual paths help.
