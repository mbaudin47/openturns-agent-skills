---
name: openturns-kriging
description: Construct, optimize, and evaluate Kriging / Gaussian Process Regression surrogate models in OpenTURNS. Use when fitting Gaussian processes, choosing covariance kernels (Matern, SquaredExponential), defining trends, computing conditional variances or confidence bounds, and validating metamodels.
---

# Kriging / Gaussian Process Regression with OpenTURNS

Guidelines, essential classes, and idioms for building, calibrating, and validating Gaussian Process Regression (Kriging) surrogate models in OpenTURNS.

## When to Use

- Constructing non-intrusive interpolation or regression metamodels from input/output training data.
- Selecting spatial covariance kernels (`ot.SquaredExponential`, `ot.MaternModel`, `ot.ExponentialModel`).
- Defining parametric trend functions using polynomial bases (`ot.ConstantBasisFactory`, `ot.LinearBasisFactory`, `ot.QuadraticBasisFactory`).
- Optimizing covariance scale and amplitude hyperparameters.
- Evaluating prediction uncertainty via conditional marginal variance or confidence intervals.
- Validating the metamodel using `ot.MetaModelValidation` and computing $R^2$ scores.

---

## 1. Key Components

A Kriging model decomposes the response $Y(x)$ as:
$$Y(x) = \sum_{j=1}^p \beta_j f_j(x) + Z(x)$$
where $\boldsymbol{f}(x)$ is a deterministic trend and $Z(x)$ is a zero-mean stationary Gaussian process with covariance function $C(s, t)$.

### A. Trend / Basis Selection
- **Constant trend (Ordinary Kriging):** `basis = ot.ConstantBasisFactory(dim).build()`
- **Linear trend (Universal Kriging):** `basis = ot.LinearBasisFactory(dim).build()`
- **Quadratic trend:** `basis = ot.QuadraticBasisFactory(dim).build()`

### B. Covariance Models
- **Squared Exponential (Gaussian kernel):**
  ```python
  scale = [1.0] * input_dim
  amplitude = [1.0]
  cov_model = ot.SquaredExponential(scale, amplitude)
  ```
- **Matérn kernel (recommended for physical models):**
  ```python
  # nu = 1.5 or 2.5
  cov_model = ot.MaternModel(scale, amplitude, 2.5)
  ```
- **Nugget effect (for noisy data or numerical stability):**
  ```python
  cov_model.setNuggetFactor(1e-6)
  ```

---

## 2. Standard Workflow (`KrigingAlgorithm`)

```python
import openturns as ot

# 1. Prepare data
x_train = ...  # ot.Sample (size N, dim d)
y_train = ...  # ot.Sample (size N, dim 1)

# 2. Define trend and covariance model
dim = x_train.getDimension()
basis = ot.LinearBasisFactory(dim).build()
covariance_model = ot.MaternModel([1.0] * dim, [1.0], 2.5)

# 3. Instantiate and run algorithm
algo = ot.KrigingAlgorithm(x_train, y_train, covariance_model, basis)
algo.run()

# 4. Extract results
result = algo.getResult()
metamodel = result.getMetaModel()
optimized_cov = result.getCovarianceModel()
print("Optimized scale:", optimized_cov.getScale())
print("Optimized amplitude:", optimized_cov.getAmplitude())

# 5. Predict and compute 95% confidence intervals
x_test = ...  # ot.Sample of query points
y_pred = metamodel(x_test)
cond_var = result.getConditionalMarginalVariance(x_test)

# 95% confidence bounds: y_pred +/- 1.96 * sqrt(cond_var)
y_lower = ot.Sample([[y_pred[i, 0] - 1.96 * (cond_var[i, 0] ** 0.5)] for i in range(x_test.getSize())])
y_upper = ot.Sample([[y_pred[i, 0] + 1.96 * (cond_var[i, 0] ** 0.5)] for i in range(x_test.getSize())])
```

---

## 3. OpenTURNS 1.27+ Architecture (`GaussianProcessFitter`)

OpenTURNS 1.27 introduced a decoupled architecture separating hyperparameter estimation (`GaussianProcessFitter`) from prediction and trajectory generation (`GaussianProcessRegression`):

```python
import openturns as ot

# Step 1: Fit covariance and trend hyperparameters
fitter = ot.GaussianProcessFitter(x_train, y_train, covariance_model, basis)
fitter.run()
fitter_result = fitter.getResult()

# Step 2: Build regression predictor
gpr = ot.GaussianProcessRegression(fitter_result)
gpr.run()
gpr_result = gpr.getResult()
metamodel = gpr_result.getMetaModel()
```

---

## 4. Metamodel Validation

Always validate surrogate predictions against test data:

```python
# Compute R2 score and draw prediction vs actual
val = ot.MetaModelValidation(y_test, metamodel(x_test))
r2_score = val.computeR2Score()[0]
graph = val.drawValidation()
```

---

## 5. Best Practices & Pitfalls

1. **Input Normalization:** If input variables have disparate scales (e.g. $10^{-6}$ vs $10^5$), scale inputs or provide appropriate initial `scale` parameters in the covariance model.
2. **Bounds on Hyperparameters:** Constrain scale search if optimization encounters local minima or singular covariance matrices:
   ```python
   # Optimize using bounded optimization algorithm
   solver = ot.NLopt("LN_COBYLA")
   algo.setOptimizationAlgorithm(solver)
   ```
3. **Data Dimensions:** `MetaModelValidation` takes `(y_test, y_pred)` in this order. Both must be 2D `ot.Sample` objects with the same dimension.
