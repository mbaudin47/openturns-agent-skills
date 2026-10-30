"""
Michaël Baudin, 2025
Benchmark the elapsed time of the cross-validation of a PCE.

Compare two methods for cross-validation:
- leave-one-out,
- K-fold.

Compare two methods for performing the CV:
- classical cross-validation, using MetaModelValidation,
- analytical cross-validation, using FunctionalChaosValidation.

Reference
---------
https://github.com/openturns/openturns/pull/2330

"""

# %%
import openturns as ot
import openturns.viewer as otv
import time
import openturns.experimental as otexp
from openturns.usecases import ishigami_function


# %%
def performClassicalCrossValidation(
    sampleSize, splitter, basisDimension=10, sparse=False
):
    """
    Perform classical cross-validation using chaos expansion.

    Parameters
    ----------
    sampleSize : int
        Number of samples to generate.
    splitter : SplitterImplementation
        The cross-validation splitter
    basisDimension : int, optional
        Dimension of the polynomial basis (default is 10).
    sparse : bool, optional
        Whether to use sparse least squares (default is False).

    Returns
    -------
    mse_score : float
        Mean MSE score from cross-validation.
    """
    im = ishigami_function.IshigamiModel()
    inputTrain = im.inputDistribution.getSample(sampleSize)
    outputTrain = im.model(inputTrain)
    multivariateBasis = ot.OrthogonalProductPolynomialFactory([im.X1, im.X2, im.X3])
    if sparse:
        # Use LeastSquaresMetaModelSelection-DecompositionMethod to
        # select QR, SVD or Cholesky
        selectionAlgorithm = ot.LeastSquaresMetaModelSelectionFactory()
    else:
        # Compute Gram matrix, always
        selectionAlgorithm = ot.PenalizedLeastSquaresAlgorithmFactory()
    projectionStrategy = ot.LeastSquaresStrategy(selectionAlgorithm)
    adaptiveStrategy = ot.FixedStrategy(multivariateBasis, basisDimension)
    dimension_output = outputTrain.getDimension()
    mse_score_sample = ot.Sample(0, dimension_output)
    index = 0
    for indices_train, indices_test in splitter:
        X_train, X_test = inputTrain[indices_train], inputTrain[indices_test]
        Y_train, Y_test = outputTrain[indices_train], outputTrain[indices_test]
        chaosAlgo = ot.FunctionalChaosAlgorithm(
            X_train,
            Y_train,
            im.inputDistribution,
            adaptiveStrategy,
            projectionStrategy,
        )
        chaosAlgo.run()
        chaosResult = chaosAlgo.getResult()
        metamodel = chaosResult.getMetaModel()
        if len(indices_test) == 1:
            diff = Y_test - metamodel(X_test)
            mse_local = [v**2 for v in diff.asPoint()]  # Loop over output dim.
        else:
            val = ot.MetaModelValidation(Y_test, metamodel(X_test))
            mse_local = val.computeMeanSquaredError()
        mse_score_sample.add([mse_local])
        index += 1
    mse_score = mse_score_sample.computeMean()
    return mse_score


# %%
def performClassicalKFoldCV(
    sampleSize, numberOfFolds=10, basisDimension=10, sparse=False
):
    """
    Perform k-fold cross-validation using classical chaos expansion.

    Parameters
    ----------
    sampleSize : int
        Number of samples to generate.
    numberOfFolds : int, optional
        Number of folds for cross-validation (default is 10).
    basisDimension : int, optional
        Dimension of the polynomial basis (default is 10).
    sparse : bool, optional
        Whether to use sparse least squares (default is False).

    Returns
    -------
    mse_score : float
        Mean MSE from cross-validation.
    """
    splitter = ot.KFoldSplitter(sampleSize, numberOfFolds)
    mse_score = performClassicalCrossValidation(
        sampleSize, splitter, basisDimension, sparse
    )
    return mse_score


