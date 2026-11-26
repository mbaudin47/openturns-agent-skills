---
name: openturns-splitters
description: Use OpenTURNS KFoldSplitter and LeaveOneOutSplitter classes for cross-validation and sample partitioning into training and test subsets.
---

# Cross-Validation with KFoldSplitter and LeaveOneOutSplitter in OpenTURNS

This guide describes how to use the `KFoldSplitter` and `LeaveOneOutSplitter` classes from the `openturns` module to partition samples (`ot.Sample`) into training and test subsets for cross-validation.

## General Principle

Classes inheriting from the OpenTURNS splitting mechanism act as iterators. At each iteration in a Python loop, the iterator yields a tuple `(indicesTrain, indicesTest)` as two `ot.Indices` objects. These objects allow direct sample slicing on an `ot.Sample` using bracket notation `sample[indices]`.

---

## 1. KFoldSplitter

The `ot.KFoldSplitter` class partitions a dataset of size $N$ into $K$ folds. Each fold is used once as a test set, while the remaining $K-1$ folds constitute the training set.

### Syntax and Main Methods
* **Constructor:** `ot.KFoldSplitter(N, k)`
  * `N` (int): Total size of the index set (typically `sample.getSize()`).
  * `k` (int): Number of folds.
* **Methods:**
  * `setRandomize(randomize)` (bool): Enable or disable random shuffling of folds.
  * `getSize()`: Returns the number of splits generated (equal to $K$).
  * `getN()`: Returns the sample size $N$.

### Basic Example

```python
import openturns as ot

# Generate a sample
sample = ot.Normal().getSample(100)
k = 5

splitter = ot.KFoldSplitter(sample.getSize(), k)

for indicesTrain, indicesTest in splitter:
    sampleTrain = sample[indicesTrain]
    sampleTest = sample[indicesTest]
    # Train and evaluate models on respective subsets
```

### Computing $R^2$ Score via K-Fold Cross-Validation

```python
import openturns as ot

def compute_r2_kfold(x_sample, y_sample, model_builder_fn, k=5):
    """
    Compute mean R2 score via K-Fold cross-validation.

    Parameters
    ----------
    x_sample : ot.Sample
        Input variables.
    y_sample : ot.Sample
        Output variables.
    model_builder_fn : callable
        Function taking (x_train, y_train) and returning an ot.Function (surrogate model).
    k : int
        Number of folds.

    Returns
    -------
    ot.Point
        Mean R2 score across all output dimensions.
    """
    n = x_sample.getSize()
    splitter = ot.KFoldSplitter(n, k)
    r2_scores = ot.Sample(0, y_sample.getDimension())

    for indicesTrain, indicesTest in splitter:
        x_train, x_test = x_sample[indicesTrain], x_sample[indicesTest]
        y_train, y_test = y_sample[indicesTrain], y_sample[indicesTest]

        metamodel = model_builder_fn(x_train, y_train)
        predictions = metamodel(x_test)

        val = ot.MetaModelValidation(y_test, predictions)
        r2_scores.add(val.computeR2Score())

    return r2_scores.computeMean()
```

---

## 2. LeaveOneOutSplitter

The `ot.LeaveOneOutSplitter` class generates $N$ splits. At each step, a single observation is held out for testing, while the remaining $N-1$ observations are used for training.

### Syntax and Main Methods
* **Constructor:** `ot.LeaveOneOutSplitter(N)`
  * `N` (int): Size of the dataset (`sample.getSize()`).
* **Methods:**
  * `getSize()`: Returns the number of generated splits (equal to $N$).
  * `getN()`: Returns the dataset size $N$.

### Basic Example

```python
import openturns as ot

sample = ot.Normal().getSample(20)
splitter = ot.LeaveOneOutSplitter(sample.getSize())

for indicesTrain, indicesTest in splitter:
    sampleTrain = sample[indicesTrain]
    sampleTest = sample[indicesTest]  # Sample of size 1
```

### Computing Leave-One-Out Mean Squared Error (LOO MSE)

```python
import openturns as ot

def compute_mse_loo(x_sample, y_sample, model_builder_fn):
    """
    Compute Leave-One-Out Mean Squared Error (LOO MSE).
    """
    n = x_sample.getSize()
    splitter = ot.LeaveOneOutSplitter(n)
    residuals = ot.Point(n)

    for j, (indicesTrain, indicesTest) in enumerate(splitter):
        x_train, x_test = x_sample[indicesTrain], x_sample[indicesTest]
        y_train, y_test = y_sample[indicesTrain], y_sample[indicesTest]

        metamodel = model_builder_fn(x_train, y_train)
        pred = metamodel(x_test)
        residuals[j] = y_test[0, 0] - pred[0, 0]

    return residuals.normSquare() / n
```

---

## Usage Guidelines & Best Practices

1. **Reproducibility:** For `KFoldSplitter`, random fold shuffling depends on the `KFoldSplitter-Randomize` key in `ot.ResourceMap`. Set the global random seed via `ot.RandomGenerator.SetSeed(...)` to guarantee repeatable fold splits.
2. **Direct Indexing:** Subsamples are extracted directly using bracket notation `sample[indices]` on `ot.Indices`, with no need for conversion to Python lists.
3. **Analytical Shortcut for Least Squares:** When the model is a linear or polynomial chaos regression, repetitive numerical evaluations via `LeaveOneOutSplitter` can be evaluated analytically in $O(1)$ time using the hat matrix diagonal (`lsqMethod.getHDiag()` on an `ot.QRMethod` object).
