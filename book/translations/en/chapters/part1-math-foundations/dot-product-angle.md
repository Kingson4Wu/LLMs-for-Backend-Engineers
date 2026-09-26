# Dot Products and Cosine Similarity: How Vectors Express Relationships

Word-vector similarity often involves cosine similarity. But **why does a dot product tell us about the angle between two vectors? What mathematics connects the two?**

Let us begin with a picture and build the explanation step by step.

## 1. Start with Projection: The Geometric Intuition

### What a Projection Means

Consider this diagram:

```
      a
     /|
    / |
   /  |
  /   |
 /_)θ |
O─────┴──────────→ b
  |a|cos(θ)
```

**The signed length of a projected onto the direction of b is |a|cos(θ).**

What does this tell us?

### Why Does Projection Reflect Similarity?

Imagine vectors representing directions of travel.

**Case 1: Exactly the same direction, θ=0°**
```
You →→→→→
    →→→→→
```
All of your movement projects onto the other direction.
cos(0°) = 1, giving the maximum projection.

**Case 2: Perpendicular directions, θ=90°**
```
You ↑↑↑
    →→→
```
Your movement has zero projection onto the other direction.
cos(90°) = 0: there is no shared component.

**Case 3: Opposite directions, θ=180°**
```
You ←←←←←
    →→→→→
```
Your projection onto the other direction is negative.
cos(180°) = -1: the directions are exactly opposite.

**The key insight**:
- **Smaller angle** → larger cos(θ) → **larger projection** → closer alignment.
- **Angle of 90°** → cos(90°) = 0 → **zero projection** → orthogonal directions.
- **Angle of 180°** → cos(180°) = -1 → **negative projection** → opposite directions.

**This is the fundamental reason cosine measures directional similarity.** In a word-embedding or other representation space, orthogonality only says that the two vectors have no projection under the current metric; it does not prove that the corresponding concepts have no linguistic or real-world relationship.

### Properties of Cosine

Over [0°, 180°]:

```
θ = 0°   → cos(0°) = 1      (same direction)
θ = 45°  → cos(45°) ≈ 0.707
θ = 90°  → cos(90°) = 0     (perpendicular)
θ = 135° → cos(135°) ≈ -0.707
θ = 180° → cos(180°) = -1   (opposite directions)
```

Cosine decreases monotonically as the angle increases over this interval.

A sketch:
```
  cos(θ)
    1 | ●
      |  \
    0 |___\__________ θ
      |    \
   -1 |     ●
      0°  90°  180°
```

Smaller angle → larger cosine → larger dot product, when vector lengths are fixed.

## 2. The Definition and Geometry of the Dot Product

### The Algebraic Definition

The **algebraic definition** is simple:

**a · b = a₁b₁ + a₂b₂ + ... + aₙbₙ**

Multiply corresponding coordinates and add them. Every term contains information about b’s components.

### The Geometric Interpretation

The dot product also has a geometric interpretation:

**a · b = |b| × (|a|cos(θ))**
= length of b × projection of a onto b’s direction

Equivalently:

**a · b = |a| × (|b|cos(θ))**
= length of a × projection of b onto a’s direction

### Why Multiply the Projection by b’s Length?

**For example**:
```
a = [3, 4]
b = [2, 0]  (along the x-axis, length 2)

Dot product = 3×2 + 4×0 = 6
```

Where does 6 come from?
- a’s x-component is 3.
- b’s x-component is 2, incorporating b’s length.
- Their product is 3 × 2 = 6.

**What if b is a unit vector?**
```
b' = [1, 0]  (length 1)

Dot product = 3×1 + 4×0 = 3
```

Now the dot product equals **a’s projection**.

**The underlying reason: products of coordinates**

Each term is **aᵢbᵢ**, not **aᵢ × 1**.

```
a = [a₁, a₂]
b = [b₁, b₂]

Dot product = a₁b₁ + a₂b₂
```

The coordinates b₁ and b₂ already encode b’s length.

Polar coordinates make this explicit:
```
b₁ = |b|cos(β)  ← Includes |b|
b₂ = |b|sin(β)  ← Includes |b|

Dot product = a₁(|b|cos(β)) + a₂(|b|sin(β))
            = |b|(a₁cos(β) + a₂sin(β))
              ↑
              This is where |b| comes from
```

**Therefore**:
- For a **unit vector** b, |b|=1, so the dot product equals a’s projection.
- Otherwise, the dot product equals a’s projection multiplied by |b|.

### What If We Want Only the Projection?

To obtain the signed projection of a onto b’s direction:

**Projection = (a · b) / |b|**

Alternatively, first normalize b:

**$\hat{b} = b / |b|$** (a unit vector)

**Projection = $a \cdot \hat{b} = (a \cdot b) / |b|$**

Cosine similarity extends this normalization by dividing by both vector lengths.

## 3. Why Do Coordinate Products Encode an Angle?

### Summing Products of Components

