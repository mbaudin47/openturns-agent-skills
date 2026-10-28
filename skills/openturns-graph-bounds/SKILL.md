---
name: openturns-graph-bounds
description: Configure x and y axis limits, bounds, and bounding boxes on OpenTURNS Graph objects. Use when setting graph min/max limits or bounding boxes in OpenTURNS.
---

# OpenTURNS Graph Bounds Configuration

Configure axis limits and bounding boxes on OpenTURNS `Graph` objects efficiently depending on the OpenTURNS version.

## When to Use

- Setting x or y axis range limits on OpenTURNS graph objects.
- Adjusting graph bounding boxes when `setBoundingBox()` is required.
- Writing version-compatible Python code for OpenTURNS graphics.

## Usage Guidelines

### OpenTURNS 1.28 and Later

Starting in version 1.28, `ot.Graph` provides direct setter methods for individual axis limits:

```python
import openturns as ot

n = ot.Normal()
graph = n.drawPDF()

# Set axis limits directly
graph.setXMin(-1.0)
graph.setXMax(2.0)
graph.setYMin(-3.0)
graph.setYMax(1.0)
```

