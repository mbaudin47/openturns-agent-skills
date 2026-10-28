---
name: openturns-python-guide
description: Best practices, essential classes, syntax reference, and workflow guidelines for OpenTURNS in Python. Use when writing Python code with OpenTURNS, working with ot.Sample or ot.Point, defining models, building metamodels, running uncertainty quantification, sensitivity analysis, calibration, or plotting native OpenTURNS graphs.
---

# OpenTURNS Python Guide

Guide to idiomatic and high-performance usage of the OpenTURNS Python library, covering fundamental data structures, model definitions, uncertainty quantification (ABC methodology), metamodeling, calibration, and native visualization.

## When to Use

Use this skill when:

* Writing Python code using the OpenTURNS library (`import openturns as ot`).
* Working with native OpenTURNS data structures (`ot.Point`, `ot.Sample`, `ot.Matrix`, `ot.RegularGrid`).
* Defining analytical or external probabilistic models and random vectors.
* Performing uncertainty propagation, sensitivity analysis (Sobol' indices, SRC), or fitting probability distributions.
* Building surrogate models (Polynomial Chaos Expansion, Kriging / Gaussian Process).
* Running model calibration (Least Squares, Gaussian, Bayesian MCMC).
* Generating native OpenTURNS graphs and contour plots with `openturns.viewer`.

## Core Data Structures and Best Practices

### Data Manipulation and Linear Algebra

* Use native OpenTURNS data structures (`ot.Point`, `ot.Sample`, `ot.Matrix`) rather than converting to NumPy arrays. OpenTURNS native classes interface directly with underlying C++ and BLAS/LAPACK optimizations.
* Use operator overloading directly on `ot.Sample` and `ot.Matrix` (`-` for residuals, `*` for element-wise products or formal matrix multiplication).
* Extract summary statistics directly via built-in methods (`getMin()`, `getMax()`, `computeMean()`, `computeStandardDeviation()`, `computeQuantile()`).

### `ot.Point`

Represents a 1D real vector.

* **Initialization:** `ot.Point(dim, fill_val)` or `ot.Point([1.0, 2.0, 3.0])`.
* **Modification:** `add(value)` appends elements in-place; `resize(newSize)` resizes; `clear()` resets to zero dimension.
* **Vector Operations:** Arithmetic operators (`+`, `-`, scalar `*` and `/`), scalar product `dot(rhs)`.
* **Norms:** Euclidean norm `norm()`, squared `normSquare()`, L1 norm `norm1()`, L-infinity norm `normInf()`, and normalization `normalize()`, `normalizeSquare()`.
* **Inspection:** Dimension via `getDimension()` or `getSize()`; element access via `x[i]` or `at(i)`; slicing via `select(indices)`; search via `index(val)`.
* **Ordering checks:** `isIncreasing()`, `isDecreasing()`, `isNonIncreasing()`, `isNonDecreasing()`, `isMonotonic()`, `isEmpty()`.
* **NumPy conversion:** Convert using `np.array(point)`.

### `ot.Sample`

Represents a collection of real vectors (2D data matrix).

* **Initialization:** `ot.Sample(size, dim)` or `ot.Sample(array_2d)`.
* **Creation helpers:** `ot.Sample.BuildFromPoint(point)` or `ot.Sample.BuildFromDataFrame(df)`.
* **File I/O:** `ot.Sample.ImportFromCSVFile("file.csv", sep)` (uses header for column names), `ot.Sample.ImportFromTextFile(...)`, and export via `sample.exportToCSVFile("file.csv")`.
* **Interoperability:** Convert to DataFrame via `sample.asDataFrame()`, to 1D point via `sample.asPoint()`, or array via `np.array(sample)`.
* **Manipulation:** `getSize()`, `getDimension()`, `add()`, `erase()`, `stack()` (horizontal stacking), `split()`, `clear()`, column selection via `getMarginal(indices)`, row selection via `select(indices)`.
* **Sorting:** `sort()`, `sortInPlace()`, `sortAccordingToAComponent(col)`, `argsort()`, `sortUnique()`, `rank()`.
* **Statistical Methods:**
  * Mean & Quantiles: `computeMean()`, `computeMedian()`, `computeQuantile(p)`, `computeQuantilePerComponent(p)`.
  * Dispersion: `computeVariance()`, `computeStandardDeviation()`, `computeRange()`.
  * Moments: `computeRawMoment(k)`, `computeCentralMoment(k)`, `computeSkewness()`, `computeKurtosis()`.
  * Dependence: `computeLinearCorrelation()`, `computeSpearmanCorrelation()`, `computeKendallTau()`, `computeCovariance()`.
  * Empirical CDF: `computeEmpiricalCDF(point)`.

## Model and Function Definition

* **Symbolic Functions:** Use `ot.SymbolicFunction(["x0", "x1"], ["1 + x0 + x1"])` for analytical models.
* **Linear Combinations:** Use `ot.VectorLinearCombinationFunction` to combine basis functions with coefficients.
* **Python Functions:** Wrap custom Python code with `ot.PythonFunction(nb_inputs, nb_outputs, py_func)` or inherit from `ot.OpenTURNSPythonFunction`. Pass custom functions directly without redundant wrapper lambdas.
* **Caching:** Wrap expensive functions with `ot.MemoizeFunction(g_function)` to cache evaluations and avoid redundant execution.
* **Parametric Models:** Use `ot.ParametricFunction(g_function, calibrated_indices, theta_prior)` to fix or calibrate parameters.

## Uncertainty Quantification (ABC Methodology)

### Step A: Define the Study

* **Distributions:**
  * Standard: `ot.Normal(mu, sigma)`, `ot.Uniform(a, b)`, `ot.Beta(a, b, c, d)`.
  * Parameterization: Use specialized constructors like `ot.LogNormalMuSigma` instead of manually calculating moment transforms.
  * Multivariate: `ot.JointDistribution((dist_x0, dist_x1))` for independent margins, or `ot.ComposedDistribution` with copulas.
* **Random Vectors:**
  * Input vector: `X = ot.RandomVector(input_distribution)`
  * Output vector: `Y = ot.CompositeRandomVector(g_function, X)`
  * Sampling: `X.getSample(sample_size)`
  * Seed control: `ot.RandomGenerator.SetSeed(1)`

### Step B: Quantification of Uncertainty Sources

* **Fitting Distributions:**
  * Parametric: `ot.NormalFactory().build(sample)`, `ot.BetaFactory().build(sample)`.
  * Non-parametric: `ot.HistogramFactory().build(sample)`, `ot.KernelSmoothing().build(sample)`.
* **Goodness-of-Fit & Diagnostics:**
  * Visual test: `ot.VisualTest.DrawQQplot(sample, distribution)`
  * Kolmogorov-Smirnov test: `ot.FittingTest.Kolmogorov(sample, distribution)` (known parameters), `ot.FittingTest.Lilliefors(sample, factory)` (estimated parameters).
  * Selection criteria: `ot.FittingTest.BIC(sample, distribution)`

### Step C: Uncertainty Propagation

* **Taylor Expansion:** `ot.TaylorExpansionMoments(output_random_vector)` for 1st/2nd order mean and variance estimates.
* **Monte Carlo / Expectation:** `ot.ExpectationSimulationAlgorithm(output_random_vector)`
* **Event & Probability Estimation:**
  * Empirical CDF: `sample.computeEmpiricalCDF(s, True)`
  * Threshold Event: `event = ot.ThresholdEvent(output_random_vector, ot.Greater(), s)`
  * Probability Simulation: `ot.ProbabilitySimulationAlgorithm(event, experiment)`

### Step C': Sensitivity Analysis

* **Linear Regression & SRC:** `ot.LinearLeastSquares(input_sample, output_sample)`, `ot.CorrelationAnalysis_SignedSRC(input_sample, output_sample)`.
* **Sobol' Indices:**
  * Experiment design: `ot.SobolIndicesExperiment(distribution, sample_size)`
  * Algorithm: `ot.SaltelliSensitivityAlgorithm()`
  * Plotting: `ot.SobolIndicesAlgorithm.DrawCorrelationCoefficients(src_indices, inputNames, "SRC coefficients")`

### Step B': Calibration

* **Linear Least Squares:** `ot.LinearLeastSquaresCalibration(parametric_g, input_sample, output_sample, theta_prior, "SVD")`
* **Non-Linear Least Squares:** `ot.NonLinearLeastSquaresCalibration(parametric_g, input_sample, output_sample, theta_prior)`
* **Gaussian Calibration:** `ot.GaussianLinearCalibration` and `ot.GaussianNonLinearCalibration`.
* **Bayesian Calibration:** `ot.RandomWalkMetropolisHastings(prior, conditional, model, input_sample, output_sample, initialState, proposal)`

## Metamodeling and Design of Experiments

### Surrogate Models

* **Polynomial Chaos Expansion (PCE):**
  * Basis construction: `ot.OrthogonalProductPolynomialFactory(distribution_collection)`
  * Construction from data: `ot.FunctionalChaosAlgorithm(input_sample, output_sample)`
  * Construction from distribution: `ot.FunctionalChaosAlgorithm(input_sample, output_sample, distribution, adaptive_strategy, projection_strategy)`
  * Sobol' indices from chaos: `ot.FunctionalChaosSobolIndices(functional_chaos_result)`
  * Chaos random vector: `ot.FunctionalChaosRandomVector(functional_chaos_result)`
* **Kriging (Gaussian Process):**
  * Covariance models: `ot.SquaredExponential([1.0]*dim, [1.0])`, `ot.MaternModel([1.0]*dim, 2.5)`
  * Fitting: `otexp.GaussianProcessFitter(input_sample, output_sample, covarianceModel, basis)`
  * Prediction & Process: `ot.KrigingRandomVector(result, input_sample)`, `ot.ConditionedGaussianProcess(kriging_result, mesh)`
* **Validation:** `ot.MetaModelValidation(output_test, metamodel(input_test))` and `drawValidation()`.

### Design of Experiments (DOE)

* **Sampling Designs:** `ot.MonteCarloExperiment`, `ot.LHSExperiment`, `ot.SimulatedAnnealingLHS`, `ot.SobolSequence`, `ot.LowDiscrepancyExperiment`.
* **Visualization:** `import openturns.viewer as otv`; `otv.PlotDesign(sample, bounds)`.

## Visualization and Native Graphing

OpenTURNS includes native graphing capabilities using `ot.Graph` and `openturns.viewer` (`otv`).

### Native Graph Construction

* **Basic Graph:** `graph = ot.Graph(title, x_title, y_title, show_axes_bool)`
* **Drawables:** `ot.Curve(sample_x, sample_y)`, `ot.Cloud(sample_x, sample_y)`
* **Visual Tests:** `ot.VisualTest.DrawPairs(sample)`, `ot.VisualTest.DrawPairsMarginals(sample, distribution)`, `ot.VisualTest.DrawParallelCoordinates(...)`
* **Color and Legend Customization:**
  * Palette: `graph.setColors(ot.Drawable().BuildDefaultPalette(nb_graphs))`
  * Legend placement: `graph.setLegendCorner((1.0, 1.0))`, `graph.setLegendPosition("upper left")`
* **Rendering with `otv.View`:**
  * Display: `view = otv.View(graph, figure_kw={"figsize": (4.0, 3.0)})`
  * Legend fine-tuning: `otv.View(graph, legend_kw={"bbox_to_anchor": (1.0, 1.0), "loc": "upper left"})`
  * Save figure: `view.getFigure().savefig("filename.pdf", bbox_inches="tight")`

### 2D Contour Plots

* **Generation:** Call `draw()` on an `ot.Function` with 2 inputs.
* **Extraction:** Retrieve contour drawable via `graph.getDrawable(0)` and access methods through `drawable.getImplementation()`.
* **Levels Configuration:**
  * Global setting: `ot.ResourceMap.SetAsUnsignedInteger("Contour-DefaultLevelsNumber", n)`
  * Local setting: `contour_impl.buildDefaultLevels()`, query via `contour_impl.getLevels()`
* **Steep Gradients:** Apply rank-based normalization for improved color variation: `contour_impl.setColorMapNorm("rank")`.
* **Filled Areas:** Enable filled contour regions with `contour_impl.setIsFilled(True)`.
* **Coloring:** Set monochrome with `contour_impl.setColor("blue")` or pass custom palettes to `contour_kw` in `otv.View`.

## Pitfalls and Gotchas

* **Avoid Unnecessary NumPy Conversions:** Converting `ot.Sample` or `ot.Point` back and forth with `np.array` discards C++ optimized linear algebra methods.
* **Use Correct Parameterization Constructors:** Avoid manually solving moment equations for distributions when built-in parameterization classes exist (e.g. `ot.LogNormalMuSigma`).
* **Use `Sample.ImportFromCSVFile` for Datasets:** When loading structured tables into OpenTURNS, use `ot.Sample.ImportFromCSVFile()` to preserve column headers.
* **Legend Formatting:** Use `setLegendCorner()` or `legend_kw` in `otv.View` to prevent legends from obscuring plot data.
