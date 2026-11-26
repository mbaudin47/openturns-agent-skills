---
name: openturns-graphics
description: Create, customize, and export OpenTURNS graphics including Curve, Cloud, Polygon.FillBetween, 2D contour plots and level lines (Contour, drawPDF, drawCrossCuts, filled, hatches, log/rank norm, colorbar), pairs plots (DrawPairs, DrawPairsMarginals, DrawPairsXY), parallel coordinates, GridLayout, and View customization. Use when creating OpenTURNS plots, styling contour levels, resolving subplot overlaps with subplots_adjust, or saving figures.
---

# OpenTURNS Graphics and Contour Guide

Comprehensive guide for creating, styling, arranging, and exporting plots in OpenTURNS using `ot.Graph`, basic Drawables (`Curve`, `Cloud`, `Polygon`), 2D `Contour` plots and level lines, statistical visual tests, and `openturns.viewer.View`.

## Quick Reference

| Purpose | Class / Method |
|---|---|
| **Import viewer** | `import openturns.viewer as otv` |
| **Create graph container** | `ot.Graph(title, x_title, y_title, show_axes_bool)` |
| **Curve (line plot)** | `ot.Curve(sample_x, sample_y)` |
| **Cloud (scatter plot)** | `ot.Cloud(sample_x, sample_y)` |
| **Fill area under curve** | `ot.Polygon.FillBetween(x.asPoint(), vLow, vUp)` |
| **Contour from function** | `f.draw([xmin, ymin], [xmax, ymax], [nx, ny])` |
| **Contour from distribution** | `dist.drawPDF([xmin, ymin], [xmax, ymax])` |
| **Contour from grid data** | `ot.Contour(x, y, data)` |
| **Cross-cuts grid (2D & 1D)** | `f.drawCrossCuts(center, xmin, xmax, pts, with_1d, is_filled, vmin, vmax)` *(returns `ot.GridLayout`)* |
| **Access Contour methods** | `contour = graph.getDrawable(0).getImplementation()` |
| **Filled contour** | `contour.setIsFilled(True)` |
| **Level lines (iso-curves)** | `contour.setIsFilled(False); contour.setDrawLabels(True)` |
| **Contour colormap & bar** | `contour.setColorMap("inferno"); contour.setColorBarPosition("right")` |
| **Log / Rank color norm** | `contour.setColorMapNorm("log")` or `"rank"` |
| **Contour hatches & alpha** | `contour.setAlpha(0.3); contour.setHatches(["/", "\\", "+", "*"])` |
| **Pairs plot** | `ot.VisualTest.DrawPairs(sample)` *(returns `ot.GridLayout`)* |
| **Pairs with distribution** | `ot.VisualTest.DrawPairsMarginals(sample, distribution)` |
| **Pairs input/output** | `ot.VisualTest.DrawPairsXY(sampleX, sampleY)` *(returns `ot.GridLayout`)* |
| **Parallel coordinates** | `ot.VisualTest.DrawParallelCoordinates(input_s, output_s, ymin, ymax, color)` |
| **Set color palette** | `graph.setColors(ot.Drawable.BuildDefaultPalette(n_graphs))` |
| **Set figure size** | `otv.View(graph, figure_kw={"figsize": (6.0, 4.0)})` |
| **Move / configure legend** | `otv.View(graph, legend_kw={"bbox_to_anchor": (1.05, 1.0), "loc": "upper left"})` |
| **Embed in Matplotlib ax** | `otv.View(graph, figure=fig, axes=[ax])` |
| **Fix GridLayout overlaps** | `view.getFigure().subplots_adjust(hspace=0.4, wspace=0.35)` |
| **Save figure** | `view.save("fig.png", dpi=300)` or `view.getFigure().savefig("fig.pdf", bbox_inches="tight")` |

---

## 1. Creating and Assembling Graphs (Curves, Clouds, and Polygons)

