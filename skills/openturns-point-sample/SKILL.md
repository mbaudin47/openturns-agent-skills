---
name: openturns-point-sample
description: Manipulate OpenTURNS Point and Sample classes in Python. Use when creating, indexing, slicing, filtering, converting between Python/NumPy objects and OpenTURNS Point or Sample, or resolving 1D sample array ambiguity errors.
---

# OpenTURNS Point and Sample Classes

Guide and best practices for creating, manipulating, indexing, slicing, and converting OpenTURNS `Point` and `Sample` objects in Python.

## When to Use
- Creating multidimensional points (`ot.Point`) or multivariate samples (`ot.Sample`).
- Extracting or setting rows and columns in a `Sample`.
- Selecting sub-samples based on explicit indices or boolean condition filters.
- Converting between Python lists, NumPy arrays, and OpenTURNS objects.
- Fixing `InvalidArgumentException` / `TypeError` when constructing a 1D `Sample` from a 1D array.

## Core Concepts & Operations

### 1. Point (`ot.Point`)
Represents a real vector in $\mathbb{R}^d$. Initialized with zeros by default.

- **Initialization**: `p = ot.Point(dimension)` or `p = ot.Point([1.0, 2.0, 3.0])`
- **Indexing**: Zero-based indexing `p[1]` (reads index 1), `p[1] = 2` (updates index 1).
- **Dimension**: `p.getDimension()` or `p.getSize()`.
- **List comprehension**: `[i * i for i in p]`.

### 2. Sample (`ot.Sample`)
Represents a multivariate sample with $n$ rows (sample size) and $d$ columns (dimension).

- **Initialization**: `sample = ot.Sample(size, dimension)` or from nested lists `ot.Sample([[0, 1], [2, 3]])`.
- **Size and Dimension**: `sample.getSize()` ($n$), `sample.getDimension()` ($d$).
- **Element Access**: `sample[row_idx, col_idx] = value` (e.g., `sample[3, 2] = 32`).

### 3. Slicing and Extracting Rows/Columns
- **Extracting a row**: `row = sample[3, :]` returns an `ot.Point`.
- **Extracting a column**: `col = sample[:, 2]` returns a 1-column `ot.Sample`.
- **Extracting multiple marginals (columns)**: `sample.getMarginal([0, 2])`.
- **Setting a row**: `sample[2, :] = [8.0, 10.0]` (must be an `ot.Point` or list of floats matching dimension).
- **Setting a column**: `sample[:, 1] = ot.Sample([[3.0], [5.0], [7.0]])`.
- **Setting a column from a 1D list**: Use `sample[:, 1] = ot.Sample.BuildFromPoint([3.0, 5.0, 7.0])`.

### 4. Selecting Specific Points / Filtering
- **Single point by index**: `sample[0]` returns an `ot.Point`.
- **Multiple points by index list**: `sample[[1, 3]]` or `sample.select([1, 3])`.
- **Filtering by condition**: `sample[[i for i in range(sample.getSize()) if sample[i, 2] < 0.0]]` or `sample.select(...)`.
- **Sub-block slicing**: `sample[0:2, 4:6]` or `sample[0:2, [4, 5]]`.

### 5. Interoperability with NumPy
- **Sample to NumPy**: `arr = np.array(sample)` (returns `np.ndarray`).
- **2D NumPy to Sample**: `sample = ot.Sample(array_2d)`.
- **1D NumPy / List to 1D Sample**:
  - Direct construction `ot.Sample(1d_array)` raises `InvalidArgumentException: Invalid array dimension: 1`.
  - **Solution**: Use `ot.Sample.BuildFromPoint(u)` or `ot.Sample([[ui] for ui in u])`.

## Gotchas & Pitfalls
- **Row vs. Column Type**: Slicing a single row (`sample[i, :]`) returns an `ot.Point`, whereas slicing a single column (`sample[:, j]`) returns an `ot.Sample`.
- **1D Array Constructor Ambiguity**: Passing a 1D array or list to `ot.Sample(array)` fails because OpenTURNS cannot guess whether it represents 1 sample in $d$ dimensions or $n$ samples in 1 dimension. Always use `ot.Sample.BuildFromPoint(list)` for $n \times 1$ samples.
- **Zero-based Indexing**: All indices for points and samples start at 0.

