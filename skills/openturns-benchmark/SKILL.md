---
name: openturns-benchmark
description: Benchmarking CPU elapsed time vs sample size in OpenTURNS using logarithmic scaling, maximum time stopping criteria, and native OpenTURNS plot utilities. Use when benchmarking OpenTURNS algorithms, polynomial chaos expansion, or least squares methods over growing sample sizes.
---

# OpenTURNS Benchmark

Guidelines and reusable code structures for benchmarking CPU execution time as a function of sample size in OpenTURNS, featuring dynamic time-based stopping criteria and native OpenTURNS plot utilities.

## When to Use

Use this skill when:
- Benchmarking execution time vs sample size for OpenTURNS algorithms, metamodels, polynomial chaos expansion (PCE), or linear least-squares solvers.
- Comparing multiple algorithms or solvers (e.g., LOO vs K-Fold cross-validation, QR vs SVD vs Cholesky).
- Constructing log-log performance plots with `ot.Graph`, `ot.Curve`, `ot.Cloud`, and `openturns.viewer.View`.

## Key Benchmarking Principles

1. **Incremental Sample Size & Dynamic Exit**
   - **Initial size $N_0$:** Scaled relative to problem complexity (e.g., $N_0 = 2 \times P$ for $P$ basis functions, or $N_0 = 5 \times k$ for $k$-fold cross-validation).
   - **Geometric growth:** Increase sample size geometrically: $N_{k+1} = \lfloor N_k \times f \rfloor$ with factor $f > 1.0$ (default $f = 2.0$).
   - **Time limit stopping criterion:** Stop the iteration loop as soon as $t_{\text{elapsed}} > t_{\text{max}}$ (e.g. `maximum_time = 1.0` or `4.0` seconds) or when reaching `maximum_number_of_iterations`.

2. **Native OpenTURNS Graphing**
   - **Data drawables:** Combine point markers (`ot.Cloud`) and trend lines (`ot.Curve`) using `plotCloudAndCurve`.
   - **Multi-curve comparison:** Use distinct colors from `ot.Drawable.BuildDefaultPalette(n)`, point styles (`"circle"`, `"+"`, `"v"`, `"^"`), and line styles (`"solid"`, `"dashed"`, `"dotdash"`, `"longdash"`).
   - **Log-log scale:** Apply logarithmic transformation on both axes:
     ```python
     graph.setLogScale(ot.GraphImplementation.LOGXY)
     ```
   - **Legend formatting:** Position legend cleanly at the top left without obscuring data:
     ```python
     graph.setLegendPosition("upper left")
     graph.setLegendCorner((1.0, 1.0))
     ```
   - **Rendering:** Pass the figure size explicitly via `otv.View(graph, figure_kw={"figsize": (5.0, 3.0)})`.

## Code Template

```python
import time
import openturns as ot
import openturns.viewer as otv


def plotCloudAndCurve(
    x_data, y_data, color=None, point_style="circle", line_style="solid", legend=""
):
    """Plot a cloud of points and a curve into an OpenTURNS Graph."""
    if color is None:
        palette = ot.Drawable.BuildDefaultPalette(1)
        color = palette[0]
    graph = ot.Graph("", "", "", True)
    
    cloud = ot.Cloud(x_data, y_data)
    cloud.setLegend(legend)
    cloud.setPointStyle(point_style)
    cloud.setColor(color)
    graph.add(cloud)
    
    curve = ot.Curve(x_data, y_data)
    curve.setLineStyle(line_style)
    curve.setColor(color)
    graph.add(curve)
    
    return graph


def benchmark_task(
    run_func,
    sample_size_init=10,
    sample_size_factor=2.0,
    maximum_time=1.0,
    maximum_number_of_iterations=100,
    verbose=False,
):
    """Generic loop to measure elapsed time across geometrically increasing sample sizes."""
    sample_size_list = []
    elapsed_time_list = []
    sample_size = sample_size_init

    for _ in range(maximum_number_of_iterations):
        start_time = time.time()
        run_func(sample_size)
        stop_time = time.time()

        elapsed_time = stop_time - start_time
        sample_size_list.append(sample_size)
        elapsed_time_list.append(elapsed_time)

        if verbose:
            print(f"n={sample_size}, elapsed={elapsed_time:.4f} (s)")

        if elapsed_time > maximum_time:
            break

        sample_size = int(sample_size * sample_size_factor)

    return sample_size_list, elapsed_time_list


def create_benchmark_graph(title="Benchmark", x_label="Sample size", y_label="Elapsed time (s)"):
    """Initialize an OpenTURNS log-log benchmark graph with standard legend positioning."""
    graph = ot.Graph(title, x_label, y_label, True)
    graph.setLogScale(ot.GraphImplementation.LOGXY)
    graph.setLegendPosition("upper left")
    graph.setLegendCorner((1.0, 1.0))
    return graph
```
