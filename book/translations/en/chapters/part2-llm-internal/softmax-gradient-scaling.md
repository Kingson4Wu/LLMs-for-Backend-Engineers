# Scaled Dot Products: Why Softmax Gradients Become Extreme

Attention uses dot products to score the match between queries and keys. If components of those vectors have comparable variance, adding more dimensions makes the dot product's variance grow with \(d_k\). Larger raw scores make Softmax increasingly concentrated.

## The saturation problem

Softmax turns scores into probabilities:

$$
\operatorname{softmax}(z)_i = \frac{e^{z_i}}{\sum_j e^{z_j}}.
$$

When one score dominates, its probability approaches one and the others approach zero. The derivative \(p_i(1-p_i)\) is then small, so gradient signals through the choice become weak. This is not a statement that large scores are always wrong; it is a reason to control their scale during learning.

Scaled dot-product attention divides its score by \(\sqrt{d_k}\):

$$
\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}+M\right)V.
$$

The scaling keeps typical logits in a range where Softmax can discriminate without immediately saturating. The mask \(M\) separately determines which relationships are allowed. Scaling stabilizes numerical and optimization behavior; it does not decide semantic relevance.

## Where the Scale Comes From

For one query–key pair,

$$
z=\sum_{i=1}^{d_k}q_i k_i.
$$

Under the common initialization-level approximation that components are independent, zero-mean, and unit-variance, each product has variance near one and the sum has variance near \(d_k\). Its typical magnitude therefore grows on the order of \(\sqrt{d_k}\). Dividing by \(\sqrt{d_k}\) keeps the typical score scale roughly comparable as the key dimension changes. This is a statistical motivation under stated assumptions, not a proof that every trained query and key distribution behaves that way.

## Why Saturation Weakens Learning

Softmax has Jacobian entries

$$
\frac{\partial p_i}{\partial z_j}=p_i(\delta_{ij}-p_j).
$$

When one probability is close to one and the rest are close to zero, these terms are small. Small changes to the score no longer change the attention weights much, so gradients through that choice become weak. This differs from gradient explosion: the local Softmax derivative is becoming small because the distribution is saturated, rather than a long chain of derivatives growing without bound.

For example, Softmax of \([1,0]\) is about \([0.73,0.27]\), leaving both alternatives responsive; Softmax of \([10,0]\) is about \([0.99995,0.00005]\), making its local derivatives nearly zero. Attention needs neither uniformly flat weights nor premature one-hot selection. Scaling controls a typical numerical range so training can learn which distinctions deserve sharper weights.

## Why Key Dimension Is Used

Queries and keys meet in a dot product whose shared dimension is \(d_k\), so \(\sqrt{d_k}\) matches the source of this accumulation. Dividing by the number of heads, hidden dimension, or an arbitrary constant does not directly normalize that variance. Alternative attention parameterizations can use different normalization choices; the standard scaled dot-product form is a design that aligns the denominator with the dot product's dimensional scale.

## Summary

Dot products accumulate across key dimensions. Without scale control, larger typical logits can push Softmax into saturated distributions and weaken its local gradients. The \(1/\sqrt{d_k}\) factor stabilizes that typical scale; masking controls visibility, and learned Q/K/V projections determine relevance.
