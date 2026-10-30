"""
Michaël Baudin, 2025
Benchmark the elapsed time of solving a linear least squares problem using OpenTURNS.
Uses the Ishigami function.
Compute its polynomial chaos expansion.
"""

# %%
import openturns as ot
import time
from openturns.usecases import ishigami_function
import openturns.viewer as otv


# %%
def performLinearLeastSquares(
    sampleSize, basisDimension=10, leastSquaresMethodName="SVD"
):
    """
    Solve a linear least squares problem.

    Parameters
    ----------
    sampleSize : int
        Number of samples to generate.

    Returns
    -------
    float
        Elapsed time in seconds to solve the least squares problem.
    """
    im = ishigami_function.IshigamiModel()
    inputTrain = im.inputDistribution.getSample(sampleSize)
    outputTrain = im.model(inputTrain)

    # Build the design matrix
    outputDimension = outputTrain.getDimension()
    multivariateBasis = ot.OrthogonalProductPolynomialFactory([im.X1, im.X2, im.X3])
    standard_distribution = multivariateBasis.getMeasure()
    transformation = ot.DistributionTransformation(
        im.inputDistribution, standard_distribution
    )
    standard_input = transformation(inputTrain)

    # Create the basis functions
    indices = ot.Indices(basisDimension)
    indices.fill()
    functions = [multivariateBasis.build(i) for i in indices]
    designProxy = ot.DesignProxy(standard_input, functions)
    leastSquaresMethod = ot.LeastSquaresMethod.Build(
        leastSquaresMethodName, designProxy, indices
    )

    # Solve the least squares problem
    start_time = time.time()
    coefficients = ot.Sample(basisDimension, outputDimension)
    for j in range(outputDimension):
        coeffsJ = leastSquaresMethod.solve(outputTrain.getMarginal(j).asPoint())
        for i in range(basisDimension):
            coefficients[i, j] = coeffsJ[i]
    end_time = time.time()

    elapsed_time = end_time - start_time
    return elapsed_time


# %%
def benchmarkLeastSquares(
    basisDimension=10,
    leastSquaresMethodName="SVD",
    maximum_time=4.0,
    sample_size_init=2,
    maximum_number_of_iterations=100,
    sample_size_factor=2.0,
    verbose=False,
):
    """
    Benchmark linear least squares problem with an increasing sample size.

    Parameters
    ----------
    maximum_time : float
        The maximum value of the elapsed time.
    sample_size_init : int
        The initial sample size.
    maximum_number_of_iterations : int
        The maximum number of iterations of increasing sample sizes.
    sample_size_factor : float, > 0
        The factor used to increase the sample size.
    verbose : bool
        If True, print intermediate messages.

    Returns
    -------
    sample_size_list : list(int)
        The list of sample sizes.
    elapsed_time_list : list(float)
        The list of elapsed times (in seconds).
    """
    sample_size_list = []
    elapsed_time_list = []
    sample_size = sample_size_init
    for i in range(maximum_number_of_iterations):
        elapsed_time = performLinearLeastSquares(
            sample_size,
            basisDimension=basisDimension,
            leastSquaresMethodName=leastSquaresMethodName,
        )
        elapsed_time_list.append(elapsed_time)
        sample_size_list.append(sample_size)
        if verbose:
            print(f"n={sample_size}, elapsed={elapsed_time:.2f} (s)")

        if elapsed_time > maximum_time:
            break
        sample_size = int(sample_size * sample_size_factor)

    return sample_size_list, elapsed_time_list


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
    cloud = ot.Cloud(x_data, elapsed_time_list)
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
def plotBenchmark(sample_size_list, elapsed_time_list, color=None, legend="", 
                  point_style="circle", line_style="solid"):
    """
    Plot the benchmark results.

    Parameters
    ----------
    sample_size_list : list(int)
        The list of sample sizes.
    elapsed_time_list : list(float)
        The list of elapsed times (in seconds).
    color : str, optional
        Color of the plot.
    legend : str, optional
        Legend label for the plot.
    point_style : str, optional
        Style of the points in the plot (default is "circle").
    line_style : str, optional
        Style of the line in the plot (default is "solid").

    Returns
    -------
    graph : ot.Graph
        The OpenTURNS graph object.
    """
    # Plot
    graph = ot.Graph(
        "Linear Least Squares benchmark",
        "Sample size",
        "Elapsed time (s)",
        True,
    )
    cloud = plotCloudAndCurve(
        sample_size_list,
        elapsed_time_list,
        point_style=point_style,
        line_style=line_style,
        legend=legend,
        color=color,
    )
    graph.add(cloud)
    graph.setLegendPosition("upper left")
    graph.setLegendCorner((1.0, 1.0))
    graph.setLogScale(ot.GraphImplementation.LOGXY)
    return graph


# %%
maximum_time = 1.0
maximum_number_of_iterations = 100
sample_size_factor = 2.0
verbose = True
method_name_list = ["QR", "SVD", "Cholesky"]
point_style_list = ["circle", "+", "v"]
basis_dimension_list = [10, 50, 100, 200, 400]
for j in range(len(basis_dimension_list)):
    basisDimension = basis_dimension_list[j]
    print(f"Basis dimension = {basisDimension}")
    sample_size_init = 2 * basisDimension
    graph = ot.Graph(
        f"Ishigami, LLS, P={basisDimension}", "Sample size", "Elapsed time (s)", True
    )
    graph.setLogScale(ot.GraphImplementation.LOGXY)
    graph.setLegendPosition("upper left")
    graph.setLegendCorner((1.0, 1.0))
    palette = ot.Drawable.BuildDefaultPalette(len(method_name_list))
    for i in range(len(method_name_list)):
        leastSquaresMethodName = method_name_list[i]
        print(f"{leastSquaresMethodName}")
        sample_size_list, elapsed_time_list = benchmarkLeastSquares(
            basisDimension=basisDimension,
            leastSquaresMethodName=leastSquaresMethodName,
            maximum_time=maximum_time,
            sample_size_init=sample_size_init,
            maximum_number_of_iterations=maximum_number_of_iterations,
            sample_size_factor=sample_size_factor,
            verbose=verbose,
        )
        curve = plotBenchmark(
            sample_size_list,
            elapsed_time_list,
            legend=leastSquaresMethodName,
            color=palette[i],
            point_style=point_style_list[i]
        )
        graph.add(curve)
    view = otv.View(graph, figure_kw={"figsize": (5.0, 3.0)})

# %%
