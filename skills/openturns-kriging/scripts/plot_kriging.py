#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kriging / Gaussian Process Regression surrogate modeling with OpenTURNS.

Target Version: OpenTURNS 1.27

This script demonstrates:
1. Training data generation from a non-linear physical model.
2. Building trend basis and spatial covariance model (Matérn kernel).
3. Fitting Gaussian process hyperparameters via GaussianProcessFitter.
4. Performing regression and evaluating surrogate predictions via GaussianProcessRegression.
5. Evaluating prediction uncertainty and conditional variance with KrigingResult.
6. Validating surrogate accuracy with MetaModelValidation (R2 score).
"""

# %%
import math
import openturns as ot


# %%
def build_training_data(n_train=20, n_test=100):
    """
    Generate synthetic train and test datasets from x * sin(x).

    Parameters
    ----------
    n_train : int, optional
        Number of training points (default is 20).
    n_test : int, optional
        Number of validation points (default is 100).

    Returns
    -------
    tuple of ot.Sample
        x_train, y_train, x_test, y_test
    """
    model = ot.SymbolicFunction(["x"], ["x * sin(x)"])
    distribution = ot.Uniform(0.0, 10.0)

    # Latin Hypercube Sampling for training
    lhs = ot.LHSExperiment(distribution, n_train)
    x_train = lhs.generate()
    x_train.sort()
    y_train = model(x_train)

    # Regular grid for validation
    step = 10.0 / (n_test - 1)
    x_test = ot.Sample([[i * step] for i in range(n_test)])
    y_test = model(x_test)

    return x_train, y_train, x_test, y_test, model


# %%
def fit_kriging_model(x_train, y_train):
    """
    Fit Kriging model using standard KrigingAlgorithm.

    Parameters
    ----------
    x_train : ot.Sample
        Input training points.
    y_train : ot.Sample
        Output training points.

    Returns
    -------
    ot.KrigingResult
        The fitted Kriging result object.
    """
    dim = x_train.getDimension()
    basis = ot.LinearBasisFactory(dim).build()
    covariance_model = ot.MaternModel([1.5] * dim, [1.0], 2.5)

    algo = ot.KrigingAlgorithm(x_train, y_train, covariance_model, basis)
    algo.run()
    return algo.getResult()


# %%
def fit_modern_gpr(x_train, y_train):
    """
    Fit Gaussian Process using OpenTURNS 1.27+ GaussianProcessFitter/Regression.

    Parameters
    ----------
    x_train : ot.Sample
        Input training points.
    y_train : ot.Sample
        Output training points.

    Returns
    -------
    ot.Function
        The fitted metamodel.
    """
    dim = x_train.getDimension()
    basis = ot.LinearBasisFactory(dim).build()
    cov_model = ot.MaternModel([1.5] * dim, [1.0], 2.5)

    fitter = ot.GaussianProcessFitter(x_train, y_train, cov_model, basis)
    fitter.run()

    gpr = ot.GaussianProcessRegression(fitter.getResult())
    gpr.run()
    return gpr.getResult().getMetaModel()


# %%
def main():
    print("=== Kriging / Gaussian Process Regression with OpenTURNS ===")

    # 1. Data generation
    x_train, y_train, x_test, y_test, _ = build_training_data(
        n_train=25, n_test=100
    )
    print(f"Generated {x_train.getSize()} training points.")

    # 2. Modern GPR workflow
    print("\nFitting modern GaussianProcessFitter + GaussianProcessRegression...")
    gpr_metamodel = fit_modern_gpr(x_train, y_train)
    y_pred_gpr = gpr_metamodel(x_test)

    val_gpr = ot.MetaModelValidation(y_test, y_pred_gpr)
    r2_gpr = val_gpr.computeR2Score()[0]
    print(f"Modern GPR R2 score on test set: {r2_gpr:.4f}")

    # 3. Standard Kriging workflow with conditional variance
    print("\nFitting standard KrigingAlgorithm for uncertainty quantification...")
    kriging_res = fit_kriging_model(x_train, y_train)
    metamodel = kriging_res.getMetaModel()
    y_pred = metamodel(x_test)

    val = ot.MetaModelValidation(y_test, y_pred)
    r2 = val.computeR2Score()[0]
    print(f"Kriging R2 score on test set: {r2:.4f}")

    # 4. Conditional variance & 95% confidence intervals
    cond_var = kriging_res.getConditionalMarginalVariance(x_test)
    z_alpha = 1.96  # 95% confidence level
    coverage_count = 0
    for i in range(x_test.getSize()):
        sigma = math.sqrt(max(0.0, cond_var[i, 0]))
        lower = y_pred[i, 0] - z_alpha * sigma
        upper = y_pred[i, 0] + z_alpha * sigma
        actual = y_test[i, 0]
        if lower <= actual <= upper:
            coverage_count += 1

    coverage_rate = coverage_count / x_test.getSize()
    print(f"95% Confidence Interval Coverage: {coverage_rate * 100:.1f}%")

    # Assertions
    assert r2 > 0.90, f"R2 score should be > 0.90, got {r2}"
    assert coverage_rate >= 0.90, f"Coverage should be >= 90%, got {coverage_rate}"

    print("\nKriging script executed successfully.")


if __name__ == "__main__":
    main()