An `ot.Graph` acts as a canvas containing one or more `ot.Drawable` objects (e.g. `Curve`, `Cloud`, `Polygon`).

### Step-by-Step Construction with Curves and Clouds

```python
import openturns as ot
import openturns.viewer as otv

# 1. Create the graph container
graph = ot.Graph("Model vs Observations", "X axis", "Y axis", True)

# 2. Build 2D sample data for drawables
sample_x = ot.Sample([[1.0], [2.0], [3.0], [4.0], [5.0]])
sample_y = ot.Sample([[1.5], [3.7], [2.8], [5.1], [7.2]])

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
palette = ot.Drawable.BuildDefaultPalette(len(graph.getDrawables()))
graph.setColors(palette)
```

### Filling Area Under a Curve (`ot.Polygon.FillBetween`)
Used to highlight tails, confidence intervals, or probability masses under a PDF:

```python
dist = ot.Normal()
graph = dist.drawPDF()

# Integration interval [1.0, 2.5]
a, b = 1.0, 2.5
n_pts = 100
step = (b - a) / (n_pts - 1)
grid = ot.RegularGrid(a, step, n_pts)
x_pts = grid.getVertices()
y_pts = dist.computePDF(x_pts)

# Build filled polygon under curve
v_low = [0.0] * n_pts
v_up = [y_pts[i, 0] for i in range(n_pts)]
shaded_area = ot.Polygon.FillBetween(x_pts.asPoint(), v_low, v_up)
shaded_area.setColor("lightblue")
shaded_area.setLegend("P(1 <= X <= 2.5)")

graph.add(shaded_area)
view = otv.View(graph)
```

---

## 2. 2D Contour Plots and Level Lines (Lignes de niveaux)

Contour plots represent scalar fields $z = f(x, y)$ in 2D space. In OpenTURNS, contour plots use the `ot.Contour` class and can be created from analytical functions, 2D joint distributions, or discrete grid data.

### Creating Contour Graphs

#### From a 2D Function (`Function.draw`)
```python
# 2D analytical model
f = ot.SymbolicFunction(["x", "y"], ["exp(-sin(cos(y)^2 * x^2 + sin(x)^2 * y^2))"])
xmin, xmax = -5.0, 5.0
ymin, ymax = -5.0, 5.0
nx, ny = 75, 75

# Draw contour graph
graph = f.draw([xmin, ymin], [xmax, ymax], [nx, ny])
```

#### From a 2D Joint Distribution (`Distribution.drawPDF`)
```python
corr = ot.CorrelationMatrix(2)
corr[0, 1] = 0.5
distribution = ot.JointDistribution([ot.Normal(), ot.Normal()], ot.NormalCopula(corr))

# Direct contour of the joint PDF
graph = distribution.drawPDF([-4.0, -4.0], [4.0, 4.0])
```

#### From Discrete Grid Data (`ot.Contour`)
```python
# Build coordinate vectors and evaluated sample
x = ot.Box([nx]).generate() * [xmax - xmin] + [xmin]
y = ot.Box([ny]).generate() * [ymax - ymin] + [ymin]
input_grid = ot.Box([nx, ny]).generate() * [xmax - xmin, ymax - ymin] + [xmin, ymin]
data = f(input_grid)

# Construct Contour drawable directly
contour = ot.Contour(x, y, data)
graph = ot.Graph("Explicit Grid Contour", "x", "y", True)
graph.add(contour)
```

---

### Accessing and Configuring `ot.Contour`

A `graph.getDrawable(0)` call returns a generic `ot.Drawable`. Specific contour configuration methods require retrieving the underlying `Contour` implementation via `.getImplementation()`:

```python
contour = graph.getDrawable(0).getImplementation()
```

#### Iso-Lines (Level Curves) vs Filled Contours
* **Iso-lines only**: `contour.setIsFilled(False)`
* **Filled areas**: `contour.setIsFilled(True)`

