---
name: openturns-functional-chaos
description: OpenTURNS FunctionalChaosAlgorithm class documentation, constructors, methods, and usage examples for Polynomial Chaos Expansion (PCE).
---

# FunctionalChaosAlgorithm

`FunctionalChaosAlgorithm` is the main OpenTURNS class used to construct Polynomial Chaos Expansions (PCE) from input and output samples of a model or physical system.

---

## Overview & Mathematical Context

A Functional Chaos Expansion represents a random response vector $Y = g(X) \in \mathbb{R}^{n_Y}$ in terms of multivariate orthonormal polynomials $\{\Psi_k\}$ evaluated on standard distributions corresponding to input random vector $X \in \mathbb{R}^{n_X}$:

$$Y \approx \sum_{k \in K} a_k \Psi_k(X)$$

`FunctionalChaosAlgorithm` manages:
1. **Input distribution estimation / definition** ($X$)
2. **Adaptive multivariate basis selection** ($\{\Psi_k\}$)
3. **Projection strategy selection** (estimation of coefficients $a_k$ via Least Squares, LARS, or Numerical Integration)

---

## Available Constructors

```python
import openturns as ot

# 1. Basic constructor (distribution estimated via BuildDistribution)
algo = ot.FunctionalChaosAlgorithm(inputSample, outputSample)

# 2. Specifying input distribution
algo = ot.FunctionalChaosAlgorithm(inputSample, outputSample, distribution)

# 3. Specifying adaptive truncation strategy
algo = ot.FunctionalChaosAlgorithm(
    inputSample, outputSample, distribution, adaptiveStrategy
)

# 4. Full configuration with projection strategy
algo = ot.FunctionalChaosAlgorithm(
    inputSample, outputSample, distribution, adaptiveStrategy, projectionStrategy
)

# 5. Weighted samples
algo = ot.FunctionalChaosAlgorithm(
    inputSample, weights, outputSample, distribution, adaptiveStrategy
)
algo = ot.FunctionalChaosAlgorithm(
    inputSample,
    weights,
    outputSample,
    distribution,
    adaptiveStrategy,
    projectionStrategy,
)
```

### Parameters Summary
- **`inputSample`**: 2D sample of input variables (`Sample` or 2D sequence of floats).
- **`outputSample`**: 2D sample of output variables (`Sample` or 2D sequence of floats).
- **`distribution`**: Joint probability distribution of inputs (`Distribution`). If omitted, estimated via `FunctionalChaosAlgorithm.BuildDistribution(inputSample)`.
- **`adaptiveStrategy`**: Strategy to select and truncate the basis terms (`AdaptiveStrategy`, e.g., `FixedStrategy`).
- **`projectionStrategy`**: Strategy to evaluate coefficients ($a_k$) (`ProjectionStrategy`, e.g., `LeastSquaresStrategy`, `IntegrationStrategy`).
- **`weights`**: Sequence of weights associated with sample points (default: $w_i = 1/N$).

---

## Key Methods

| Method | Description |
| :--- | :--- |
| `run()` | Executes the metamodel computation. |
| `getResult()` | Returns the `FunctionalChaosResult` object containing the metamodel and basis details. |
| `getDistribution()` / `setDistribution(dist)` | Accessor for input joint distribution. |
| `getAdaptiveStrategy()` | Accessor for adaptive selection strategy. |
| `getProjectionStrategy()` / `setProjectionStrategy(strat)` | Accessor/mutator for projection strategy. |
| `getUseDomination()` / `setUseDomination(bool)` | Accessor/mutator for domination flag (bypasses isoprobabilistic transformation). |
| `getWeights()` | Returns weights associated with sample points. |
| `BuildDistribution(inputSample)` | Static method that infers marginal distributions and copula from a sample. |

---

## Code Examples

