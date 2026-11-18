---
name: openturns-reliability
description: Evaluate rare event failure probabilities and structural reliability in OpenTURNS. Use when defining failure events with ThresholdEvent, estimating failure probabilities via FORM, SORM, SubsetSampling, or Monte Carlo simulation, and computing Hasofer-Lind reliability indices and importance factors.
---

# Reliability Analysis and Rare Event Probability with OpenTURNS

Guidelines, essential classes, and idioms for structural reliability, rare event estimation, and design point search using OpenTURNS.

## When to Use

- Estimating the probability of a rare failure event $P_f = \mathbb{P}(g(\boldsymbol{X}) \le 0)$.
- Setting up limit state events via `ot.ThresholdEvent` and `ot.CompositeRandomVector`.
- Performing First Order Reliability Method (`ot.FORM`) and Second Order Reliability Method (`ot.SORM`).
- Finding the most probable failure point (design point $\boldsymbol{u}^*$) in the standard normal space and computing the Hasofer-Lind reliability index $\beta_{\text{HL}}$.
- Evaluating parameter importance factors $\alpha_i^2$ indicating which random inputs drive failure.
- Estimating very low failure probabilities ($P_f < 10^{-4}$) using advanced sampling algorithms (`ot.SubsetSampling`, `ot.DirectionalSampling`).
- Validating with crude Monte Carlo (`ot.ProbabilitySimulationAlgorithm`).

---

## 1. Problem Definition & Threshold Event

A reliability problem is defined by an input random vector $\boldsymbol{X} \sim f_{\boldsymbol{X}}$ and a limit state function $g(\boldsymbol{X})$ where the failure domain is $\mathcal{D}_f = \{\boldsymbol{x} \in \mathbb{R}^d : g(\boldsymbol{x}) \le 0\}$.

```python
import openturns as ot

# 1. Input distribution and RandomVector
input_distribution = ...  # ot.JointDistribution
input_vector = ot.RandomVector(input_distribution)

# 2. Limit state function g(x) <= threshold (failure when g(x) <= 0)
limit_state_function = ot.SymbolicFunction(
    ["E", "F", "L", "I"],
    ["0.30 - (F * L^3) / (3.0 * E * I)"]
)
output_vector = ot.CompositeRandomVector(limit_state_function, input_vector)

# 3. ThresholdEvent: failure operator ot.Less() or ot.Greater()
event = ot.ThresholdEvent(output_vector, ot.Less(), 0.0)
```

---

## 2. First and Second Order Reliability Methods (FORM / SORM)

FORM transforms $\boldsymbol{X}$ into standard normal space $\boldsymbol{U} = T(\boldsymbol{X}) \sim \mathcal{N}(\mathbf{0}, \boldsymbol{I}_d)$ and searches for the design point $\boldsymbol{u}^*$ closest to the origin.

### A. Important: Optimization Solver Starting Point
In modern OpenTURNS, the starting point must be configured directly on the optimization solver (e.g., `Cobyla` or `AbdoRackwitz`), not passed as a 3rd argument to `FORM`:

```python
# Create optimization solver and set starting point (usually the distribution mean)
solver = ot.Cobyla()
solver.setStartingPoint(input_distribution.getMean())

# Run FORM
form = ot.FORM(solver, event)
form.run()
form_result = form.getResult()

# Extract FORM metrics
pf_form = form_result.getEventProbability()
beta_hl = form_result.getHasoferReliabilityIndex()
u_star = form_result.getStandardSpaceDesignPoint()
x_star = form_result.getPhysicalSpaceDesignPoint()
importance_factors = form_result.getImportanceFactors()

# Plot importance factors pie chart
graph_importance = form_result.drawImportanceFactors()
```

### B. Second Order Reliability Method (SORM)
SORM accounts for the local curvature of the limit state surface at the design point:

```python
sorm = ot.SORM(solver, event)
sorm.run()
sorm_result = sorm.getResult()

pf_breitung = sorm_result.getEventProbabilityBreitung()
pf_tvedt = sorm_result.getEventProbabilityTvedt()
```

---

## 3. Advanced Sampling: Subset Sampling

For non-linear limit states or when $P_f \ll 10^{-4}$ where crude Monte Carlo is computationally prohibitive, `ot.SubsetSampling` generates intermediate conditional failure events using Markov Chain Monte Carlo:

```python
subset = ot.SubsetSampling(event)
subset.setMaximumOuterSampling(1000)  # Number of chains / iterations
subset.setBlockSize(100)             # Samples per conditional step
subset.run()

subset_result = subset.getResult()
pf_subset = subset_result.getProbabilityEstimate()
cov_subset = subset_result.getCoefficientOfVariation()
print(f"Subset Pf: {pf_subset:.4e} (CV = {cov_subset:.2%})")
```

---

## 4. Crude Monte Carlo Verification

For moderate probabilities ($P_f > 10^{-3}$), verify with standard simulation:

```python
algo_mc = ot.ProbabilitySimulationAlgorithm(event, ot.MonteCarloExperiment())
algo_mc.setMaximumOuterSampling(10000)
algo_mc.setBlockSize(100)
algo_mc.setMaximumCoefficientOfVariation(0.05)  # Stopping criterion
algo_mc.run()

result_mc = algo_mc.getResult()
pf_mc = result_mc.getProbabilityEstimate()
```

---

## 5. Best Practices & Pitfalls

1. **Solver Starting Point Deprecation:** Do not write `ot.FORM(solver, event, startingPoint)`. Always use `solver.setStartingPoint(...)` before instantiating `ot.FORM(solver, event)`.
2. **Accessors for Design Points:**
   - Standard space design point: `result.getStandardSpaceDesignPoint()`
   - Physical space design point: `result.getPhysicalSpaceDesignPoint()`
   - Reliability index: `result.getHasoferReliabilityIndex()`
3. **Multiple Local Minima:** If the limit state function has multiple local minima, local gradient algorithms (Cobyla, AbdoRackwitz) may miss the global design point. Consider multiple starting points or using `SubsetSampling`.
4. **Failure Operator:** Check whether failure is $g(X) \le 0$ (`ot.Less()`) or $g(X) \ge 0$ (`ot.Greater()`). An inversion flips the computed probability ($P_f$ vs $1 - P_f$).