#### Best Practice: Superposing Filled Contours and Iso-Lines
Combining a filled background gradient with crisp, labeled level lines on top gives optimal readability:

```python
graph = distribution.drawPDF([-4.0, -4.0], [4.0, 4.0])

# 1. Background: filled contour with colorbar
filled_contour = graph.getDrawable(0).getImplementation()
filled_contour.setIsFilled(True)
filled_contour.setColorMap("viridis")
filled_contour.setColorBarPosition("right")
graph.setDrawable(0, filled_contour)

# 2. Foreground: sharp black level lines with labels
lines_contour = graph.getDrawable(0).getImplementation()
lines_contour.setIsFilled(False)
lines_contour.setColor("black")
lines_contour.setColorBarPosition("")  # Hide duplicate colorbar
lines_contour.setLineWidth(1.5)
lines_contour.setDrawLabels(True)
graph.add(lines_contour)

view = otv.View(graph)
```

---

### Controlling Levels and Labels

* **Automatic levels**: `contour.buildDefaultLevels(10)`
* **Global default level count**: `ot.ResourceMap.SetAsUnsignedInteger("Contour-DefaultLevelsNumber", 8)`
* **Explicit levels**: `contour.setLevels([0.01, 0.05, 0.1, 0.2, 0.5])`
* **Let Matplotlib decide automatically**: `contour.setLevels([])`
* **Retrieve current levels**: `levels = contour.getLevels()`
* **Show numeric labels on lines**: `contour.setDrawLabels(True)`
* **Custom formatted labels** (e.g. scientific notation):
  ```python
  contour.setDrawLabels(True)
  contour.setLabels(["{:.2e}".format(lvl) for lvl in contour.getLevels()])
  ```

---

### Colormaps, Scaling, and Normalization

#### Color Normalization (`setColorMapNorm`)
For functions or likelihoods spanning several orders of magnitude (e.g. log-likelihood, steep bivariate densities), standard linear scaling loses detail:
* **Logarithmic scale**: `contour.setColorMapNorm("log")`
* **Rank-based scale** (quantile spacing): `contour.setColorMapNorm("rank")`

#### Range and Colorbar Tuning
```python
contour.setColorMap("inferno")
contour.setColorBarPosition("right")  # Set to "" to hide
contour.setVmin(0.01)
contour.setVmax(2.5)
contour.setExtend("both")  # "neither", "min", "max", or "both"
```

#### Multi-color Contours via `otv.View`
While `ot.Contour` accepts a single color (`contour.setColor("red")`), multi-color palettes can be applied via `contour_kw` in `View`:
```python
palette = ot.Drawable.BuildTableauPalette(len(contour.getLevels()))
view = otv.View(graph, contour_kw={"colors": palette, "cmap": None})
```

#### Hatches and Transparency
```python
contour.setAlpha(0.35)
contour.setHatches(["/", "\\", "/\\", "+", "*"])
```

---

### Multidimensional Function Cross-Cuts (`Function.drawCrossCuts`)

The `drawCrossCuts()` method provides a qualitative sensitivity analysis of a scalar-output multidimensional function $f: \mathbb{R}^n \rightarrow \mathbb{R}$ by drawing an `ot.GridLayout` of 2D contour panels (and optionally 1D curves along the diagonal).

Around a central point $\boldsymbol{c} = (c_1, \dots, c_n)$ (typically the distribution mean or median), all variables are frozen except one or two:
- **1D cuts** ($i = j$): plots $y = f(c_1, \dots, s, \dots, c_n)$ for $s \in [x_i^{min}, x_i^{max}]$ along the diagonal.
- **2D cuts** ($i \neq j$): plots contour maps of $y = f(c_1, \dots, s, \dots, t, \dots, c_n)$ for $(s, t) \in [x_i^{min}, x_i^{max}] \times [x_j^{min}, x_j^{max}]$.
- **Comparable color scale**: all 2D contour subplots share a unified range $[v_{min}, v_{max}]$ across the entire matrix.

