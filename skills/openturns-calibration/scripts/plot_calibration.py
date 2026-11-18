#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model calibration and parameter estimation with OpenTURNS.

This script demonstrates:
1. Setting up a parametric physical model via ParametricFunction.
2. Generating synthetic experimental observations with measurement noise.
3. Estimating parameters using NonLinearLeastSquaresCalibration.
4. Performing Gaussian Bayesian calibration with GaussianNonLinearCalibration.
5. Sampling the posterior parameter distribution using RandomWalkMetropolisHastings (MCMC).
6. Generating diagnostic plots (observations vs predictions, residuals).
"""

# %%
import math
import openturns as ot


# %%
def build_calibration_problem():
    """
    Build physical model and synthetic noisy observations.

    Model: y = a * x / (b + x) (Michaelis-Menten kinetics)
    Ground truth: a = 2.5, b = 1.2
    """
    # Full function: [x, a, b] -> y
    def michaelis_menten(X):
        x, a, b = X[0], X[1], X[2]
        return [a * x / (b + x)]

    full_fn = ot.PythonFunction(3, 1, michaelis_menten)
    full_fn.setInputDescription(["x", "a", "b"])
    full_fn.setOutputDescription(["y"])

    # True parameters and reference model
    true_theta = [2.5, 1.2]
    parametric_model = ot.ParametricFunction(full_fn, [1, 2], true_theta)

    # Generate synthetic observations with noise sigma = 0.05
    ot.RandomGenerator.SetSeed(42)
    n_obs = 15
    x_obs = ot.Sample([[0.2 + i * 0.4] for i in range(n_obs)])

    exact_y = parametric_model(x_obs)
    noise_dist = ot.Normal(0.0, 0.05)
    noise = noise_dist.getSample(n_obs)
    y_obs = exact_y + noise

    return parametric_model, x_obs, y_obs, true_theta


# %%
def run_least_squares_calibration(model, x_obs, y_obs):
    """
    Perform non-linear least squares calibration.
    """
    initial_guess = ot.Point([1.5, 0.8])
    calib = ot.NonLinearLeastSquaresCalibration(
        model, x_obs, y_obs, initial_guess
    )
    calib.run()
    result = calib.getResult()

    theta_map = result.getParameterMAP()
    graph_pred = result.drawObservationsVsPredictions()
    graph_res = result.drawResiduals()

    return theta_map, result, graph_pred, graph_res


# %%
def run_gaussian_calibration(model, x_obs, y_obs):
    """
    Perform Gaussian calibration with prior distribution on parameters.
    """
    prior_mean = ot.Point([2.0, 1.0])
    cov_prior = ot.CovarianceMatrix(2)
    cov_prior[0, 0] = 1.0  # Var(a)
    cov_prior[1, 1] = 1.0  # Var(b)

    cov_error = ot.CovarianceMatrix(1)
    cov_error[0, 0] = 0.05**2  # measurement error variance

    calib = ot.GaussianNonLinearCalibration(
        model, x_obs, y_obs, prior_mean, cov_prior, cov_error
    )
    calib.run()
    result = calib.getResult()

    theta_map = result.getParameterMAP()
    posterior = result.getParameterPosterior()
    return theta_map, posterior


# %%
def run_bayesian_mcmc_calibration(x_obs, y_obs):
    """
    Perform full Bayesian MCMC calibration with RandomWalkMetropolisHastings.
    """
    prior = ot.JointDistribution(
        [ot.Uniform(1.0, 4.0), ot.Uniform(0.2, 3.0)]
    )
    initial_state = [2.0, 1.0]
    proposal = ot.Normal([0.0, 0.0], [0.03, 0.03], ot.IdentityMatrix(2))

    sampler = ot.RandomWalkMetropolisHastings(prior, initial_state, proposal)

    # Link function: [a, b, x] -> [mu, sigma] with frozen x
    def link_py(X):
        a, b, x = X[0], X[1], X[2]
        mu = a * x / (b + x)
        sigma = 0.05
        return [mu, sigma]

    full_link = ot.PythonFunction(3, 2, link_py)
    link_fn = ot.ParametricFunction(full_link, [2], [1.0])

    conditional = ot.Normal()
    sampler.setLikelihood(conditional, y_obs, link_fn, x_obs)

    sample = sampler.getSample(2500)
    # Burn-in: remove first 500 samples
    chain = sample[500:]
    theta_mean = chain.computeMean()
    return theta_mean, chain


# %%
def main():
    print("=== Model Calibration and Inverse Problems with OpenTURNS ===")

    model, x_obs, y_obs, true_theta = build_calibration_problem()
    print(f"Ground truth parameters: a = {true_theta[0]}, b = {true_theta[1]}")
    print(f"Number of observations: {x_obs.getSize()}")

    # 1. Non-linear least squares
    print("\n1. Running Non-Linear Least Squares Calibration...")
    theta_ls, res_ls, graph_pred, _ = run_least_squares_calibration(
        model, x_obs, y_obs
    )
    print(f"Estimated theta (LS): a = {theta_ls[0]:.4f}, b = {theta_ls[1]:.4f}")

    # 2. Gaussian non-linear calibration
    print("\n2. Running Gaussian Non-Linear Calibration...")
    theta_gauss, post_gauss = run_gaussian_calibration(model, x_obs, y_obs)
    print(
        f"Estimated theta (MAP): a = {theta_gauss[0]:.4f}, b = {theta_gauss[1]:.4f}"
    )

    # 3. Bayesian MCMC calibration
    print("\n3. Running Bayesian MCMC Calibration (RandomWalkMetropolisHastings)...")
    theta_mcmc, chain = run_bayesian_mcmc_calibration(x_obs, y_obs)
    print(
        f"Estimated theta (MCMC mean): a = {theta_mcmc[0]:.4f}, b = {theta_mcmc[1]:.4f}"
    )

    # Assertions: estimated parameters should be close to true values (2.5, 1.2)
    assert abs(theta_ls[0] - true_theta[0]) < 0.20, "Parameter 'a' estimate out of tolerance"
    assert abs(theta_ls[1] - true_theta[1]) < 0.20, "Parameter 'b' estimate out of tolerance"
    assert abs(theta_gauss[0] - true_theta[0]) < 0.20, "MAP 'a' estimate out of tolerance"
    assert abs(theta_gauss[1] - true_theta[1]) < 0.20, "MAP 'b' estimate out of tolerance"
    assert abs(theta_mcmc[0] - true_theta[0]) < 0.25, "MCMC 'a' estimate out of tolerance"
    assert abs(theta_mcmc[1] - true_theta[1]) < 0.25, "MCMC 'b' estimate out of tolerance"

    print("\nCalibration script executed successfully.")


if __name__ == "__main__":
    main()