# %%
def performClassicalLOOCV(sampleSize, basisDimension=10, sparse=False):
    """
    Perform leave-one-out cross-validation using classical chaos expansion.

    Parameters
    ----------
    sampleSize : int
        Number of samples to generate.
    basisDimension : int, optional
        Dimension of the polynomial basis (default is 10).
    sparse : bool, optional
        Whether to use sparse least squares (default is False).

    Returns
    -------
    mse_score : float
        Mean MSE from cross-validation.
    """
    splitter = ot.LeaveOneOutSplitter(sampleSize)
    mse_score = performClassicalCrossValidation(
        sampleSize, splitter, basisDimension, sparse
    )
    return mse_score


# %%
def performAnalyticalCrossValidation(
    sampleSize, splitter, basisDimension=10, sparse=False
):
    """
    Perform analytical cross-validation using chaos expansion.

    Parameters
    ----------
    sampleSize : int
        Number of samples to generate.
    splitter : SplitterImplementation
        The cross-validation splitter
    basisDimension : int, optional
        Dimension of the polynomial basis (default is 10).
    sparse : bool, optional
        Whether to use sparse least squares (default is False).

    Returns
    -------
    mse_score : float
        Mean MSE from cross-validation.
    """
    im = ishigami_function.IshigamiModel()
    inputTrain = im.inputDistribution.getSample(sampleSize)
    outputTrain = im.model(inputTrain)
    multivariateBasis = ot.OrthogonalProductPolynomialFactory([im.X1, im.X2, im.X3])
    if sparse:
        # Use LeastSquaresMetaModelSelection-DecompositionMethod to
        # select QR, SVD or Cholesky
        selectionAlgorithm = ot.LeastSquaresMetaModelSelectionFactory()
    else:
        # Compute Gram matrix, always
        selectionAlgorithm = ot.PenalizedLeastSquaresAlgorithmFactory()
    projectionStrategy = ot.LeastSquaresStrategy(selectionAlgorithm)
    adaptiveStrategy = ot.FixedStrategy(multivariateBasis, basisDimension)
    chaosAlgo = ot.FunctionalChaosAlgorithm(
        inputTrain,
        outputTrain,
        im.inputDistribution,
        adaptiveStrategy,
        projectionStrategy,
    )
    chaosAlgo.run()
    chaosResult = chaosAlgo.getResult()
    # Cross-validation
    validation = otexp.FunctionalChaosValidation(chaosResult, splitter)
    mse_score = validation.computeMeanSquaredError()
    return mse_score


# %%
def performAnalyticalKFoldCV(
    sampleSize, numberOfFolds=10, basisDimension=10, sparse=False
):
    """
    Perform k-fold cross-validation using analytical chaos expansion.

    Parameters
    ----------
    sampleSize : int
        Number of samples to generate.
    numberOfFolds : int, optional
        Number of folds for cross-validation (default is 10).
    basisDimension : int, optional
        Dimension of the polynomial basis (default is 10).
    sparse : bool, optional
        Whether to use sparse least squares (default is False).

    Returns
    -------
    mse_score : float
        Mean MSE from cross-validation.
    """
    splitter = ot.KFoldSplitter(sampleSize, numberOfFolds)
    mse_score = performAnalyticalCrossValidation(
        sampleSize, splitter, basisDimension, sparse
    )
    return mse_score


# %%
def performAnalyticalLOOCV(sampleSize, basisDimension=10, sparse=False):
    """
    Perform leave-one-out cross-validation using analytical chaos expansion.

    Parameters
    ----------
    sampleSize : int
        Number of samples to generate.
    basisDimension : int, optional
        Dimension of the polynomial basis (default is 10).
    sparse : bool, optional
        Whether to use sparse least squares (default is False).

    Returns
    -------
    mse_score : float
        Mean MSE from cross-validation.
    """
    splitter = ot.LeaveOneOutSplitter(sampleSize)
    mse_score = performAnalyticalCrossValidation(
        sampleSize, splitter, basisDimension, sparse
    )
    return mse_score


