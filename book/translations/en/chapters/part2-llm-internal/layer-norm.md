# LayerNorm: Keeping Representations Numerically Stable

## The Problem This Section Addresses

LayerNorm calculates a mean and variance across the feature dimensions of one token, then normalizes and applies learned scaling and shifting. It neither compares different tokens nor uses statistics from other examples in the same batch.

In a Transformer, LayerNorm and residual paths help layers retain more stable representation and gradient conditions. Its exact location and form vary by architecture. It is not a way to force every value into one fixed range; it is a learnable normalization transform.

## How the Mechanism Works

### The Core Operation: Normalize One Token’s Vector

At a given Transformer layer, a token is represented by a d-dimensional vector x = (x1, x2, ..., xd).

LayerNorm performs three operations:

```
Step 1: Compute the mean
μ = (x₁ + x₂ + ... + x_d) / d

Step 2: Compute the variance
σ² = [(x₁-μ)² + (x₂-μ)² + ... + (x_d-μ)²] / d

Step 3: Standardize, then apply an affine transformation
LN(x)_i = γ × (x_i - μ) / √(σ² + ε) + β
```

γ and β are learned parameters, typically initialized to γ=1 and β=0.

### Intuition: Bring the Vector Back Around the Origin

```text
Before normalization: x = [1000, 1001, 999]   ← Large values, small relative differences
After standardization: ≈ [0, 1.225, -1.225]   ← Mean 0, variance 1 (ignoring ε)
```

After standardization, the vector has approximately zero mean and unit standard deviation. This improves the numerical condition of the layer input; it does not guarantee that every value in the whole network remains stable.

γ and β let the model learn an appropriate scale and shift instead of being forced to keep a fixed standardized representation.

### Why Transformers Particularly Need Normalization

Three interacting structures can create numerical instability:

**1. Attention combines value vectors by weighted summation**

If a head produces large values, it can dominate later computation; if one feature has a much larger scale, it can suppress others. Attention weights alone do not fix the scale of the value vectors.

**2. Residual connections repeatedly accumulate updates**

Output at layer l+1 = output at layer l + transformation at layer l

Residuals preserve an information path while adding a sublayer update. The update scale depends on the parameters and inputs: it need not grow continuously, and residuals alone do not guarantee stability.

**3. Softmax is highly sensitive to scale**

The useful operating range of attention’s Softmax depends on its input scale:
- Very large differences → a nearly one-hot distribution, often with very small gradients.
- Very small differences → a nearly uniform distribution, with little attention focus.

Together, these effects make normalization important for Transformer training, alongside residual design, initialization, and optimization.

### Where LayerNorm Appears in a Transformer

A Pre-LN Transformer, a common arrangement in modern large models:

```
Input x
  │
  ├─→ LayerNorm(x)
  │       │
  │       ▼
  │    Self-Attention(LayerNorm(x))
  │       │
  │       ▼
  │      y = x + Attention(LayerNorm(x))   ← Residual connection
  │       │
  │       ▼
  ├─→ LayerNorm(y)
  │       │
  │       ▼
  │    Feed-Forward Network(LayerNorm(y))
  │       │
  │       ▼
  │      y + FFN(LayerNorm(y))         ← Residual connection
  │       │
  └───────┘
```

The division of responsibilities:
- **Attention** manages information exchange: which other positions to consult.
- **Residual connections** preserve existing information.
- **LayerNorm** improves the layerwise numerical conditions.

### LayerNorm Versus BatchNorm

BatchNorm is common in computer vision. LayerNorm is generally better suited to Transformers because it does not depend on batch composition:

| Property | BatchNorm | LayerNorm |
|----------|-----------|-----------|
| Normalization axis | Across examples in a batch | Across features of one example/token |
| Uses other examples? | Yes during training | No |
| Sensitive to batch composition? | Yes; variable lengths and padding complicate statistics | Independent of the batch |
| Inference with batch size 1 | Depends on reliable stored training statistics | No batch-size dependence |

LayerNorm is often preferred because it keeps normalization local to each token and does not depend on batch composition. That preference does not make BatchNorm impossible in every NLP or Transformer variant.

## Formalization

LN(x) = γ ⊙ (x - μ) / √(σ² + ε) + β

where:
- μ = Σ xi / d is the mean.
- σ² = Σ(xi - μ)² / d is the variance.
- ε is a small constant preventing division by zero.
- γ and β are learned scale and shift parameters.

## Section Summary

LayerNorm applies learnable mean–variance normalization across one token’s feature dimensions without batch statistics. It improves layerwise numerical conditions and supports stable training together with residual design, initialization, and optimization; it is not a stability guarantee by itself.

## Further Reading

- [Transformer Architecture](../part2-llm-internal/transformer-architecture.md) — Pre-LN and Post-LN placement and their effects on training stability.
