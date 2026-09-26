# Activation Functions: Where Nonlinearity Comes From

Within a Transformer layer, Attention lets each token read from its context; the feed-forward network (MLP or FFN) transforms that representation at each position. An activation function sits between the MLP's two linear transformations. Its purpose is not to make numbers look nicer. Without a nonlinearity, however deep the network becomes, it is still effectively one affine layer.

This section starts with XOR, the smallest useful counterexample, then returns to LLMs to distinguish hidden-layer nonlinearities from Sigmoid and Softmax at the output.

## A Problem a Linear Model Cannot Solve: XOR

XOR outputs 0 when its two inputs are the same and 1 when they differ.

| $x_1$ | $x_2$ | XOR |
| --- | --- | --- |
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

On a plane, the two positive examples lie on one diagonal and the two negative examples on the other:

~~~text
x₂ ↑
   |
 1 |   ○       ●
   |
 0 |   ●       ○
   +----------------→ x₁
       0       1
●: output 1; ○: output 0
~~~

A binary linear classifier first computes $s=w^\mathsf{T}x+b$, then classifies by whether $s>0$ or $s<0$; in two dimensions, $s=0$ is a line. Even if a final Sigmoid is applied, Sigmoid is strictly monotonic, so the threshold stays on that same $s=0$ line. It therefore cannot separate these two diagonal pairs perfectly.

This can be proved directly. If a line separated the classes, every weighted average of samples in the same class would remain on that class's side. But the midpoint of the positive examples $(0,1)$ and $(1,0)$ is:

$$
\frac{(0,1)+(1,0)}{2}=(0.5,0.5)
$$

The midpoint of the negative examples $(0,0)$ and $(1,1)$ is also:

$$
\frac{(0,0)+(1,1)}{2}=(0.5,0.5)
$$

One point cannot lie strictly on both sides of a classification line, so no linear classifier separates all four points. Geometrically, the convex hulls of the two classes meet at the center; a line cannot separate overlapping regions.

Stacking linear layers does not help. For two layers,

$$
h=W_1x+b_1,\qquad y=W_2h+b_2
$$

substitution gives

$$
y=(W_2W_1)x+(W_2b_1+b_2)
$$

which is still one affine transformation. Depth changes how parameters are written, not the kind of function that can be represented.

## How ReLU Expresses XOR

ReLU is a basic and common nonlinearity:

$$
\operatorname{ReLU}(a)=\max(0,a)
$$

It clips negative inputs to zero and preserves positive ones:

~~~text
y
│        /
│       /
│      /
│_____/________ x
      0
~~~

The following two-unit network exactly expresses XOR on these four Boolean inputs:

$$
h_1=\operatorname{ReLU}(x_1-x_2),\qquad
h_2=\operatorname{ReLU}(x_2-x_1),\qquad
o=h_1+h_2
$$

Evaluating it point by point makes the mechanism visible:

| Input | $h_1$ | $h_2$ | $o$ |
| --- | --- | --- | --- |
| $(0,0)$ | 0 | 0 | 0 |
| $(1,0)$ | 1 | 0 | 1 |
| $(0,1)$ | 0 | 1 | 1 |
| $(1,1)$ | 0 | 0 | 0 |

Here $o=|x_1-x_2|$. Both units use the same boundary condition, $x_1=x_2$: one activates in the half-plane where $x_1>x_2$, the other in the opposite half-plane. They are not two crossing boundaries and do not directly form an X-shaped decision boundary. The point is that different computation paths run on the two sides of one boundary.

This does not mean real problems require hand-designed ReLU units; training learns their weights. It shows that each ReLU opens or closes a computation path according to the input, and later linear layers can combine those conditional results.

## What Nonlinearity Actually Changes

A ReLU network does not necessarily draw a smooth curve. For a fixed pattern of which ReLUs are active, the whole network remains affine. When an input crosses a unit's zero point, that pattern switches and the network moves into another locally linear region. A ReLU network can therefore be understood as many local linear rules joined according to the input.

This is the first-principles role of an activation: **it breaks the closure of affine transformations under composition, allowing depth to express nonlinear functions.** It supplies the possibility of representation; it does not automatically produce the right answer.

### Expressive Power Is Not Learning

These must be kept separate:

- **Expressive power:** whether the architecture and parameter space contain a function that can describe the target relation.
- **Training result:** whether optimization actually finds good parameters from data and keeps working on new inputs.

Activations chiefly address the first. Data, loss, optimization, initialization, and regularization influence the second. More layers or a different activation does not guarantee higher accuracy; it changes what a model can represent and how gradients propagate.

## Common Functions Have Different Jobs

### ReLU: Simple Piecewise Gating

ReLU has derivative 1 on the positive side and 0 on the negative side. This has direct consequences:

