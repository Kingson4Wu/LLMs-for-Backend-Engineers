# Optimizers: How Gradients Become Parameter Updates

## The Problem This Section Addresses

Backpropagation calculates loss gradients for parameters, but an update rule is still needed to decide how to use them. The learning rate sets an overall step size; momentum and adaptive statistics address gradient scale and variation across directions and parameters.

An optimizer does not create model capability or replace data and objectives. It determines how each training step turns an existing gradient signal into a parameter change, affecting stability, convergence speed, and the results training can reach.

## How the Mechanism Works

### SGD: A Simple Global-Scale Baseline

```python
theta = theta - lr * gradient  # Same learning-rate multiplier for every parameter
```

SGD applies **one global scale to gradient updates**. This does not mean that SGD theoretically assumes all parameters are identical, but one scale can be hard to tune when curvature, gradient magnitude, or update frequency differ substantially.

Parameters need not have similar optimization geometry. In a Transformer, some rows of an input embedding are updated only when their tokens occur, while feed-forward weights typically receive gradients more often. A global learning rate may move slowly along some directions and oscillate along others. With momentum and a suitable schedule, SGD can still train many models effectively.

```
Illustrative loss contours:

     Steep direction (FFN)
         |
    x <- oscillation
     \   /
      \ /  <- SGD zigzags through a valley
        -> Shallow direction (embedding)
```

### Momentum: Smooth Oscillation with Inertia

```python
velocity = momentum * velocity + gradient
theta = theta - lr * velocity
```

The physical analogy is a ball rolling over the loss surface. Consistent directions accumulate velocity; alternating sideways contributions tend to cancel.

Momentum improves **directional stability**, but it does not provide Adam’s per-parameter scaling based on squared-gradient history.

### Adam: Adaptive Updates for Each Parameter

Adam gives each parameter its own effective throttle.

It maintains:
- **First moment m_t**: an exponential moving average of gradients, similar to momentum.
- **Second moment v_t**: an exponential moving average of squared gradients.

```python
m = beta1 * m + (1 - beta1) * gradient        # First moment
v = beta2 * v + (1 - beta2) * (gradient ** 2) # Second moment

theta = theta - lr * m / (sqrt(v) + epsilon)   # Simplified: bias correction omitted
```

**The adaptation**:
- Persistently large gradients increase v_t, reducing the normalized update scale.
- Smaller or sparse gradient history can produce a smaller v_t and relatively larger scaling.

### AdamW: Decouple Weight Decay

With L2 regularization added to Adam’s gradient, the regularization contribution also gets scaled by sqrt(v_t), making its effective strength parameter-dependent.

AdamW **decouples weight decay** from the adaptive gradient calculation and applies it directly to parameters:

```python
theta = theta - lr * m / (sqrt(v) + epsilon) - lr * weight_decay * theta
```

Parameters in the same decay group receive the same proportional shrinkage, separating that effect from gradient adaptation. Its effect on generalization still depends on the data, model, and hyperparameters.

### Warmup: Protect the Start of Training

At the start of training, gradients, activations, and moment estimates are still forming. Immediately using the full learning rate can produce overly large updates, especially in deep Transformer training recipes.

Warmup gradually increases the learning rate over the first N steps:

```
Learning rate
  ^
  |          ___________
  |         /
  |        /
  |_______/________________> Training steps
        Warmup
```

This reduces the risk created when large early steps coincide with statistics that are still settling. Whether warmup is needed and how long it lasts depend on the training recipe.

### The Progression

```
SGD          -> Limitation: global scaling can cause oscillation
  +- Momentum  -> Smooth directions, still no squared-gradient adaptation
      +- Adam  -> Per-parameter adaptive scaling
          +- AdamW -> Decouple weight decay
              +- Warmup -> Gradual startup
```

## Formalization (Notes)

**Adam with bias correction**:

```
theta_{t+1} = theta_t - lr * (m_hat_t / (sqrt(v_hat_t) + eps))
```

where:
- m_hat_t = m_t / (1 - beta1^t) corrects first-moment initialization bias.
- v_hat_t = v_t / (1 - beta2^t) corrects second-moment initialization bias.
- Common illustrative values are beta1 = 0.9, beta2 = 0.999, eps = 1e-8.

**PyTorch example**:

```python
import torch.optim as optim

# An illustrative Transformer training configuration
optimizer = optim.AdamW(
    model.parameters(),
    lr=1e-4,
    weight_decay=0.1,
    betas=(0.9, 0.999)
)

# A warmup schedule is often followed by cosine decay
```

## Section Summary

AdamW and warmup are a common combination in Transformer training: the former uses gradient history to adapt updates, while the latter reduces the risk from unstable early statistics. They are parts of a training recipe, not a default answer guaranteed to work apart from model, data, and learning-rate design.

## Further Reading

- [Backpropagation](../part1-math-foundations/backpropagation.md) — Where gradients come from.
- [Vanishing and Exploding Gradients](../part1-math-foundations/vanishing-exploding-gradients.md) — Why optimization choices matter for training deep networks.
