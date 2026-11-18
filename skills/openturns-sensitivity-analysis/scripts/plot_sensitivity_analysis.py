#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensitivity analysis using OpenTURNS with the Ishigami test function.

This script demonstrates:
1. Design of experiments with SobolIndicesExperiment.
2. Estimation of first and total order Sobol' indices using Saltelli and Martinez algorithms.
3. Computation of bootstrap confidence intervals.
4. Computation of analytical Sobol' indices from a Polynomial Chaos Expansion (PCE).
5. Generation of native OpenTURNS sensitivity bar plots.
"""

# %%
import openturns as ot
from openturns.usecases import ishigami_function


# %%
def compute_sobol_sampling(size=1000, compute_second_order=True):
    """
    Compute Sobol' indices using sampling-based estimators.

    Parameters
    ----------
    size : int, optional
        Base sample size per block (default is 1000).
    compute_second_order : bool, optional
        Whether to compute second order indices (default is True).

    Returns
    -------
    dict
        Dictionary containing estimated indices, intervals, and graph.
    """
    im = ishigami_function.IshigamiModel()
    distribution = im.distribution
    model = im.model

    # Generate dedicated paired Sobol design
    experiment = ot.SobolIndicesExperiment(
        distribution, size, compute_second_order
    )
    input_design = experiment.generate()
    output_design = model(input_design)

    # Estimate with Saltelli algorithm
    saltelli = ot.SaltelliSensitivityAlgorithm(
        input_design, output_design, size
    )
    saltelli.setBootstrapSize(200)
    saltelli.setConfidenceLevel(0.95)

    first_order = saltelli.getFirstOrderIndices()
    total_order = saltelli.getTotalOrderIndices()
    fo_interval = saltelli.getFirstOrderIndicesInterval()
    to_interval = saltelli.getTotalOrderIndicesInterval()

    # Estimate with Martinez algorithm (bounded in [-1, 1])
    martinez = ot.MartinezSensitivityAlgorithm(
        input_design, output_design, size
    )
    martinez_fo = martinez.getFirstOrderIndices()
    martinez_to = martinez.getTotalOrderIndices()

    graph = saltelli.draw()

    results = {
        "first_order": first_order,
        "total_order": total_order,
        "first_order_interval": fo_interval,
        "total_order_interval": to_interval,
        "martinez_first_order": martinez_fo,
        "martinez_total_order": martinez_to,
        "graph": graph,
    }
    if compute_second_order:
        results["second_order"] = saltelli.getSecondOrderIndices()

    return results


# %%
def compute_sobol_pce(sample_size=400, total_degree=6):
    """
    Compute analytical Sobol' indices via Polynomial Chaos Expansion.

    Parameters
    ----------
    sample_size : int, optional
        Training sample size (default is 400).
    total_degree : int, optional
        Maximum polynomial degree (default is 6).

    Returns
    -------
    tuple of (ot.Point, ot.Point)
        First order and total order analytical Sobol' indices.
    """
    im = ishigami_function.IshigamiModel()
    x_train = im.distribution.getSample(sample_size)
    y_train = im.model(x_train)

    multivariate_basis = ot.OrthogonalProductPolynomialFactory(
        [im.X1, im.X2, im.X3]
    )
    enumerate_function = multivariate_basis.getEnumerateFunction()
    basis_size = enumerate_function.getBasisSizeFromTotalDegree(total_degree)
    adaptive_strategy = ot.FixedStrategy(multivariate_basis, basis_size)

    chaos_algo = ot.FunctionalChaosAlgorithm(
        x_train, y_train, im.distribution, adaptive_strategy
    )
    chaos_algo.run()
    chaos_result = chaos_algo.getResult()

    pce_sobol = ot.FunctionalChaosSobolIndices(chaos_result)
    dim = im.distribution.getDimension()

    first_order = ot.Point([pce_sobol.getSobolIndex(i) for i in range(dim)])
    total_order = ot.Point([pce_sobol.getSobolTotalIndex(i) for i in range(dim)])

    return first_order, total_order


# %%
def main():
    print("=== Global Sensitivity Analysis with OpenTURNS ===")

    # 1. Sampling-based estimation
    print("Running sampling-based Sobol analysis...")
    res = compute_sobol_sampling(size=1000, compute_second_order=True)

    print(f"First-order indices (Saltelli): {res['first_order']}")
    print(f"Total-order indices (Saltelli): {res['total_order']}")
    print(f"First-order indices (Martinez): {res['martinez_first_order']}")
    print(f"Total-order indices (Martinez): {res['martinez_total_order']}")
    print(f"Second-order indices matrix:\n{res['second_order']}")

    # 2. PCE-based estimation
    print("\nRunning PCE-based analytical Sobol analysis...")
    pce_fo, pce_to = compute_sobol_pce(sample_size=400, total_degree=6)
    print(f"PCE First-order indices: {pce_fo}")
    print(f"PCE Total-order indices: {pce_to}")

    # Theoretical Ishigami values: S1 ~ 0.3138, S2 ~ 0.4424, S3 ~ 0.0
    # Total order: ST1 ~ 0.5576, ST2 ~ 0.4424, ST3 ~ 0.2437
    assert 0.25 < pce_fo[0] < 0.38, "S1 should be around 0.31"
    assert 0.38 < pce_fo[1] < 0.50, "S2 should be around 0.44"
    assert abs(pce_fo[2]) < 0.05, "S3 should be close to 0"

    print("\nSensitivity analysis script executed successfully.")


if __name__ == "__main__":
    main()