### 1. Default / Minimal Setup (Least Squares)
```python
import openturns as ot

# Generate training data
distribution = ot.JointDistribution([ot.Uniform(-1.0, 1.0)] * 2)
inputTrain = distribution.getSample(100)
model = ot.SymbolicFunction(["x1", "x2"], ["x1^2 + sin(x2)"])
outputTrain = model(inputTrain)

# Create algorithm with default strategies
algo = ot.FunctionalChaosAlgorithm(inputTrain, outputTrain, distribution)
algo.run()

# Extract metamodel
result = algo.getResult()
metamodel = result.getMetaModel()
```

### 2. Custom Basis and Sparse PCE via LARS
```python
import openturns as ot

# Define model inputs
dist = ot.JointDistribution(
    [ot.Uniform(-math.pi, math.pi), ot.Uniform(-math.pi, math.pi)]
)
inputTrain = dist.getSample(100)
outputTrain = model(inputTrain)

# Define multivariate orthonormal basis
multivariateBasis = ot.OrthogonalProductPolynomialFactory(
    [ot.StandardDistributionPolynomialFactory(dist.getMarginal(i)) for i in range(2)]
)

# Set degree truncation
totalDegree = 6
enumFunc = multivariateBasis.getEnumerateFunction()
basisSize = enumFunc.getBasisSizeFromTotalDegree(totalDegree)
adaptiveStrategy = ot.FixedStrategy(multivariateBasis, basisSize)

# Set sparse selection strategy (LARS)
selectionAlgo = ot.LeastSquaresMetaModelSelectionFactory(
    ot.LARS(), ot.CorrectedLeaveOneOut()
)
projectionStrategy = ot.LeastSquaresStrategy(selectionAlgo)

# Construct and run algorithm
algo = ot.FunctionalChaosAlgorithm(
    inputTrain, outputTrain, dist, adaptiveStrategy, projectionStrategy
)
algo.run()
result = algo.getResult()
```

### 3. Integration Strategy with Gauss Product Experiment
```python
import openturns as ot

# Create experiment & design points
marginalSizes = [4, 4]
experiment = ot.GaussProductExperiment(distribution, marginalSizes)
X, W = experiment.generateWithWeights()
Y = model(X)

# Define basis & strategy
multivariateBasis = ot.OrthogonalProductPolynomialFactory(
    [ot.StandardDistributionPolynomialFactory(distribution.getMarginal(i)) for i in range(2)]
)
adaptiveStrategy = ot.FixedStrategy(
    multivariateBasis, multivariateBasis.getEnumerateFunction().getBasisSizeFromTotalDegree(3)
)
projectionStrategy = ot.IntegrationStrategy()

# Run integration PCE
algo = ot.FunctionalChaosAlgorithm(
    X, W, Y, distribution, adaptiveStrategy, projectionStrategy
)
algo.run()
result = algo.getResult()
```

---

## Post-Processing Results

Once `algo.run()` is complete:

```python
result = algo.getResult()

# 1. Obtain metamodel function
metamodel = result.getMetaModel()

# 2. Extract mean & covariance via FunctionalChaosRandomVector
randomVector = ot.FunctionalChaosRandomVector(result)
mean = randomVector.getMean()
covariance = randomVector.getCovariance()

# 3. Compute Sobol' sensitivity indices
sobolIndices = ot.FunctionalChaosSobolIndices(result)
fo_s1 = sobolIndices.getSobolIndex(0)
to_s1 = sobolIndices.getSobolTotalIndex(0)
```

---

## Default ResourceMap Key Configurations

- **`FunctionalChaosAlgorithm-QNorm`**: `1.0` uses `LinearEnumerateFunction`; otherwise uses `HyperbolicAnisotropicEnumerateFunction`.
- **`FunctionalChaosAlgorithm-Sparse`**: If `True`, enables sparse selection (LARS).
- **`FunctionalChaosAlgorithm-FittingAlgorithm`**: `'CorrectedLeaveOneOut'` or `'KFold'`.
- **`MetaModelAlgorithm-PValueThreshold`**: Default Kolmogorov p-value threshold (`0.05`) for `BuildDistribution`.
- **`MetaModelAlgorithm-ModelSelectionCriterion`**: Model criterion for parametric fitting (`BIC`, `AIC`, `AICC`).
