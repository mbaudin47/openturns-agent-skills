---
name: openturns-sensitivity-analysis
description: Perform global sensitivity analysis in OpenTURNS using Sobol' indices (Saltelli, Martinez, Jansen, Mauntz-Kucherenko), bootstrap confidence intervals, and PCE-based Sobol indices. Use when estimating first-order, second-order, or total Sobol' indices, generating Sobol designs of experiments, or plotting sensitivity bar charts.
---

# Global Sensitivity Analysis with OpenTURNS

Guidelines, essential classes, and idioms for conducting Global Sensitivity Analysis (GSA) and estimating Sobol' sensitivity indices using OpenTURNS.

## When to Use

- Estimating first-order ($S_1$), second-order ($S_2$), and total-order ($S_T$) Sobol' indices.
- Generating dedicated Sobol' designs of experiments via `SobolIndicesExperiment`.
- Comparing sampling-based estimators (`SaltelliSensitivityAlgorithm`, `MartinezSensitivityAlgorithm`, `JansenSensitivityAlgorithm`, `MauntzKucherenkoSensitivityAlgorithm`).
- Quantifying estimator uncertainty with bootstrap confidence intervals.
- Computing exact analytical Sobol' indices from a Polynomial Chaos Expansion metamodel via `FunctionalChaosSobolIndices`.
- Visualizing sensitivity indices with native OpenTURNS bar plots (`draw()`).

---

## 1. Sampling-Based Sobol' Indices Workflow

### A. Principle and Cost
For an input vector with independent marginals and a scalar model $Y = g(\boldsymbol{X})$:
- **First order index:** $S_i = \operatorname{Var}(\mathbb{E}[Y \mid X_i]) / \operatorname{Var}(Y)$
- **Total order index:** $S_{Ti} = 1 - \operatorname{Var}(\mathbb{E}[Y \mid \boldsymbol{X}_{\sim i}]) / \operatorname{Var}(Y)$

The design of experiments requires specific paired evaluations:
- Without 2nd order indices: sample size is $N \times (d + 2)$.
- With 2nd order indices: sample size is $N \times (2d + 2)$.

### B. Standard Implementation

```python
import openturns as ot
from openturns.usecases import ishigami_function

# 1. Load or define model and input distribution
im = ishigami_function.IshigamiModel()
distribution = im.distribution
model = im.model

# 2. Build Sobol' design of experiments
size = 1000
computeSecondOrder = True
experiment = ot.SobolIndicesExperiment(distribution, size, computeSecondOrder)
inputDesign = experiment.generate()
outputDesign = model(inputDesign)

# 3. Estimate indices (Saltelli or Martinez)
sensitivityAnalysis = ot.SaltelliSensitivityAlgorithm(inputDesign, outputDesign, size)

# 4. Bootstrap confidence intervals (e.g. 95% level, 500 resamples)
sensitivityAnalysis.setBootstrapSize(500)
sensitivityAnalysis.setConfidenceLevel(0.95)

# 5. Extract results
first_order = sensitivityAnalysis.getFirstOrderIndices()
total_order = sensitivityAnalysis.getTotalOrderIndices()
first_order_ci = sensitivityAnalysis.getFirstOrderIndicesInterval()
total_order_ci = sensitivityAnalysis.getTotalOrderIndicesInterval()

if computeSecondOrder:
    second_order = sensitivityAnalysis.getSecondOrderIndices()

# 6. Plot native OpenTURNS graph
graph = sensitivityAnalysis.draw()
```

---

## 2. Choosing the Right Estimator

OpenTURNS provides several sampling-based algorithms with the same constructor `(inputDesign, outputDesign, size)`:

| Class | Properties & Recommended Use |
| :--- | :--- |
| `ot.SaltelliSensitivityAlgorithm` | Standard Saltelli formulation. Robust default choice. |
| `ot.MartinezSensitivityAlgorithm` | Based on correlation coefficients. Guarantees indices remain in $[-1, 1]$. Highly recommended when indices are close to zero. |
| `ot.JansenSensitivityAlgorithm` | Jansen estimator. Effective for total-order indices. |
| `ot.MauntzKucherenkoSensitivityAlgorithm` | Well-suited when total variance is difficult to estimate. |

---

## 3. Analytical Sobol' Indices via PCE

When a Polynomial Chaos Expansion (PCE) has been constructed, Sobol' indices can be derived analytically from the expansion coefficients at zero additional simulation cost:

```python
import openturns as ot

# Assuming pceResult is an ot.FunctionalChaosResult
pceSobol = ot.FunctionalChaosSobolIndices(pceResult)

dim = distribution.getDimension()
for i in range(dim):
    s1 = pceSobol.getSobolIndex(i)
    st = pceSobol.getSobolTotalIndex(i)
    print(f"X{i+1}: S1 = {s1:.4f}, ST = {st:.4f}")

# Second order interaction between X_i and X_j
s12 = pceSobol.getSobolIndex([0, 1])
```

---

## 4. Best Practices & Pitfalls

1. **Independent Marginals:** Standard Sobol' index decomposition requires independent input variables. If inputs are dependent, consider HSIC indices (`ot.HSICEstimatorGlobalSensitivity`).
2. **Reusing Evaluations:** Always generate inputs using `ot.SobolIndicesExperiment` and evaluate the model once on `inputDesign`. Do not generate separate samples for first and total order.
3. **Negative Indices:** Due to sample variance, sampling estimators may yield slightly negative values for non-influential variables. Use `ot.MartinezSensitivityAlgorithm` or bootstrap confidence intervals to check if zero is inside the interval.
4. **Graph Rendering:** `sensitivityAnalysis.draw()` returns an `ot.Graph`. Display it with `openturns.viewer.View(graph)` or export it to file with `graph.draw("sobol.png")`.