# %%
# Check on a single MSE score
sampleSize = 500
mse_score = performClassicalLOOCV(sampleSize)
print(f"Classical LOO CV = {mse_score}")
mse_score = performAnalyticalLOOCV(sampleSize)
print(f"Classical LOO CV = {mse_score}")
mse_score = performClassicalKFoldCV(sampleSize)
print(f"Classical KFold CV = {mse_score}")
mse_score = performAnalyticalKFoldCV(sampleSize)
print(f"Analytical KFold CV = {mse_score}")


# %%
def benchmark_CV(
    is_analytical_cv=True,
    is_kfold=True,
    maximum_time=4.0,
    sample_size_init=2,
    maximum_number_of_iterations=100,
    sample_size_factor=2.0,
    numberOfFolds=10,
    basisDimension=10,
    verbose=False,
):
    """
    Benchmark KFold CV value with an increasing sample size

    Parameters
    ----------
    is_analytical_cv : bool
        Set to True to benchmark analytical CV.
        Set to False to benchmark classical CV.
    is_kfold : bool
        Set to True to benchmark K-Fold.
        Set to False to benchmark leave-one-out.
    maximum_time : float
        The maximum value of the elapsed time.
    sample_size_init : int
        The initial sample size
    maximum_number_of_iterations : int
        The maximum number of iterations of increasing sample sizes
    sample_size_factor : float, > 0
        The factor used to increased the sample size
    verbose : bool
        If True, print intermediate messages

    Returns
    -------
    sample_size_list : list(int)
        The list of sample sizes
    elapsed_time_list : list(float)
        The list of elapsed time (in seconds)
    """

    sample_size_list = []
    elapsed_time_list = []
    sample_size = sample_size_init
    for i in range(maximum_number_of_iterations):
        start_time = time.time()
        if is_kfold:
            if is_analytical_cv:
                _ = performAnalyticalKFoldCV(
                    sample_size, basisDimension=basisDimension, numberOfFolds=numberOfFolds
                )
            else:
                _ = performClassicalKFoldCV(
                    sample_size, basisDimension=basisDimension, numberOfFolds=numberOfFolds
                )
        else:
            if is_analytical_cv:
                _ = performAnalyticalLOOCV(
                    sample_size, basisDimension=basisDimension, 
                )
            else:
                _ = performClassicalLOOCV(
                    sample_size, basisDimension=basisDimension, 
                )
        stop_time = time.time()
        elapsed_time = stop_time - start_time
        elapsed_time_list.append(elapsed_time)
        sample_size_list.append(sample_size)
        if verbose:
            print(f"n={sample_size}, " f"elapsed={elapsed_time:.2f} (s)")

        if elapsed_time > maximum_time:
            break
        sample_size = int(sample_size * sample_size_factor)

    return (sample_size_list, elapsed_time_list)


# %%
def plotCloudAndCurve(
    x_data, y_data, color=None, point_style="circle", line_style="solid", legend=""
):
    """
    Plot a cloud of points and a curve.

    Parameters
    ----------
    x_data : list(int) or list(float)
        The list of x-coordinates.
    y_data : list(int) or list(float)
        The list of y-coordinates.
    color : str, optional
        The color of the points and curve (default is None).
    point_style : str, optional
        The style of the points (default is "circle").
    line_style : str, optional
        The style of the curve (default is "solid").
    legend : str, optional
        The legend label (default is "").

    Returns
    -------
    graph : ot.Graph
        The OpenTURNS graph containing the cloud and curve.
    """
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


