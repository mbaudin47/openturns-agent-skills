#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structural reliability and rare event probability estimation with OpenTURNS.

This script demonstrates:
1. Setting up a limit state function and failure event via ThresholdEvent.
2. Estimating failure probability using FORM (First Order Reliability Method).
3. Estimating failure probability using SORM (Second Order Reliability Method).
4. Estimating rare failure probability using SubsetSampling.
5. Extracting the Hasofer-Lind index, design points, and importance factors.
6. Generating native OpenTURNS importance factor charts.
"""

# %%
import math
import openturns as ot
from openturns.usecases import cantilever_beam


# %%
def build_reliability_event(threshold=0.30):
    """
    Build the cantilever beam failure event:
    Deviation: y = (F * L^3) / (3 * E * I)
    Failure event: deviation >= threshold  <=>  threshold - deviation <= 0.

    Parameters
    ----------
    threshold : float, optional
        Maximum allowable deflection in meters (default is 0.30).

    Returns
    -------
    tuple
        (distribution, event, limit_state_model)
    """
    cb = cantilever_beam.CantileverBeam()
    distribution = cb.distribution

    # Limit state function: g(E, F, L, I) = threshold - (F * L^3) / (3 * E * I)
    limit_state = ot.SymbolicFunction(
        ["E", "F", "L", "I"],
        [f"{threshold} - (F * L^3) / (3.0 * E * I)"],
    )

    vect_in = ot.RandomVector(distribution)
    vect_out = ot.CompositeRandomVector(limit_state, vect_in)
    event = ot.ThresholdEvent(vect_out, ot.Less(), 0.0)

    return distribution, event, limit_state


# %%
def run_form_analysis(distribution, event):
    """
    Perform First Order Reliability Method (FORM).
    """
    solver = ot.Cobyla()
    # In modern OpenTURNS, set starting point on solver
    solver.setStartingPoint(distribution.getMean())

    form = ot.FORM(solver, event)
    form.run()
    result = form.getResult()

    pf = result.getEventProbability()
    beta_hl = result.getHasoferReliabilityIndex()
    x_star = result.getPhysicalSpaceDesignPoint()
    u_star = result.getStandardSpaceDesignPoint()
    importance = result.getImportanceFactors()
    graph = result.drawImportanceFactors()

    return {
        "pf": pf,
        "beta_hl": beta_hl,
        "x_star": x_star,
        "u_star": u_star,
        "importance": importance,
        "graph": graph,
        "result": result,
    }


# %%
def run_sorm_analysis(distribution, event):
    """
    Perform Second Order Reliability Method (SORM).
    """
    solver = ot.Cobyla()
    solver.setStartingPoint(distribution.getMean())

    sorm = ot.SORM(solver, event)
    sorm.run()
    result = sorm.getResult()

    pf_breitung = result.getEventProbabilityBreitung()
    pf_tvedt = result.getEventProbabilityTvedt()

    return {
        "pf_breitung": pf_breitung,
        "pf_tvedt": pf_tvedt,
        "result": result,
    }


# %%
def run_subset_sampling(event, max_outer=500, block_size=100):
    """
    Perform advanced simulation for rare events using SubsetSampling.
    """
    subset = ot.SubsetSampling(event)
    subset.setMaximumOuterSampling(max_outer)
    subset.setBlockSize(block_size)
    subset.run()

    result = subset.getResult()
    pf_estimate = result.getProbabilityEstimate()
    cov = result.getCoefficientOfVariation()

    return {
        "pf": pf_estimate,
        "cov": cov,
        "result": result,
    }


# %%
def main():
    print("=== Structural Reliability Analysis with OpenTURNS ===")

    # 1. Event setup
    threshold = 0.30
    distribution, event, _ = build_reliability_event(threshold=threshold)
    print(f"Limit state threshold: {threshold} m")
    print(f"Random variables: {distribution.getDescription()}")

    # 2. FORM Analysis
    print("\n1. Running FORM (First Order Reliability Method)...")
    res_form = run_form_analysis(distribution, event)
    print(f"FORM Failure Probability Pf: {res_form['pf']:.4e}")
    print(f"Hasofer-Lind Reliability Index Beta: {res_form['beta_hl']:.4f}")
    print(f"Physical design point X*: {res_form['x_star']}")
    print(f"Standard design point U*: {res_form['u_star']}")
    print(f"Importance factors:\n{res_form['importance']}")

    # 3. SORM Analysis
    print("\n2. Running SORM (Second Order Reliability Method)...")
    res_sorm = run_sorm_analysis(distribution, event)
    print(f"SORM Breitung Pf: {res_sorm['pf_breitung']:.4e}")
    print(f"SORM Tvedt Pf:    {res_sorm['pf_tvedt']:.4e}")

    # 4. Subset Sampling Analysis
    print("\n3. Running Subset Sampling (MCMC-based rare event simulation)...")
    res_subset = run_subset_sampling(event, max_outer=600, block_size=100)
    print(
        f"Subset Sampling Pf: {res_subset['pf']:.4e} (CV = {res_subset['cov']:.2%})"
    )

    # Assertions
    # Both FORM and SORM give rare event probability around 1e-6 to 4e-7
    assert 1e-7 < res_form["pf"] < 1e-5, f"FORM Pf unexpected: {res_form['pf']}"
    assert 1e-7 < res_sorm["pf_breitung"] < 1e-5, f"SORM Pf unexpected: {res_sorm['pf_breitung']}"
    assert 4.0 < res_form["beta_hl"] < 5.5, f"Beta HL unexpected: {res_form['beta_hl']}"

    print("\nReliability analysis script executed successfully.")


if __name__ == "__main__":
    main()