What is **a₁b₁ + a₂b₂** doing?

**Suppose**:
```
a = [3, 4]
b = [5, 0]  (along the x-axis)

Dot product = 3×5 + 4×0 = 15
```

What does this calculate?

Because b lies on the x-axis, only a’s x-component contributes:
- a’s x-component is 3.
- b’s length is 5.
- The result is 3×5 = 15.

**The idea**: each **aᵢbᵢ** multiplies the two vectors’ components along coordinate axis i. Adding them measures their overall alignment across all axes.

### Two More Examples

**Example 1**:
```
a = [1, 1]    // Direction 45°
b = [1, 0]    // Direction 0°
θ = 45°

Dot product = 1×1 + 1×0 = 1
|a| = √2
|b| = 1

Check: |a||b|cos(45°) = √2 × 1 × 0.707 ≈ 1 ✓
```

**Example 2**:
```
a = [0, 1]    // Direction 90°
b = [1, 0]    // Direction 0°
θ = 90°

Dot product = 0×1 + 1×0 = 0

Check: |a||b|cos(90°) = 1 × 1 × 0 = 0 ✓
```

## 4. Derivation: Dot Product = |a||b|cos(θ)

We can now prove that the algebraic and geometric expressions are equivalent.

### Method 1: Begin in Two Dimensions

**Step 1: Express the vectors in polar coordinates**

Take two two-dimensional vectors:
```
a = [a₁, a₂]
b = [b₁, b₂]
```

Their polar-coordinate representations are:
```
a = [|a|cos(α), |a|sin(α)]  // α: angle from the x-axis to a
b = [|b|cos(β), |b|sin(β)]  // β: angle from the x-axis to b
```

The angular difference is **θ = β - α**.

**Step 2: Compute the dot product**

```
a · b = a₁b₁ + a₂b₂
     = |a|cos(α) × |b|cos(β) + |a|sin(α) × |b|sin(β)
     = |a||b| [cos(α)cos(β) + sin(α)sin(β)]
```

**Step 3: Apply a trigonometric identity**

The key identity is:

**cos(α)cos(β) + sin(α)sin(β) = cos(β - α) = cos(θ)**

Therefore:

**a · b = |a||b|cos(θ)**

**Starting from the algebraic definition, this is a derived result.**

### Method 2: The Law of Cosines in Any Dimension

Consider the triangle formed by the origin O and the endpoints A and B:

```
      A (endpoint of a)
     / \
    /   \
   /     \
  / θ     \
 O─────────B (endpoint of b)
```

Its side lengths are:
- OA = |a|
- OB = |b|
- AB = |a - b|

**The law of cosines** gives:

**|a - b|² = |a|² + |b|² - 2|a||b|cos(θ)**

**Expand the left side**:

```
|a - b|² = (a - b)·(a - b)
         = a·a - 2a·b + b·b
         = |a|² - 2a·b + |b|²
```

**Equate the expressions**:

```
|a|² - 2a·b + |b|² = |a|² + |b|² - 2|a||b|cos(θ)

⇒ -2a·b = -2|a||b|cos(θ)

⇒ a·b = |a||b|cos(θ)
```

**This proof works in any dimension.**

### Three Dimensions and Beyond

**In three dimensions**, spherical coordinates and more elaborate trigonometric identities give the same result:

**a · b = |a||b|cos(θ)**

**In higher dimensions**, the law-of-cosines argument applies to **any n-dimensional vectors**:

**a · b = |a||b|cos(θ)**

Cosine similarity therefore works in any dimension.

## 5. Cosine Similarity: Remove Length, Keep Direction

### Deriving the Formula

We now know:

**a · b = |a| |b| cos(θ)**

Divide both sides by **|a||b|**, for nonzero vectors:

**cos(θ) = (a · b) / (|a| × |b|)**

This is **cosine similarity**.

### The Complete Derivation

```
1. Polar coordinates: a = |a|[cos(α), sin(α)]

2. Dot product: a·b = |a||b|[cos(α)cos(β) + sin(α)sin(β)]

3. Identity: cos(α)cos(β) + sin(α)sin(β) = cos(β-α) = cos(θ)

4. Therefore: a·b = |a||b|cos(θ)

5. Rearrange: cos(θ) = (a·b)/(|a||b|)
```

### Check with Concrete Numbers

**Example 1: An angle of 45°**
```
a = [1, 0]     // x-axis, α = 0°
b = [1, 1]     // Direction 45°, β = 45°
θ = 45°

Calculation:
|a| = √(1² + 0²) = 1
|b| = √(1² + 1²) = √2
a · b = 1×1 + 0×1 = 1

Cosine similarity = 1 / (1 × √2) = 1/√2 ≈ 0.707

Check: cos(45°) = √2/2 ≈ 0.707 ✓
```

