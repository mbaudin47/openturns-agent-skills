"""Calculate Polynomial Chaos Expansion (PCE) coefficients directly.

Compute PCE coefficients using numerical integration without relying on
ot.FunctionalChaosAlgorithm. Map input samples onto standard measure and
evaluate the model at quadrature nodes.

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
experiment : ot.WeightedExperiment
    Weighted experiment providing quadrature nodes and weights.

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
multivariateBasis = ot.OrthogonalProductPolynomialFactory(
    [distributionE, distributionF, distributionL, distributionI]
)

# %%
totalDegree = 2
enumerateFunction = multivariateBasis.getEnumerateFunction()
basisSize = enumerateFunction.getBasisSizeFromTotalDegree(totalDegree)
adaptiveStrategy = ot.FixedStrategy(multivariateBasis, basisSize)

# %%
marginalSize = [4] * inputDimension
experiment = ot.GaussProductExperiment(inputDistribution, marginalSize)
inputSample, weights = experiment.generateWithWeights()
sampleSize = inputSample.getSize()
outputSample = model(inputSample)


# %%
distributionStandard = multivariateBasis.getMeasure()
transformation = ot.DistributionTransformation(inputDistribution, distributionStandard)
standardSample = transformation(inputSample)
inverseTransformation = transformation.inverse()

# %%
coefficients = ot.Sample(basisSize, outputDimension)
functionalBasis = []
for k in range(basisSize):
    basisFunction = multivariateBasis.build(k)
    functionalBasis.append(basisFunction)
    basisValue = basisFunction(standardSample)
    for i in range(outputDimension):
        integrandValue = ot.Point(
            [basisValue[j, 0] * outputSample[j, i] for j in range(sampleSize)]
        )
        coefficients[k, i] = integrandValue.dot(weights)

# %%
indices = range(basisSize)
pceResult = ot.FunctionalChaosResult(
    inputSample,
    outputSample,
    inputDistribution,
    transformation,
    inverseTransformation,
    multivariateBasis,
    indices,
    coefficients,
    functionalBasis,
)

# %%