#### Method Parameters
```python
grid = f.drawCrossCuts(
    centralPoint,           # list or Point of float (dimension n)
    xMin,                   # lower bounds of inputs (dimension n)
    xMax,                   # upper bounds of inputs (dimension n)
    pointNumber,            # list or Indices of int (discretization per input)
    withMonoDimensionalCuts,# bool: True to include 1D curves on diagonal, False for 2D only
    isFilled,               # bool: True for filled contours, False for level lines
    vMin, vMax              # float (optional): global min/max for the shared color scale
)
```

#### Complete Workflow with Shared Colorbar and Clean Axes
In higher dimensions ($n \ge 3$), configuring a unified colormap, setting figure dimensions, adding a single global colorbar, and hiding redundant interior tick labels produces publication-ready visual sensitivity plots:

```python
import openturns as ot
import openturns.viewer as otv

# 1. Define model and parameter bounds
f = ot.SymbolicFunction(
    ["x0", "x1", "x2"],
    ["sin(x0) + 7.0 * sin(x1)^2 + 0.1 * x2^4 * sin(x0)"]
)
f.setInputDescription(["x0", "x1", "x2"])
f.setOutputDescription(["y"])
f.setName("Ishigami Cross Cuts")

center = [0.0, 0.0, 0.0]
lower_bound = [-3.14, -3.14, -3.14]
upper_bound = [3.14, 3.14, 3.14]
n_points = [20, 20, 20]

# 2. Generate cross-cut grid (without 1D cuts, filled contours)
grid = f.drawCrossCuts(
    center,
    lower_bound,
    upper_bound,
    n_points,
    False,   # withMonoDimensionalCuts
    True,    # isFilled
    -10.0,   # vMin
    18.0     # vMax
)
grid.setTitle("")

# 3. Apply colormap and level count across all panels via View
view = otv.View(grid, contour_kw={"cmap": "viridis", "levels": 20})

fig = view.getFigure()
axes = view.getAxes()
fig.set_size_inches(10, 10)

# 4. Add a single shared colorbar referencing the first 2D contour subview
fig.colorbar(
    view.getSubviews()[1][0].getContourSets()[0],
    ax=axes[:-1, -1],
    fraction=0.25,
    pad=0.04
)

# 5. Hide redundant interior tick labels in the triangular grid
for i in range(len(axes)):
    for j in range(i + 1):
        if i < len(axes) - 1:
            axes[i][j].xaxis.set_ticklabels([])
        if j > 0:
            axes[i][j].yaxis.set_ticklabels([])

fig.subplots_adjust(top=0.98, bottom=0.06, left=0.08, right=0.92)
```

---

## 3. Statistical Visual Tests

OpenTURNS provides specialized diagnostic matrices under `ot.VisualTest`:

### Pairs Plot (`DrawPairs`)
Matrix of 2D scatter plots for all pairwise combinations of marginals. Returns an `ot.GridLayout` of dimension $(d-1) \times (d-1)$:

```python
R = ot.CorrelationMatrix(3)
for i in range(1, 3):
    R[i, i - 1] = -0.4
sample = ot.Normal([0.0] * 3, [1.0] * 3, R).getSample(200)
sample.setDescription(["X0", "X1", "X2"])

grid = ot.VisualTest.DrawPairs(sample)
view = otv.View(grid, figure_kw={"figsize": (6.0, 6.0)})
```

### Pairs Plot with Distribution (`DrawPairsMarginals`)
Overlays theoretical marginal PDFs on the diagonal and 2D contour iso-lines on off-diagonal plots:

```python
distribution = ot.Normal(3)
grid_marginals = ot.VisualTest.DrawPairsMarginals(sample, distribution)
```

