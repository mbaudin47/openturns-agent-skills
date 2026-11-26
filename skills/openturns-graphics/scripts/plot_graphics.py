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
    """Demonstrate DrawPairs, DrawPairsMarginals, DrawPairsXY, and DrawParallelCoordinates."""
    ot.RandomGenerator.SetSeed(42)

    # 1. Sample from 3D correlated normal distribution (as in plot_visualize_pairs)
    R = ot.CorrelationMatrix(3)
    for i in range(1, 3):
        R[i, i - 1] = -0.4
    distribution = ot.Normal([0.0] * 3, [5.0] * 3, R)
    sample = distribution.getSample(200)
    sample.setDescription(["X0", "X1", "X2"])

    # 2. Pairs plot (returns ot.GridLayout of 2D marginal projections)
    pairs_grid = ot.VisualTest.DrawPairs(sample)
    v_pairs = otv.View(pairs_grid, figure_kw={"figsize": (6.0, 6.0)})
    # Adjust spacing to avoid label collisions in pairs matrix
    v_pairs.getFigure().subplots_adjust(hspace=0.35, wspace=0.35)
    v_pairs.getFigure().savefig("demo_pairs.png", bbox_inches="tight")
    v_pairs.close()

    # 3. Pairs with theoretical distribution overlay (PDFs and isolines)
    pairs_marg_grid = ot.VisualTest.DrawPairsMarginals(sample, distribution)
    v_pairs_marg = otv.View(pairs_marg_grid, figure_kw={"figsize": (6.0, 6.0)})
    v_pairs_marg.getFigure().subplots_adjust(hspace=0.35, wspace=0.35)
    v_pairs_marg.getFigure().savefig("demo_pairs_marginals.png", bbox_inches="tight")
    v_pairs_marg.close()

    # 4. Input/Output Pairs plot (DrawPairsXY)
    model = ot.SymbolicFunction(["X0", "X1", "X2"], ["X0 + 2.0 * X1 - X2", "X0 * X2"])
    output_sample = model(sample)
    output_sample.setDescription(["Y0", "Y1"])

    pairs_xy_grid = ot.VisualTest.DrawPairsXY(sample, output_sample)
    v_pairs_xy = otv.View(pairs_xy_grid, figure_kw={"figsize": (8.0, 5.0)})
    v_pairs_xy.getFigure().subplots_adjust(hspace=0.35, wspace=0.35)
    v_pairs_xy.getFigure().savefig("demo_pairs_xy.png", bbox_inches="tight")
    v_pairs_xy.close()

    # 5. Parallel coordinates with target selection
    # Highlight lines where Y0 in [1.0, 5.0] in red (quantileScale=False)
    par_graph = ot.VisualTest.DrawParallelCoordinates(
        sample, output_sample.getMarginal(0), 1.0, 5.0, "red", False
    )
    v_par = otv.View(par_graph, figure_kw={"figsize": (6.5, 3.5)})
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