# %%
def performBenchmark(
    totalDegree=8,
    numberOfFolds=10,
    maximum_time=1.0,
):
    # Initialize
    sample_size_init = 5 * numberOfFolds
    # Compute basis dimension
    im = ishigami_function.IshigamiModel()
    multivariateBasis = ot.OrthogonalProductPolynomialFactory([im.X1, im.X2, im.X3])
    enumerateFunction = multivariateBasis.getEnumerateFunction()
    basisDimension = enumerateFunction.getBasisSizeFromTotalDegree(totalDegree)
    print(f"Degree = {totalDegree}, basisDimension = {basisDimension}")

    # Classical LOO
    im = ishigami_function.IshigamiModel()
    print("Classical LOO")
    liste_samplesize_classical_loo, elapse_time_classical_loo = benchmark_CV(
        is_analytical_cv=False,
        is_kfold=False,
        sample_size_init=sample_size_init,
        maximum_time=maximum_time,
        verbose=True,
    )

    # Analytical LOO
    print("Analytical LOO")
    liste_samplesize_analytical_loo, elapse_time_analytical_loo = (
        benchmark_CV(
            is_analytical_cv=True,
            is_kfold=False,
            sample_size_init=sample_size_init,
            maximum_time=maximum_time,
            verbose=True,
        )
    )

    # Classical K-Fold
    im = ishigami_function.IshigamiModel()
    print("Classical K-Fold")
    liste_samplesize_classical_kfold, elapse_time_classical_kfold = benchmark_CV(
        is_analytical_cv=False,
        sample_size_init=sample_size_init,
        maximum_time=maximum_time,
        verbose=True,
    )

    # Analytical K-Fold
    print("Analytical K-Fold")
    liste_samplesize_analytical_kfold, elapse_time_analytical_kfold = (
        benchmark_CV(
            is_analytical_cv=True,
            sample_size_init=sample_size_init,
            maximum_time=maximum_time,
            verbose=True,
        )
    )

    # Plot
    graph = ot.Graph(
        "Ishigami"
        f", P+1={basisDimension} coeff. (deg={totalDegree})"
        f", k={numberOfFolds}",
        "Sample size",
        "Elapsed time (s)",
        True,
    )
    palette = ot.Drawable.BuildDefaultPalette(4)
    cloud = plotCloudAndCurve(
        liste_samplesize_classical_loo,
        elapse_time_classical_loo,
        color=palette[0],
        point_style="+",
        line_style="longdash",
        legend="Classical LOO",
    )
    graph.add(cloud)
    cloud = plotCloudAndCurve(
        liste_samplesize_analytical_loo,
        elapse_time_analytical_loo,
        color=palette[1],
        point_style="^",
        line_style="dotdash",
        legend="Analytical LOO",
    )
    graph.add(cloud)
    cloud = plotCloudAndCurve(
        liste_samplesize_classical_kfold,
        elapse_time_classical_kfold,
        color=palette[2],
        point_style="circle",
        line_style="solid",
        legend="Classical K-Fold",
    )
    graph.add(cloud)
    cloud = plotCloudAndCurve(
        liste_samplesize_analytical_kfold,
        elapse_time_analytical_kfold,
        color=palette[3],
        point_style="v",
        line_style="dashed",
        legend="Analytical K-Fold",
    )
    graph.add(cloud)
    graph.setLegendPosition("upper left")
    graph.setLegendCorner((1.0, 1.0))
    graph.setLogScale(ot.GraphImplementation.LOGXY)
    view = otv.View(graph, figure_kw={"figsize": (5.0, 3.0)})
    return view


# %%
maximum_time = 2.0

# %%
performBenchmark(totalDegree=2, numberOfFolds=10, maximum_time=maximum_time)

# %%
performBenchmark(totalDegree=8, numberOfFolds=10, maximum_time=maximum_time)

# %%
performBenchmark(totalDegree=14, numberOfFolds=10, maximum_time=maximum_time)

# %%
performBenchmark(totalDegree=8, numberOfFolds=5, maximum_time=maximum_time)

# %%
performBenchmark(totalDegree=8, numberOfFolds=10, maximum_time=maximum_time)

# %%
performBenchmark(totalDegree=8, numberOfFolds=20, maximum_time=maximum_time)

# %%