### Input/Output Pairs Plot (`DrawPairsXY`)
Projects marginals of an output sample $Y$ (rows) against marginals of an input sample $X$ (columns):

```python
model = ot.SymbolicFunction(["X0", "X1", "X2"], ["X0 + 2*X1", "X0 * X2"])
output_sample = model(sample)
output_sample.setDescription(["Y0", "Y1"])

grid_xy = ot.VisualTest.DrawPairsXY(sample, output_sample)
```

### Parallel Coordinates (`DrawParallelCoordinates`)
Visualizes high-dimensional inputs and highlights lines leading to an output criterion:

```python
par_graph = ot.VisualTest.DrawParallelCoordinates(
    sample, output_sample.getMarginal(0), 1.0, 4.0, "red", False
)
```

---

## 4. Multi-Plot Layouts (`GridLayout`) and Matplotlib Integration

### Inspecting and Modifying Sub-Graphs in a `GridLayout`
```python
# Check grid dimensions
rows = grid.getNbRows()
cols = grid.getNbColumns()

# Access and customize a specific sub-graph at row i, column j
sub_graph = grid.getGraph(0, 0)
sub_graph.setTitle("Subplot Title")
grid.setGraph(0, 0, sub_graph)
```

### Resolving Overlaps in `GridLayout` / `DrawPairs`
Compact grids often lead to overlapping tick marks, axis labels, or titles. Always adjust spacing using `fig.subplots_adjust` or `plt.subplots_adjust`:
- **`wspace`**: horizontal margin between subplots (fraction of average axis width).
- **`hspace`**: vertical margin between subplots (fraction of average axis height).

```python
view = otv.View(grid, figure_kw={"figsize": (8.0, 6.0)})
fig = view.getFigure()

# Increase horizontal (wspace) and vertical (hspace) margins
fig.subplots_adjust(hspace=0.45, wspace=0.35)
```

### Advanced View Customization (`figure_kw`, `legend_kw`, Axes access)
`otv.View` bridges OpenTURNS `Graph` and `GridLayout` objects to Matplotlib `Figure` and `Axes` instances:

```python
# Move legend outside the plot box and customize figure size
view = otv.View(
    graph,
    figure_kw={"figsize": (6.5, 4.0), "dpi": 150},
    legend_kw={"bbox_to_anchor": (1.05, 1.0), "loc": "upper left", "frameon": True},
    plot_kw={"color": "blue"},
)

# Access underlying Matplotlib objects directly
fig = view.getFigure()
axes = view.getAxes()
axes[0].grid(True, linestyle=":", alpha=0.6)
```

### Embedding OpenTURNS Graphs in Matplotlib Subplots
Render OpenTURNS graphs directly into existing Matplotlib axes:

```python
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(10, 4))
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)

_ = otv.View(graph_1, figure=fig, axes=[ax1])
_ = otv.View(graph_2, figure=fig, axes=[ax2])
fig.suptitle("Side-by-side OpenTURNS Figures")
```

---

## 5. Exporting Figures

When legends are placed outside the axes (e.g. with `bbox_to_anchor` in `legend_kw`) or when multiple subplots are tiled, default bounding box calculations may truncate outside legends, axis labels, or colorbars.

Always use **`bbox_inches="tight"`** when exporting to compute a bounding box encompassing all figure elements:

```python
# Save to vector PDF with tight bounding box (preserves exterior legends)
view.getFigure().savefig("filename.pdf", bbox_inches="tight")

# Save to vector SVG
view.getFigure().savefig("filename.svg", bbox_inches="tight")

# Save to high-resolution raster PNG (kwargs are forwarded to savefig)
view.save("filename.png", dpi=300, bbox_inches="tight")
# Or equivalently:
view.getFigure().savefig("filename.png", dpi=300, bbox_inches="tight")

# Show all windows if running interactively
otv.View.ShowAll()

# Always close view in batch/automated scripts to free memory
view.close()
```