- it does not attenuate gradients on the positive side, which helps deep training;
- some units output zero for a given input, creating sparse activations; sparsity alone does not mean less overfitting;
- a unit that remains negative has zero gradient through itself and may be hard to revive; this is usually called dead ReLU.

These trade-offs made it a foundational hidden-layer choice.

### Sigmoid: Mapping One Score Between 0 and 1

$$
\sigma(a)=\frac{1}{1+e^{-a}}
$$

~~~text
y
1 |        _____
  |       /
  |      /
0 |_____/________ x
        0
~~~

Sigmoid maps real numbers to $(0,1)$ and is common for independent binary probabilities or gates. It saturates for large magnitudes, where its derivative approaches zero, so it is usually not the default for deep hidden layers.

### Tanh: A Zero-Centered Bounded Signal

$$
\tanh(a)=\frac{e^a-e^{-a}}{e^a+e^{-a}}
$$

Tanh maps values to $(-1,1)$ and is zero-centered. It appears in earlier RNNs and structures that need a bounded signed state. It can emit positive and negative signals, but does not remove the saturation problem in deep networks.

### Softmax: Competition Across a Vector, Not Hidden-Layer Gating

Softmax is nonlinear too, but it does not operate independently on each element:

$$
p_i=\frac{e^{z_i}}{\sum_j e^{z_j}}
$$

It turns a group of scores into a competitive distribution summing to 1, for multiclass outputs and Attention weights. Its job is normalization and selection, not giving an MLP piecewise expressiveness; see [Softmax: Turning Scores into Probabilities](softmax.md).

For example, Softmax maps `[2.0, 1.0, 0.1]` to about `[0.659, 0.242, 0.099]`. Raising one score changes every candidate's weight because all share one denominator; this is the crucial distinction from element-wise Sigmoid.

### Choosing by Position First

| Position or task | Common choice | Why |
| --- | --- | --- |
| General hidden layers | ReLU or a variant | Piecewise gating with unsaturated positive gradients |
| Independent binary outputs | Sigmoid | Each score independently maps to $(0,1)$ |
| Bounded signed state | Tanh | Zero-centered output with a fixed range |
| Mutually exclusive candidates or Attention | Softmax | Normalizes and creates competition across a vector |

This is not a fixed recipe. Position, loss, architecture, and training stability all matter; the LLM MLP below is a modern variant.

## Nonlinearity in an LLM Feed-Forward Network

The original Transformer used two linear transformations with ReLU between them in its position-wise feed-forward network. Later architectures use different variants: BERT-style models commonly use GELU, while many decoder LLMs use SiLU/Swish and gated variants such as SwiGLU. These are architecture choices, not the definition of every Transformer. The [original Transformer paper](https://arxiv.org/abs/1706.03762), [GELU paper](https://arxiv.org/abs/1606.08415), and [GLU variants paper](https://arxiv.org/abs/2002.05202) document this progression.

GELU and SiLU are smooth gating-like nonlinearities:

$$
\operatorname{GELU}(a)=a\Phi(a),\qquad
\operatorname{SiLU}(a)=a\sigma(a)
$$

Here $\Phi$ is the standard normal cumulative distribution function. The essential point is not to derive it here: unlike ReLU, they modulate signals smoothly instead of abruptly clipping at zero.

SwiGLU lets one projection gate another. Ignoring biases, a common notation is:

$$
\operatorname{MLP}(h)=\bigl(\operatorname{SiLU}(hW_g)\odot(hW_u)\bigr)W_d
$$

$\odot$ is element-wise multiplication. $W_g$ and $W_u$ project into a wider intermediate space, then $W_d$ projects back. Attention determines where a token reads from; this MLP combines features within that token's representation through nonlinearity and gating. [Transformer Architecture Through Data Flow](../part2-llm-internal/transformer-architecture.md) explains the complete layer.

~~~text
Representation h for one token
  ├─ W_g → SiLU → gate
  ├─ W_u → candidate features
  └─ element-wise product → W_d → new representation
~~~

## Section Summary

Without activations, any number of affine layers can be merged into one and cannot express relations such as XOR. Element-wise gates such as ReLU partition the input space, so a network can combine local linear rules; this adds expressive possibility, while learning remains a separate matter. Sigmoid, Tanh, Softmax, GELU, and SwiGLU have different jobs and should not be conflated merely because all are called activations.

## Further Reading

- [Perceptrons: How Parameters Learn from Error](./perceptron-learning.md) — How parameters are learned from loss rather than written by hand
- [Vanishing and Exploding Gradients](./vanishing-exploding-gradients.md) — How saturation, derivatives, and deep training affect one another
- [Transformer Architecture Through Data Flow](../part2-llm-internal/transformer-architecture.md) — How Attention, MLPs, residual paths, and normalization form a layer
