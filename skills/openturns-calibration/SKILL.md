---
name: openturns-calibration
description: Perform parameter calibration and inverse problems in OpenTURNS. Use when calibrating physical model parameters from experimental data using NonLinearLeastSquaresCalibration, GaussianNonLinearCalibration, or Bayesian calibration via RandomWalkMetropolisHastings.
---

# Model Calibration and Inverse Problems with OpenTURNS

Guidelines, essential classes, and idioms for calibrating parameters of computer models against experimental observations using OpenTURNS.

## When to Use

- Estimating unknown physical parameters $\boldsymbol{\theta}$ from experimental data $(x_k, y_k)_{k=1}^n$.
- Non-linear least-squares calibration via `ot.NonLinearLeastSquaresCalibration`.
- Maximum A Posteriori (MAP) and Gaussian calibration with prior distribution via `ot.GaussianNonLinearCalibration`.
- Full Bayesian calibration and posterior sampling via MCMC (`ot.RandomWalkMetropolisHastings`).
- Analyzing parameter uncertainties, posterior covariance, and residual diagnostics.

---

## 1. Problem Formulation and Parametric Function

Consider a physical model with input variables $\boldsymbol{x}$, unknown parameters $\boldsymbol{\theta}$, and measurement noise $\boldsymbol{\varepsilon}$:
$$\boldsymbol{y} = g(\boldsymbol{x}, \boldsymbol{\theta}) + \boldsymbol{\varepsilon}$$

For deterministic and Gaussian calibration (`NonLinearLeastSquaresCalibration`, `GaussianNonLinearCalibration`), OpenTURNS expects an `ot.ParametricFunction` where parameter indices within the full input vector are frozen with reference/initial values:

```python
import openturns as ot

# Full function: takes [x, theta1, theta2] -> dimension 3
def full_model_py(X):
    x, theta1, theta2 = X[0], X[1], X[2]
    return [theta1 * x / (theta2 + x)]

full_function = ot.PythonFunction(3, 1, full_model_py)

# Freeze theta indices (here indices [1, 2])
# Input dimension of parametric_model becomes dim(x) = 1
# Parameter dimension becomes dim(theta) = 2
theta_indices = [1, 2]
theta_reference = [1.0, 0.0]
parametric_model = ot.ParametricFunction(full_function, theta_indices, theta_reference)
```

---

## 2. Non-Linear Least Squares Calibration

When no informative prior is available, minimize the sum of squared residuals:

```python
import openturns as ot

# Experimental observations
x_obs = ot.Sample([[1.0], [2.0], [3.0], [4.0], [5.0]])
y_obs = ot.Sample([[3.5], [5.9], [8.6], [11.1], [13.4]])
theta_prior = ot.Point([1.0, 0.0])  # Initial guess

# Calibrate
algo = ot.NonLinearLeastSquaresCalibration(parametric_model, x_obs, y_obs, theta_prior)
algo.run()

result = algo.getResult()
theta_hat = result.getParameterMAP()
posterior_dist = result.getParameterPosterior()

print("Calibrated parameters:", theta_hat)
print("Posterior covariance:\n", posterior_dist.getCovariance())
```

---

## 3. Gaussian Non-Linear Calibration (Prior & Noise Covariance)

Incorporates Gaussian prior knowledge $\boldsymbol{\theta} \sim \mathcal{N}(\boldsymbol{\mu}_\theta, \boldsymbol{\Sigma}_\theta)$ and measurement error covariance $\boldsymbol{\Sigma}_\varepsilon$:

```python
# Prior mean and covariance on theta
theta_prior_mean = ot.Point([1.0, 0.0])
cov_theta = ot.CovarianceMatrix(2)
cov_theta[0, 0] = 4.0
cov_theta[1, 1] = 4.0

# Measurement noise covariance
cov_error = ot.CovarianceMatrix(1)
cov_error[0, 0] = 0.04  # sigma^2 = 0.2^2

algo_gaussian = ot.GaussianNonLinearCalibration(
    parametric_model, x_obs, y_obs, theta_prior_mean, cov_theta, cov_error
)
algo_gaussian.run()
result_gaussian = algo_gaussian.getResult()

theta_map = result_gaussian.getParameterMAP()
posterior = result_gaussian.getParameterPosterior()
```

---

## 4. Bayesian Calibration via MCMC (`RandomWalkMetropolisHastings`)

For full posterior sampling without Gaussian approximations, use MCMC:

```python
# 1. Define prior distribution on parameters theta
prior = ot.JointDistribution([ot.Uniform(1.0, 4.0), ot.Uniform(0.2, 3.0)])

# 2. Setup proposal distribution for random walk steps
proposal = ot.Normal([0.0, 0.0], [0.03, 0.03], ot.IdentityMatrix(2))

# 3. Create MCMC sampler
initial_state = [2.0, 1.0]
sampler = ot.RandomWalkMetropolisHastings(prior, initial_state, proposal)

# 4. Link function: takes theta as input and x as frozen parameter
# ot.Normal() has parameter dimension 2 [mu, sigma], so link function must output [mu, sigma]
def link_py(X):
    theta1, theta2, x = X[0], X[1], X[2]
    mu = theta1 * x / (theta2 + x)
    sigma = 0.05  # known observation standard deviation
    return [mu, sigma]

full_link = ot.PythonFunction(3, 2, link_py)
link_function = ot.ParametricFunction(full_link, [2], [1.0])  # freeze x (index 2)

# 5. Set likelihood and sample posterior
conditional = ot.Normal()
sampler.setLikelihood(conditional, y_obs, link_function, x_obs)
posterior_sample = sampler.getSample(2000)
theta_posterior_mean = posterior_sample[500:].computeMean()
```

---

## 5. Diagnostic Plots and Post-Processing

`ot.CalibrationResult` provides native diagnostic graphics:

```python
# Observations vs predictions
graph_obs_pred = result.drawObservationsVsPredictions()

# Residual distribution and normal plot
graph_residuals = result.drawResiduals()
graph_normal = result.drawResidualsNormalPlot()

# Parameter distributions (prior vs posterior)
graph_params = result.drawParameterDistributions()
```

---

## 6. Best Practices & Pitfalls

1. **Parameter Dimension vs Model Dimension:**
   - In `NonLinearLeastSquaresCalibration`: `parametric_model` inputs are $\boldsymbol{x}$; its parameters are $\boldsymbol{\theta}$.
   - In `RandomWalkMetropolisHastings.setLikelihood`: `link_function` inputs are $\boldsymbol{\theta}$; its parameters are $\boldsymbol{x}$ (covariates). Its output dimension must match `conditional.getParameterDimension()`.
2. **Initial Point:** For non-linear models, least-squares optimization may converge to local minima; test several starting points if residuals appear high.
3. **Identifiability:** If multiple parameters produce the same model output (collinear parameters), calibration becomes ill-conditioned. Inspect the posterior covariance matrix eigenvalues.
4. **Residual Analysis:** Always inspect `drawResidualsNormalPlot()` to verify that residuals follow zero-mean independent Gaussian distributions as hypothesized.
