# Perceptrons: How Parameters Learn from Error

A perceptron sums inputs with weights and then transforms the result. It makes two adjacent but different questions visible: the network structure determines which functions can be represented; training uses loss gradients to adjust the weights. XOR shows the boundary of a single-layer perceptron. This chapter follows how error feedback can shape piecewise-linear functions.

## The Basic Form of a Neural Network

Neural networks do not begin by hand-writing a polynomial such as \(x_1^2+x_2^2+x_3^3\). Their basic unit is

$$
y=f(w_1x_1+w_2x_2+\cdots+w_nx_n+b),
$$

where \(x_i\) are input features, \(w_i\) and \(b\) are learned parameters, and \(f\) is an activation function chosen by the architecture. Nonlinear capacity comes from activations composed across layers, rather than from explicitly inserting squared or cubed terms.

## Structure Is Not Learned Parameters

It helps to separate two levels. The designer chooses the number of layers, connections, and activation types. Training learns the numerical weights and biases. A network does not select a closed-form analytic formula; within a fixed structure, repeated parameter updates shape the function it implements.

For a single layer,

$$
y=f(w^\top x+b).
$$

Even with an activation function, its classification boundary remains linear. A single perceptron cannot represent nonlinear regions such as XOR or a circle. Hidden layers create the additional expressive capacity.

## How a Complex Function Is Learned

Learning is continuous numerical optimization:

1. parameters begin from an initialization unrelated to the target;
2. a forward pass computes the current function's output;
3. a loss measures prediction error;
4. backpropagation computes gradients of that loss with respect to parameters;
5. gradient descent makes a small update;
6. repeated updates gradually reshape the function.

The model does not recognize an analytic formula in the way a person might. It moves through parameter space toward lower loss.

## ReLU Creates Breakpoints

For geometric intuition, consider

$$
\operatorname{ReLU}(z)=\max(0,z),\qquad h(x)=\operatorname{ReLU}(wx+b).
$$

For one-dimensional input, the output is zero where \(wx+b<0\), and a line where \(wx+b>0\). One ReLU unit therefore begins contributing a linear segment after a boundary. That boundary, or breakpoint, is

$$
t=-\frac{b}{w}.
$$

There is no separate trainable parameter called \(t\). Training changes \(w\) and \(b\); the breakpoint moves as their ratio changes.

For a one-hidden-layer network,

$$
f(x)=\sum_i a_i\operatorname{ReLU}(w_ix+b_i)+c,
$$

the function is piecewise linear: it is linear on each interval, while its first derivative can jump at breakpoints. Complexity comes from many breakpoints and the sum of their active linear pieces.

## Three ReLUs, Worked Through

Consider

$$
\hat y=\operatorname{ReLU}(x+1)+\operatorname{ReLU}(x)+\operatorname{ReLU}(x-1).
$$

The breakpoints \(-1\), \(0\), and \(1\) divide the input axis into four intervals. They are activation boundaries, not lines in the output graph.

| Input interval | Active units | Output |
| --- | --- | --- |
| \(x<-1\) | none | \(0\) |
| \(-1<x<0\) | \(\operatorname{ReLU}(x+1)\) | \(x+1\) |
| \(0<x<1\) | first two | \(2x+1\) |
| \(x>1\) | all three | \(3x\) |

The horizontal first segment is the sum when every ReLU is inactive; each later segment is the sum of all currently active units. No one ReLU “draws” the whole polyline.

```text
y
|               /
|            __/       all three active
|         __/          first two active
|      __/
|   __/                first active
|__/                   none active
+------------------- x
   -1     0     1
```

## Approximation and Its Limit

A parabola \(y=x^2\) has continuously changing slope. A finite ReLU network cannot produce continuous curvature: in one dimension it remains piecewise linear. It can, however, approximate a smooth curve on any finite interval by placing enough breakpoints close together, so its slopes change in sufficiently small steps.

For a single-hidden-layer ReLU network approximating \(x^2\) on \([-M,M]\) with maximum error \(\varepsilon\), a representative bound is

$$
N=O\left(\frac{M^2}{\varepsilon}\right).
$$

A wider interval or tighter error tolerance requires more pieces. The point is not that this construction is how practical models are manually designed; it shows what parameters and nonlinear units can express, and why representation capacity remains separate from whether optimization finds a useful solution.

## Summary

Neural networks do not explicitly construct high-degree polynomials. Linear transformations plus nonlinear activations create their expressive functions. In one dimension, ReLU networks make piecewise-linear functions; breakpoints arise from learned weights and biases, and output segments are sums of active units. Finite networks can approximate smooth functions on bounded intervals without becoming those functions exactly.
