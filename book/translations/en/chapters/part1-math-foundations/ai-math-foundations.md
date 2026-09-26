# AI Math and Machine Learning: A Bird's-Eye View

This part does not catalogue mathematical terms. It builds one traceable learning chain: data are represented as numbers; a parameterized function makes a prediction; a loss measures error; gradients and an optimizer change parameters; validation asks whether those changes still work on new examples. The following chapters unpack the important links in that chain.

## AI: Modeling, Optimization, and Engineering

AI is not a mysterious kind of computation. It combines three responsibilities:

- **mathematics** describes a problem, a pattern, and an objective;
- **algorithms** search or optimize within that mathematical model;
- **computer systems** implement and accelerate the required computation.

In this sense:

> AI = a mathematical model + an optimization algorithm + an engineering implementation.

Modeling choices, data, optimization, and available compute jointly constrain what a system can learn. More compute can make larger models and datasets practical; it does not by itself determine what the model learns.

## Machine Learning as Function Estimation

### From Data to a Mapping

In machine learning, inputs and outputs are ultimately represented as numerical vectors. A model learns a mapping:

$$
\text{input vector} \longrightarrow \text{output vector},
$$

or, more formally,

$$
\hat y = f_\theta(x),
$$

where \(\theta\) denotes the model parameters.

### The Function-Approximation View

The rule that generated observations in the real world is usually unknown, and only finitely many examples are available. Machine learning chooses a model family—linear functions, neural networks, and so on—defines how error is measured, and uses data to fit its parameters. The result is an approximation to an unknown relationship, not direct access to the relationship itself.

Machine-learning problems can therefore be understood as problems of **function estimation** or **function approximation**.

## Loss and Objective: Local Error and the Criterion Being Optimized

This distinction is central and often blurred.

A **loss function** measures the error for one example. Squared error, for instance, is

$$
\ell(y,\hat y)=(y-\hat y)^2.
$$

It answers: how wrong was this prediction?

Training, however, optimizes a dataset-level **objective** such as

$$
J(\theta)=\frac{1}{N}\sum_{i=1}^{N}\ell_i+\lambda\Omega(\theta).
$$

The first term is average empirical loss. The second is a regularizer that constrains model complexity. In the simplest case the objective is just average loss; in practice it may also include several objectives or constraints. Many language-model runs minimize average token cross-entropy without an explicitly written regularizer.

> Loss is local prediction error; the objective is the overall criterion minimized during training.

## One Unifying View: AI as Optimization

Much of machine learning and deep learning can be expressed as minimizing—or sometimes maximizing—an objective in parameter space.

### Global and Local Optima

A global minimum is the smallest value in the whole space. A local minimum is smallest only within a neighborhood. In high-dimensional parameter spaces, exhaustive global search is impractical, so useful algorithms normally seek a sufficiently good solution. Engineering acceptance is therefore not “proved globally optimal”; it is “the objective is low enough and generalization is acceptable.”

### Calculus and Gradients

A derivative describes a rate of change. For a multivariable function, the gradient is the vector of first derivatives. It points in the direction of fastest local increase, so the negative gradient is the local direction of fastest decrease.

Gradient descent, stochastic gradient descent (SGD), Newton-style methods, and quasi-Newton methods all rely on derivatives and matrix computation, though they use that information differently.

## Convexity and Why Deep Learning Is Different

For a convex objective, every local minimum is a global one. This gives unusually clean optimization guarantees for models such as linear regression with squared loss, logistic regression with log loss, and convex SVM objectives.

Neural networks are different. Layers, nonlinear activations, and coupled parameters make the objective non-convex with respect to parameters, even when a familiar loss has a simple form. Deep learning still works in practice because it does not require a certified global optimum. The optimization landscape can contain saddle points, flat regions, and many parameter settings with similar function; their distribution depends on the architecture, data, and parameterization. Mini-batch noise may sometimes help exploration, but it is not a universal escape guarantee. Initialization, regularization, normalization, residual paths, and optimization design make the process more controllable.

## Linear Algebra Is the Computational Skeleton

Modern deep learning also relies on calculus, probability, statistics, and numerical optimization, but linear algebra is its main computational language. Vectors represent inputs and embeddings; matrices implement neural-network transformations; attention and Transformer layers are organized as large matrix operations. Without linear algebra there is no practical modern deep learning.

## Perceptrons, Activations, and Biases

A basic neural unit has the form

$$
y=f(w\cdot x+b),
$$

where \(w\) is a learned weight vector, \(b\) is a learned bias, and \(f\) is an activation function. The weights set a direction and sensitivity; the bias shifts a threshold or decision boundary. Without a bias, a linear boundary is forced through the origin and the model loses useful expressiveness.

Early step functions have no useful gradient almost everywhere, making gradient-based learning difficult. Modern networks instead use differentiable or almost-everywhere differentiable functions with usable subgradients, such as sigmoid, tanh, and ReLU.

The programmer specifies the architecture, loss, and data pipeline. The numerical values of weights and biases are learned by training. The same architecture trained on different data can therefore become different models.

## Training, Validation, and Test: Checking Generalization

Good performance on examples a model has seen does not establish performance on new requests. A common division separates three responsibilities:

| Data split | Used for | Must not be used as |
| --- | --- | --- |
| Training set | Loss, backpropagation, and parameter updates | Proof of performance on unseen data |
| Validation set | Choosing architectures, hyperparameters, and checkpoints | The final unbiased scorecard |
| Test set | Estimating unseen performance after choices are complete | A repeatedly consulted tuning signal |

Validation data may influence engineering choices, whereas test data should remain independent evidence. If a team repeatedly changes a model, prompt, or hyperparameters after seeing test scores, the test set has indirectly become part of optimization and its score no longer reliably estimates unseen performance. A fixed three-way split is not mandatory: cross-validation, time-based splits, and online evaluation can serve related roles. The essential boundary is retaining evidence that did not guide the decision being assessed.

This is the question of **generalization**: did the model learn a transferable relationship, or only adapt to examples it has already seen?

## Overfitting, Neural Networks, and Reinforcement Learning

Overfitting is the familiar failure mode in which training performance is strong but test performance is poor: the model has enough effective complexity to remember particulars that available data do not support as a general rule. Regularization, data augmentation, model-size control, dropout, and early stopping can reduce that risk.

A neural network combines multiple differentiable perceptron-like units; deep learning uses deeper networks. Depth can represent complex functions more efficiently than a shallow arrangement with a comparable parameter budget, although the full theoretical account remains an active research area.

Reinforcement learning changes the signal rather than abandoning optimization. Instead of minimizing error against a supplied correct label, it aims to maximize long-term cumulative reward through interaction and trial and error. The reward still becomes a signal that changes parameters.

## The Thread Through This Part

AI uses mathematics to define an objective, optimization to search for parameters, and data to approximate an unknown function. Theory asks about properties such as convexity and optima; engineering asks whether training is stable, the result generalizes, and the system is useful. The next chapters make the representation, probability, error, and update steps concrete.

## References

- [AI Math Essentials](https://kingson4wu.github.io/zh/posts/20260120-ai/)
