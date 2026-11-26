---
name: openturns-graph-bounds
description: Configure x and y axis limits, bounds, and bounding boxes on OpenTURNS Graph objects. Use when setting graph min/max limits or bounding boxes in OpenTURNS.
---

# OpenTURNS Graph Bounds Configuration

Configure axis limits and bounding boxes on OpenTURNS `Graph` objects efficiently depending on the OpenTURNS version.

## When to Use

- Setting x or y axis range limits on OpenTURNS graph objects.
- Adjusting graph bounding boxes when `setBoundingBox()` is required.
- Writing version-compatible Python code for OpenTURNS graphics (OpenTURNS 1.27 vs 1.28+).

## Usage Guidelines

### OpenTURNS 1.27 and Earlier

In OpenTURNS 1.27 and earlier, individual axis setters (`setXMin`, `setXMax`) do not exist. Use either the native `setBoundingBox()` method or configure the Matplotlib axes directly via `otv.View`:

#### 1. Native Bounding Box (`ot.Interval`)
```python
import openturns as ot

n = ot.Normal()
graph = n.drawPDF()

# Define 2D interval: [x_min, y_min] to [x_max, y_max]
bbox = ot.Interval([-3.0, 0.0], [3.0, 0.5])
graph.setBoundingBox(bbox)
```

#### 2. Via Matplotlib Axes in `otv.View`
```python
import openturns as ot
import openturns.viewer as otv

n = ot.Normal()
graph = n.drawPDF()

view = otv.View(graph)
axes = view.getAxes()
axes[0].set_xlim(-3.0, 3.0)
axes[0].set_ylim(0.0, 0.5)
```

---

### OpenTURNS 1.28 and Later

Starting in version 1.28, `ot.Graph` provides direct setter methods for individual axis limits:

```python
import openturns as ot

n = ot.Normal()
graph = n.drawPDF()

# Set axis limits directly
graph.setXMin(-3.0)
graph.setXMax(3.0)
graph.setYMin(0.0)
graph.setYMax(0.5)
```

### Version-Independent Pattern

```python
import openturns as ot

def set_graph_limits(graph, x_min=None, x_max=None, y_min=None, y_max=None):
    """Set graph limits in a version-compatible manner."""
    if hasattr(graph, "setXMin"):
        if x_min is not None:
            graph.setXMin(x_min)
        if x_max is not None:
            graph.setXMax(x_max)
        if y_min is not None:
            graph.setYMin(y_min)
        if y_max is not None:
            graph.setYMax(y_max)
    else:
        # OpenTURNS <= 1.27: retrieve current bounding box and update
        current_bbox = graph.getBoundingBox()
        lower = list(current_bbox.getLowerBound())
        upper = list(current_bbox.getUpperBound())
        if x_min is not None:
            lower[0] = x_min
        if x_max is not None:
            upper[0] = x_max
        if y_min is not None:
            lower[1] = y_min
        if y_max is not None:
            upper[1] = y_max
        graph.setBoundingBox(ot.Interval(lower, upper))
```
