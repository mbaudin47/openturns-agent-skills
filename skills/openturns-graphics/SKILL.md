---
name: openturns-graphics
description: Create, customize, and export OpenTURNS graphics using ot.Graph, ot.Curve, ot.Cloud, pairs plots (DrawPairs, DrawPairsMarginals), parallel coordinates (DrawParallelCoordinates), GridLayout, and openturns.viewer.View. Use when creating OpenTURNS plots, customizing palettes and colors, adjusting figure size, bounding box or legend positions, resolving subplot overlaps with subplots_adjust (hspace, wspace), or saving figures to PDF/PNG.
---

# OpenTURNS Graphics Guide

Comprehensive guide for creating, styling, arranging, and exporting plots in OpenTURNS using `ot.Graph`, specialized Drawables, statistical visual tests, and `openturns.viewer.View`.

## Quick Reference

| Purpose | Class / Method |
|---|---|
| **Import viewer** | `import openturns.viewer as otv` |
| **Create graph** | `ot.Graph(title, x_title, y_title, show_axes_bool)` |
| **Curve (line plot)** | `ot.Curve(sample_x, sample_y)` |
| **Cloud (scatter plot)** | `ot.Cloud(sample_x, sample_y)` |
| **Pairs plot** | `ot.VisualTest.DrawPairs(sample)` |
| **Pairs with distribution** | `ot.VisualTest.DrawPairsMarginals(sample, distribution)` |
| **Parallel coordinates** | `ot.VisualTest.DrawParallelCoordinates(input_sample, output_sample, min_val, max_val, color)` |
| **Set color palette** | `graph.setColors(ot.Drawable().BuildDefaultPalette(n_graphs))` |
| **Set figure size** | `otv.View(graph, figure_kw={"figsize": (4.0, 3.0)})` |
| **Move / configure legend** | `otv.View(graph, legend_kw={"bbox_to_anchor": (1.0, 1.0), "loc": "upper left"})` |
| **Save figure** | `view.getFigure().savefig("filename.pdf", bbox_inches="tight")` |
| **Fix GridLayout overlaps** | `view.getFigure().subplots_adjust(hspace=0.4, wspace=0.4)` |

---

## 1. Creating and Assembling Graphs

An `ot.Graph` acts as a canvas containing one or more `ot.Drawable` objects (e.g. `Curve`, `Cloud`, `Polygon`).

```python
import openturns as ot
import openturns.viewer as otv

# 1. Create the graph container
graph = ot.Graph("My Title", "X axis", "Y axis", True)

# 2. Build 2D sample data for drawables
sample_x = ot.Sample([[1.0], [2.0], [3.0], [4.0]])
sample_y = ot.Sample([[1.5], [3.7], [2.8], [5.1]])

# 3. Create Curve and Cloud drawables
curve = ot.Curve(sample_x, sample_y)
curve.setLegend("Fitted Model")
curve.setLineStyle("dashed")
curve.setLineWidth(2)

cloud = ot.Cloud(sample_x, sample_y)
cloud.setLegend("Observations")
cloud.setPointStyle("bullet")

# 4. Add drawables to the graph
graph.add(curve)
graph.add(cloud)

# 5. Set custom palette across drawables
palette = ot.Drawable().BuildDefaultPalette(len(graph.getDrawables()))
graph.setColors(palette)
```

---

## 2. Statistical Visual Tests

OpenTURNS provides high-level diagnostic and multi-variable plots under `ot.VisualTest`.

### Pairs Plot (`DrawPairs`)
Displays a matrix of 2D scatter plots for all pairwise combinations of marginals:

```python
sample = ot.Normal(3).getSample(100)
sample.setDescription(["X1", "X2", "X3"])

# Generate pairwise scatter matrix
pairs_graph = ot.VisualTest.DrawPairs(sample)
```

### Pairs Plot with Distribution (`DrawPairsMarginals`)
Overlays theoretical marginal PDFs on the diagonal and 2D iso-contours on the off-diagonal scatter plots:

```python
distribution = ot.Normal(3)
pairs_marginals_graph = ot.VisualTest.DrawPairsMarginals(sample, distribution)
```

### Parallel Coordinates (`DrawParallelCoordinates`)
Visualizes high-dimensional input samples and highlights lines leading to a target output range:

```python
input_sample = ot.Normal(3).getSample(200)
input_sample.setDescription(["X0", "X1", "X2"])

# Scalar output model: Y = X0 + 2*X1 - X2
model = ot.SymbolicFunction(["X0", "X1", "X2"], ["X0 + 2.0 * X1 - X2"])
output_sample = model(input_sample)

# Highlight trajectories where output Y is in [2.0, 5.0] in red (quantileScale=False for physical scale)
par_graph = ot.VisualTest.DrawParallelCoordinates(
    input_sample, output_sample, 2.0, 5.0, "red", False
)
```

---

## 3. Customizing the Figure with `openturns.viewer.View`

`otv.View` bridges OpenTURNS `Graph` objects to Matplotlib `Figure` and `Axes` instances.

### Sizing and Legends

```python
import openturns.viewer as otv

# Configure figure size and outside legend placement
view = otv.View(
    graph,
    figure_kw={"figsize": (6.0, 4.0), "dpi": 150},
    legend_kw={"bbox_to_anchor": (1.05, 1.0), "loc": "upper left", "frameon": True},
)
```

### Accessing Matplotlib Primitives

```python
fig = view.getFigure()
axes = view.getAxes()

# Directly adjust matplotlib properties if needed
axes[0].grid(True, linestyle=":", alpha=0.6)
```

---

## 4. Resolving Overlaps in `GridLayout` and Multi-Plots

When using `ot.GridLayout` or multi-panel visual tests like `DrawPairs`, subplot labels and titles may collide or overlap due to default tight margins.

To fix this, increase the spacing between subplots using `matplotlib.pyplot.subplots_adjust` (or `fig.subplots_adjust`) by adjusting:
- **`wspace`**: horizontal margin between subplots (fraction of average axis width).
- **`hspace`**: vertical margin between subplots (fraction of average axis height).

```python
import matplotlib.pyplot as plt
import openturns as ot
import openturns.viewer as otv

# Example with GridLayout
grid = ot.GridLayout(2, 2)
grid.setGraph(0, 0, ot.Normal().drawPDF())
grid.setGraph(0, 1, ot.Uniform().drawPDF())
grid.setGraph(1, 0, ot.Exponential().drawPDF())
grid.setGraph(1, 1, ot.LogNormal().drawPDF())

# Render with View
view = otv.View(grid, figure_kw={"figsize": (8.0, 6.0)})
fig = view.getFigure()

# Increase margins to prevent overlapping titles and axis labels
fig.subplots_adjust(hspace=0.4, wspace=0.35)
```

Alternatively, call `plt.subplots_adjust`:
```python
plt.subplots_adjust(hspace=0.4, wspace=0.35)
```

---

## 5. Exporting Figures

Export figures to vector (`.pdf`, `.svg`) or raster (`.png`) formats using `bbox_inches="tight"` to ensure legends and bounding boxes are not cut off:

```python
# Save to PDF with bounding box adjustment
view.getFigure().savefig("filename.pdf", bbox_inches="tight")

# Save to high-resolution PNG
view.getFigure().savefig("filename.png", dpi=300, bbox_inches="tight")

# Always close view / figure when done in batch scripts
view.close()
```