**Example 2: Perpendicular vectors**
```
a = [1, 0]     // x-axis
b = [0, 1]     // y-axis
θ = 90°

Calculation:
|a| = 1
|b| = 1
a · b = 1×0 + 0×1 = 0

Cosine similarity = 0 / (1 × 1) = 0

Check: cos(90°) = 0 ✓
```

**Example 3: Same direction, different lengths**
```
a = [3, 4]     // Length 5
b = [6, 8]     // Length 10, same direction
θ = 0°

Calculation:
|a| = √(3² + 4²) = 5
|b| = √(6² + 8²) = 10
a · b = 3×6 + 4×8 = 18 + 32 = 50

Cosine similarity = 50 / (5 × 10) = 1

Check: cos(0°) = 1 ✓
```

### Why Use Cosine Similarity?

Cosine similarity divides each vector by its length and therefore compares direction only. It is appropriate when a task is meant to ignore length and compare direction.

**For example**:
```
"king"  = [0.2, 0.5, 0.8, ...]  Perhaps length 1.2
"queen" = [0.3, 0.6, 0.9, ...]  Perhaps length 1.5
```

If these vectors point in nearly the same direction, their cosine similarity is close to 1. That says that they have similar directions in this model and at this representation layer. It does not prove identical meaning, and vector length cannot in general be read as word frequency, semantic intensity, or importance. Whether length carries useful information depends on the architecture, training objective, and whether normalization has been applied.

Dot product and cosine similarity therefore answer different questions:
- **Raw dot product** is affected by both length and direction.
- **Cosine similarity** removes length and retains the directional relationship.

### The Bounded Range

**-1 ≤ cos(θ) ≤ 1**

- **cos(θ) = 1**: exactly the same direction, θ = 0°.
- **cos(θ) = 0**: perpendicular, θ = 90°; no projection in either direction.
- **cos(θ) = -1**: exactly opposite directions, θ = 180°.

## 6. Key Takeaways

### Why Does the Dot Product Reflect an Angle?

**1. The mathematics**

The sum of coordinate products and the product of lengths times cosine are mathematically equivalent. Trigonometric identities establish this equivalence rigorously.

**2. The intuition**

- **Projection**: one vector’s length times the other vector’s signed projection onto its direction.
- **Components**: the sum of shared alignment along coordinate axes.
- **Angle**: cosine decreases monotonically over the relevant interval, encoding directional difference.

**3. Why does a smaller angle give a larger dot product?**

Because:
- Dot product = |a||b|cos(θ).
- Cosine decreases monotonically on [0°,180°].
- Smaller θ → larger cos(θ) → larger dot product, with lengths held fixed.

This follows from the mathematical structure rather than an arbitrary design choice.

### What Cosine Similarity Gives Us

**cos(θ) = (a · b) / (|a| × |b|)**

- **Removes vector-length effects** by dividing by both lengths.
- **Retains directional information**, depending only on θ.
- **Uses the bounded range [-1, 1]**, making results easier to interpret.
- **Can compare representation directions**; whether it is suitable for a semantic task depends on the embedding model's training and usage contract.

Dot products naturally measure alignment because their mathematical structure contains angle information. Word-vector methods exploit this fact.

There is an important boundary here: only **cosine similarity** between nonzero vectors is necessarily in [-1, 1]. A dot product has no fixed range; it can keep growing as vector lengths grow.

## In LLMs: The Same Dot Product Has Different Jobs

Seeing a dot product in an LLM does not mean it is always computing “semantic similarity.” First ask where it sits in the computation.

### Attention: A Match Score for the Current Token

Scaled dot-product Attention in a Transformer can be written as:

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^\mathsf{T}}{\sqrt{d_k}}\right)V
$$

Each Query takes dot products with the Keys to form scores. Scaling, masking, and Softmax turn those scores into weights, which then combine the Values. This is scaled dot-product Attention, not cosine similarity, in the [original Transformer paper](https://arxiv.org/abs/1706.03762).

Q and K are produced by different learned projections of the current-layer representations. Their dot product is a match score for deciding where this layer and head should read information from in this context. Both direction and length can affect it. It should not be read directly as a fixed semantic distance between two tokens.

### Retrieval: Follow the Embedding Model's Metric

Vector retrieval commonly uses cosine similarity or dot product, but the chosen metric should follow the embedding model's training and serving contract. If both query and document vectors have been L2-normalized, their dot product equals cosine similarity; without normalization, the two can produce different rankings. Embedding tools often support both metrics and explicitly tie the choice to whether a model contains a normalization layer; see the [Sentence Transformers documentation](https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html).

Both situations calculate vector scores, but neither permits skipping over the training objective and context to call a high score “more similar in the real world.” A score gets its meaning from how the model learned it, which layer computes it, and how the system uses it next.

## Further Reading

- [From One-Hot to Embeddings](./from-onehot-to-embedding.md) — How embeddings learn representations from data.
- [Transformer Architecture Through Data Flow](../part2-llm-internal/transformer-architecture.md) — The full data flow through Query, Key, and Value.
