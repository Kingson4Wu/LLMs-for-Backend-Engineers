# Mathematical and Machine-Learning Foundations of AI: A Panorama

This part does not list mathematical terms. It establishes a traceable learning chain: data is represented numerically; a model makes predictions with a parameterized function; a loss measures error; gradients and an optimizer modify parameters accordingly; validation checks whether the modifications hold on new examples. Later chapters expand the key stages of vectors, probability, error, and training.

## Artificial Intelligence: Modeling, Optimization, and Engineering Implementation

Artificial intelligence is not mysterious technology. Its essence is:

* **Mathematics**: describing problems, characterizing patterns, and defining objectives.
* **Algorithms**: searching and optimizing mathematical models.
* **Computers**: implementing and accelerating computation.

In one sentence:

> Artificial intelligence = mathematical models + optimization algorithms + engineering implementation

Model capability is constrained jointly by modeling, data, optimization, and available compute. Compute can expand trainable model and data scale, but cannot by itself decide what a model learns.

---

## Machine Learning: Function Estimation and Function Approximation

### From Data to a Mapping

In machine learning:

* Data is ultimately represented as **numerical vectors**.
* A model learns a mapping:

$$
\text{input vector} \rightarrow \text{output vector}
$$

This is learning a function:

$$
\hat{y} = f_\theta(x)
$$

where $\theta$ is the model parameter.

### The Function-Approximation View

The function governing a real-world pattern is usually unknown and can only be observed through finite samples.

Machine learning:

* defines a loss function.
* selects a model form, such as a linear model or neural network.
* trains parameters with data.

It finally obtains:

> an approximation to the true function

It is therefore accurate to say:

> a machine-learning problem is fundamentally a function-estimation/function-approximation problem

---

## Loss and Objective Functions: From Pointwise Error to a Global Criterion

This is the easiest level to confuse and one of the most important.

### Loss Function

A loss function measures:

> a model's prediction error on one individual example

For example, squared error:

$$
\ell(y, \hat{y}) = (y - \hat{y})^2
$$

It answers:

> How seriously was this prediction wrong?

### Objective Function

Training actually optimizes a **global function**:

$$
J(\theta) = \frac{1}{N}\sum_{i=1}^N \ell_i + \lambda \Omega(\theta)
$$

Where:
- The first term is average loss, or empirical risk, which fits the data.
- The second term is a regularizer that limits model complexity.

**Conclusion (very important):**

> A loss function is local error; an objective function is the overall criterion actually minimized during training.

In the simplest case, the objective can equal average loss. Common objectives can also include regularization, multiple sub-objectives, or constraints. Many language-model training procedures directly minimize average token cross-entropy and need not explicitly write a regularizer.

---

## A Unified View: AI Is an Optimization Problem

Whether machine learning or deep learning, the central task can be unified as:

> minimizing or maximizing an objective function in parameter space

### Global and Local Optima

* **Global minimum**: smallest in the entire space.
* **Local minimum**: smallest in one neighborhood.

In high-dimensional parameter space:

* Global search is infeasible.
* Practical algorithms usually find only sufficiently good solutions.

The engineering standard is:

> objective value sufficiently small + acceptable generalization

---

## Calculus: The Mathematical Basis of Optimization

### Derivatives and Gradients

* Derivative: the rate at which a function changes.
* Gradient: the vector of first derivatives of a multivariable function.

The gradient direction is:

> the direction of fastest increase

Therefore, the **negative-gradient direction** is the direction of fastest decrease.

### Common Optimization Algorithms

All mainstream training algorithms rely underneath on derivatives and matrix operations:

* Gradient descent (GD).
* Stochastic gradient descent (SGD).
* Newton and quasi-Newton methods (BFGS/L-BFGS).

---

## Convex Functions: The Difference Between Theoretical Guarantees and Deep Learning

### Guarantees from Convexity

If an objective is convex:

* Every local minimum = the global minimum.
* Optimization is clean.

This is common in traditional machine learning:

| Model | Loss | Objective |
|------|------|----------|
| Linear regression | Squared error | Convex |
| Logistic regression | Log loss | Convex |
| SVM | Hinge loss | Convex |

### Why Deep Learning Is Nonconvex

In neural networks:

* Models are highly nonlinear.
* Parameters are strongly coupled.
* Activations are stacked across layers.

The result is:

> Even when the loss-function form is convex, the objective remains nonconvex with respect to parameters.

---

## Why Deep Learning Can Still Work

