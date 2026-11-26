#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenTURNS Graphics and Visualization Guide.

This script demonstrates:
1. Creating Graph containers and adding Curve and Cloud drawables.
2. Styling palettes, line styles, point styles, and legends.
3. Multi-variable visual tests: DrawPairs, DrawPairsMarginals, DrawParallelCoordinates.
4. Setting figure size and moving legend location using openturns.viewer.View.
5. Managing multi-plot layouts (GridLayout) and adjusting margins (hspace, wspace)
   with subplots_adjust to prevent overlapping subplots.
6. Exporting graphics to PDF and PNG with tight bounding boxes.
"""

# %%
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for automated execution
import matplotlib.pyplot as plt
import openturns as ot
import openturns.viewer as otv


# %%
def demo_curve_and_cloud():
    """Build a graph with a fitted curve, observation cloud, and styled palette."""
    graph = ot.Graph("Model vs Observations", "Input X", "Output Y", True)

    # Observations (Cloud)
    x_obs = ot.Sample([[1.0], [2.0], [3.0], [4.0], [5.0]])
    y_obs = ot.Sample([[1.1], [3.9], [8.8], [16.2], [24.8]])
    cloud = ot.Cloud(x_obs, y_obs)
    cloud.setLegend("Observations")
    cloud.setPointStyle("bullet")

    # Model curve (Curve)
    x_curve = ot.Sample([[0.1 * i] for i in range(10, 51)])
    y_curve = ot.Sample([[0.98 * (x[0] ** 2)] for x in x_curve])
    curve = ot.Curve(x_curve, y_curve)
    curve.setLegend("Fitted y = a * x^2")
    curve.setLineStyle("dashed")
    curve.setLineWidth(2)

    graph.add(cloud)
    graph.add(curve)

    # Set palette across drawables
    palette = ot.Drawable().BuildDefaultPalette(len(graph.getDrawables()))
    graph.setColors(palette)

    # Render with custom size and outside legend
    view = otv.View(
        graph,
        figure_kw={"figsize": (5.5, 3.5)},
        legend_kw={"bbox_to_anchor": (1.05, 1.0), "loc": "upper left"},
    )
    fig = view.getFigure()
    fig.savefig("demo_curve_cloud.png", bbox_inches="tight")
    view.close()


# %%
def demo_visual_tests():
    """Demonstrate DrawPairs, DrawPairsMarginals, and DrawParallelCoordinates."""
    ot.RandomGenerator.SetSeed(42)

    # Sample from 3D correlated normal distribution
    corr = ot.CorrelationMatrix(3)
    corr[0, 1] = 0.6
    corr[1, 2] = -0.4
    copula = ot.NormalCopula(corr)
    distribution = ot.JointDistribution([ot.Normal(), ot.Normal(), ot.Normal()], copula)
    sample = distribution.getSample(150)
    sample.setDescription(["X1", "X2", "X3"])

    # 1. Pairs plot
    pairs_graph = ot.VisualTest.DrawPairs(sample)
    v_pairs = otv.View(pairs_graph, figure_kw={"figsize": (6.0, 6.0)})
    v_pairs.getFigure().savefig("demo_pairs.png", bbox_inches="tight")
    v_pairs.close()

    # 2. Pairs with theoretical distribution overlay
    pairs_marg_graph = ot.VisualTest.DrawPairsMarginals(sample, distribution)
    v_pairs_marg = otv.View(pairs_marg_graph, figure_kw={"figsize": (6.0, 6.0)})
    v_pairs_marg.getFigure().savefig("demo_pairs_marginals.png", bbox_inches="tight")
    v_pairs_marg.close()

    # 3. Parallel coordinates with target selection
    # Y = X1 + 2*X2 - X3
    model = ot.SymbolicFunction(["X1", "X2", "X3"], ["X1 + 2.0 * X2 - X3"])
    output_sample = model(sample)
    output_sample.setDescription(["Y"])

    # Highlight lines where Y in [1.0, 3.0] in red (quantileScale=False)
    par_graph = ot.VisualTest.DrawParallelCoordinates(
        sample, output_sample, 1.0, 3.0, "red", False
    )
    v_par = otv.View(par_graph, figure_kw={"figsize": (6.0, 3.5)})
    v_par.getFigure().savefig("demo_parallel_coordinates.png", bbox_inches="tight")
    v_par.close()


# %%
def demo_grid_layout_with_spacing():
    """Demonstrate GridLayout and fixing overlapping labels via subplots_adjust."""
    grid = ot.GridLayout(2, 2)
    grid.setTitle("Marginal Probability Density Functions")

    grid.setGraph(0, 0, ot.Normal().drawPDF())
    grid.setGraph(0, 1, ot.Uniform(-2.0, 2.0).drawPDF())
    grid.setGraph(1, 0, ot.Exponential(1.5).drawPDF())
    grid.setGraph(1, 1, ot.LogNormal(0.0, 0.5).drawPDF())

    view = otv.View(grid, figure_kw={"figsize": (7.0, 5.5)})
    fig = view.getFigure()

    # Increase horizontal and vertical subplot margins to avoid overlapping titles/axes
    fig.subplots_adjust(hspace=0.45, wspace=0.35)

    fig.savefig("demo_grid_layout.pdf", bbox_inches="tight")
    view.close()


# %%
if __name__ == "__main__":
    demo_curve_and_cloud()
    demo_visual_tests()
    demo_grid_layout_with_spacing()
    print("All OpenTURNS graphics demos executed and saved successfully.")
