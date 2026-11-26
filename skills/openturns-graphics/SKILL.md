---
name: openturns-graphics
description: Create, customize, and export OpenTURNS graphics using ot.Graph, ot.Curve, ot.Cloud, pairs plots (DrawPairs, DrawPairsMarginals, DrawPairsXY), parallel coordinates (DrawParallelCoordinates), GridLayout, and openturns.viewer.View. Use when creating OpenTURNS plots, customizing palettes and colors, adjusting figure size, bounding box or legend positions, resolving subplot overlaps with subplots_adjust (hspace, wspace), or saving figures to PDF/PNG.
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
| **Pairs plot** | `ot.VisualTest.DrawPairs(sample)` *(returns `ot.GridLayout`)* |
| **Pairs with distribution** | `ot.VisualTest.DrawPairsMarginals(sample, distribution)` |
| **Pairs input/output** | `ot.VisualTest.DrawPairsXY(sampleX, sampleY)` *(returns `ot.GridLayout`)* |
| **Parallel coordinates** | `ot.VisualTest.DrawParallelCoordinates(input_sample, output_sample, min_val, max_val, color)` |
| **Set color palette** | `graph.setColors(ot.Drawable().BuildDefaultPalette(n_graphs))` |
| **Set figure size** | `otv.View(graph, figure_kw={"figsize": (4.0, 3.0)})` |
| **Move / configure legend** | `otv.View(graph, legend_kw={"bbox_to_anchor": (1.0, 1.0), "loc": "upper left"})` |
| **Display all windows** | `otv.View.ShowAll()` |
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
Draws each pair of 2-d marginal projection clouds for a multidimensional sample.
Returns an `ot.GridLayout` of dimension $(d-1) \times (d-1)$:

```python
import openturns as ot
import openturns.viewer as otv

# Generate correlated 3D normal sample
R = ot.CorrelationMatrix(3)
for i in range(1, 3):
    R[i, i - 1] = -0.4
distribution = ot.Normal([0.0] * 3, [5.0] * 3, R)
sample = distribution.getSample(200)
sample.setDescription(["X0", "X1", "X2"])

# Draw 2D pairwise projections (returns ot.GridLayout)
grid = ot.VisualTest.DrawPairs(sample)
view = otv.View(grid, figure_kw={"figsize": (6.0, 6.0)})
```

*Note on styling*: Point style defaults to `Drawable-DefaultPointStyle` in `ot.ResourceMap`, and the color defaults to the first color in the default palette.

### Pairs Plot with Distribution (`DrawPairsMarginals`)
Overlays theoretical marginal PDFs on the diagonal and 2D iso-contours on the off-diagonal scatter plots:

```python
distribution = ot.Normal(3)
pairs_marginals_graph = ot.VisualTest.DrawPairsMarginals(sample, distribution)
```

### Input/Output Pairs Plot (`DrawPairsXY`)
Draws 2-d projections relating marginals of an output sample $Y$ (in rows) with respect to marginals of an input sample $X$ (in columns). Useful for visualizing relationships between model inputs and outputs:

```python
# Model: Y = [X0 + X1, X0 - X2]
model = ot.SymbolicFunction(["X0", "X1", "X2"], ["X0 + X1", "X0 - X2"])
output_sample = model(sample)
output_sample.setDescription(["Y0", "Y1"])

grid_xy = ot.VisualTest.DrawPairsXY(sample, output_sample)
view_xy = otv.View(grid_xy, figure_kw={"figsize": (8.0, 5.0)})
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

`otv.View` bridges OpenTURNS `Graph` and `GridLayout` objects to Matplotlib `Figure` and `Axes` instances.

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

### Displaying All Windows
In interactive Python scripts or notebooks, show all open figures simultaneously:
```python
otv.View.ShowAll()
```

### Accessing Matplotlib Primitives

```python
fig = view.getFigure()
axes = view.getAxes()

# Directly adjust matplotlib properties on axes
axes[0].grid(True, linestyle=":", alpha=0.6)
```

---

## 4. Multi-Plot Layouts (`GridLayout`) and Overlap Management

An `ot.GridLayout(nb_rows, nb_cols)` arranges multiple sub-graphs into a grid. Both `ot.GridLayout` and visual test matrices (`DrawPairs`, `DrawPairsXY`) often suffer from overlapping titles, axis labels, or tick marks due to compact default margins.

### Inspecting and Modifying Sub-Graphs in a Grid
```python
# Check grid dimensions
rows = grid.getNbRows()
cols = grid.getNbColumns()

# Access and customize a specific sub-graph at row i, column j
sub_graph = grid.getGraph(0, 0)
sub_graph.setTitle("Subplot Title")
grid.setGraph(0, 0, sub_graph)
```

### Resolving Subplot Overlaps with `subplots_adjust`
To prevent labels from colliding, adjust the horizontal margin (`wspace`) and vertical margin (`hspace`) via `matplotlib.pyplot.subplots_adjust` or `fig.subplots_adjust`:
- **`wspace`**: horizontal margin between subplots (fraction of average axis width).
- **`hspace`**: vertical margin between subplots (fraction of average axis height).

```python
import matplotlib.pyplot as plt
import openturns as ot
import openturns.viewer as otv

# Render GridLayout or DrawPairs
view = otv.View(grid, figure_kw={"figsize": (8.0, 6.0)})
fig = view.getFigure()

# Increase margins to eliminate overlap between adjacent subplots
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