The key is not a theoretical guarantee, but engineering reality:

1. **It does not seek a global optimum.**
   Sufficient performance is enough.

2. **Optimization landscape and parameterization**
   Deep networks have saddle points, flat regions, and many functionally similar parameter solutions. Their distribution depends on architecture, data, and parameterization; it cannot simply be reduced to “few local minima.”

3. **Randomness in SGD**
   Noise from mini-batches can sometimes help search different regions, but this is an empirical effect rather than a universal guarantee of escaping saddle points.

4. **Engineering techniques**
   Initialization, regularization, BatchNorm, residual structures, and more.

In one sentence:

> Nonconvex optimization is difficult in theory and controllable in engineering.

---

## Linear Algebra: The Skeleton of Deep Learning

Linear algebra is the core computational language of modern deep learning; it also relies on calculus, probability and statistics, and numerical optimization:

* Vector representations and embeddings.
* Neural-network forward passes.
* CNNs, Attention, and Transformers.

It is fair to state:

> Without linear algebra, there is no modern deep learning.

---

## Perceptrons, Activation Functions, and Bias

### Perceptron Model

$$
y = f(w \cdot x + b)
$$

* $w$: weights, which determine direction and sensitivity.
* $b$: bias, which determines threshold or translation.

### The Role of Bias

Bias:

> prevents a decision boundary from being forced through the origin

Geometrically:

* Weights determine direction and slope.
* Bias determines the starting position.

Without bias, model expressiveness is severely limited.

### The Meaning of Activation Functions

Early step functions have no useful gradient almost everywhere and are hard to train with gradient methods. Modern networks use differentiable or almost-everywhere differentiable functions with usable subgradients, such as Sigmoid, ReLU, and Tanh, to support gradient descent.

---

## Training Mechanism: How Parameters Learn from Data

Programmers are responsible for:

* Model structure.
* Loss function.
* Data preparation.

**The numerical values of parameters:**

> are learned entirely automatically by training

Even with the same structure, different data leads to different learned models.

---

## Training, Validation, and Testing: How to Check Generalization

Training repeatedly uses data to update parameters, but doing well on seen data does not mean handling new requests. To separate parameter learning, model selection, and final evaluation, available examples are often divided by responsibility:

| Data | What it is used for | What it must not establish |
| --- | --- | --- |
| Training set | Compute loss, backpropagate, and update parameters | Prove generalization to new examples |
| Validation set | Compare architecture, hyperparameters, and checkpoints; decide whether to continue, adjust, or stop | Serve as the final unbiased scorecard |
| Test set | Estimate performance on unseen examples after model selection | Be repeatedly inspected and then used for tuning |

Validation data can affect engineering choices; test data should be kept until the end. If a team repeatedly changes models, prompts, or hyperparameters according to test scores, the test set indirectly participates in optimization and its final score no longer reliably represents truly unseen data. Projects need not always have three fixed datasets: cross-validation, temporal splits, or online evaluation can also be used. The key is to preserve independent evidence that did not participate in selection.

This is the question that **generalization** answers: did a model learn transferable relationships, or only adapt to examples it has already seen? The next section, overfitting, is the typical failure of this distinction.

---

## Overfitting: Memorizing Examples Rather Than Learning a Pattern

Typical characteristics:

* Very good training-set performance.
* Very poor test-set performance.

The underlying reason is:

> model complexity > the complexity supported by the data

Approaches:

* Regularization.
* Data augmentation.
* Controlling model size.
* Dropout, early stopping, and related techniques.

---

## Neural Networks and Deep Learning

* Neural networks: combinations of multilayer differentiable perceptrons.
* Deep learning: deeper neural networks.

The effect of greater depth is:

> with similar parameter scale, approximating more complex functions

The theoretical explanation remains under study, while engineering results have repeatedly verified the effect.

---

## Reinforcement Learning: From Supervised Learning to Interactive Learning

The goal of reinforcement learning is not minimizing prediction error, but:

> maximizing long-term cumulative reward

Characteristics:

* No standard answer.
* Learning through trial and error.
* Reward signals drive parameter updates.

---

## Thread of the Whole Article

> Artificial intelligence uses mathematics to define objectives, optimization to find parameters, and data to approximate unknown functions. Theory concerns convexity and optimality; engineering concerns effectiveness, stability, and generalization.

---

## References

* [A concise overview of AI mathematics](https://kingson4wu.github.io/zh/posts/20260120-ai/)
