"""Compute Polynomial Chaos Expansion (PCE) coefficients via least squares.

Fit a PCE meta-model using linear regression on a training sample without
relying on ot.FunctionalChaosAlgorithm. Map input samples onto standard
measure, build the orthogonal basis up to totalDegree, and estimate
coefficients with ot.LeastSquaresMethod.

Parameters
----------
model : ot.Function
    Physical model function to evaluate.
multivariateBasis : ot.OrthogonalProductPolynomialFactory
    Multivariate orthogonal polynomial basis factory.
totalDegree : int
    Total truncation degree of the expansion. Must be >= 0.
inputDistribution : ot.Distribution
    Joint probability distribution of the input random vector X.
inputSample : ot.Sample
    Input design of experiments sample in physical space.
outputSample : ot.Sample
    Output sample corresponding to model evaluations.

Returns
-------
pceResult : ot.FunctionalChaosResult
    Polynomial Chaos Expansion result object containing coefficients.
"""


# %%
import openturns as ot

# %%
distributionE = ot.Beta(0.9, 3.5, 65.0e9, 75.0e9)
distributionE.setDescription(["E"])
parametersF = ot.LogNormalMuSigma(300.0, 30.0, 0.0)  # Paramétrage par les moments
distributionF = ot.ParametrizedDistribution(parametersF)
distributionF.setDescription(["F"])
distributionL = ot.Uniform(2.50, 2.60)  # En mètres
distributionL.setDescription(["L"])
distributionI = ot.Beta(2.5, 4.0, 1.3e-7, 1.7e-7)  # En m⁴  # in cm^4
distributionI.setDescription(["I"])

inputDistribution = ot.JointDistribution(
    [distributionE, distributionF, distributionL, distributionI]
)

# %%
inputDimension = inputDistribution.getDimension()
outputDimension = 2  # dimension of the output


def function_beam(X):
    E, F, L, I = X
    Y = F * (L**3) / (3 * E * I)
    return [Y, Y]  # Create a multivariate output


model = ot.PythonFunction(inputDimension, outputDimension, function_beam)
model.setInputDescription(inputDistribution.getDescription())

# %%
# Create the orthogonal basis
enumerateFunction = ot.LinearEnumerateFunction(inputDimension)
multivariateBasis = ot.OrthogonalProductPolynomialFactory(
    [ot.LegendreFactory()] * inputDimension, enumerateFunction
)

# %%
# Create the input/output database
size = 1000
input_sample = inputDistribution.getSample(size)
output_sample = model(input_sample)
totalDegree = 3
strataIndex = enumerateFunction.getMaximumDegreeStrataIndex(totalDegree)
maximumBasisSize = enumerateFunction.getStrataCumulatedCardinal(strataIndex)
transformation = ot.DistributionTransformation(inputDistribution, multivariateBasis.getMeasure())

# %%
# Create a polynomial chaos expansion, step-by-step
standard_input = transformation(input_sample)
indices = ot.Indices(maximumBasisSize)
indices.fill()
functions = [multivariateBasis.build(i) for i in indices]
designProxy = ot.DesignProxy(standard_input, functions)
leastSquaresMethod="SVD"
leastSquaresMethod = ot.LeastSquaresMethod.Build(
    leastSquaresMethod, designProxy, indices
)
outputDimension = output_sample.getDimension()
coefficients = ot.Sample(maximumBasisSize, outputDimension)
for j in range(outputDimension):
    coeffsJ = leastSquaresMethod.solve(output_sample.getMarginal(j).asPoint())
    for i in range(maximumBasisSize):
        coefficients[i, j] = coeffsJ[i]

# %%
# Create the result

pceResult = ot.FunctionalChaosResult(
    input_sample,  # 1
    output_sample, # 2
    inputDistribution,  # 3
    transformation,  # 4
    transformation.inverse(),  # 5
    multivariateBasis,  # 6
    indices,  # 7
    coefficients,  # 8
    functions,  # 9
)

# %%
