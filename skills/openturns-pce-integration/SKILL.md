---
name: openturns-pce-integration
description: Compute Polynomial Chaos Expansion (PCE) coefficients via numerical integration and quadrature without relying on FunctionalChaosAlgorithm. Use when explicit, step-by-step implementation of PCE coefficient estimation by numerical integration is required.
---

# OpenTURNS Polynomial Chaos Expansion via Numerical Integration

This guide synthesizes the theory, underlying OpenTURNS object architecture, and explicit implementation of Polynomial Chaos Expansion (PCE) coefficient estimation via numerical integration (quadrature), without relying on the high-level `ot.FunctionalChaosAlgorithm`.

## When to Use

- When explicit, step-by-step control over basis creation and numerical integration is needed.
- When teaching or demonstrating low-level PCE estimation without "black-box" wrappers.
- When creating an explicit `FunctionalChaosResult` object manually.

## Architecture and Workflow

To open the OpenTURNS black box and manually construct an `ot.FunctionalChaosResult`, follow these six steps:

1. **Define Input Distribution and Physical Model**: Construct the joint distribution $P_{\mathbf{X}}$ and the physical function $g$.
2. **Construct the Multivariate Basis**: Instantiate `ot.OrthogonalProductPolynomialFactory` and determine the basis size $K$ associated with total degree $p$ via the linear enumeration function.
3. **Generate the Integration Experiment**: Generate quadrature nodes and integration weights via `experiment.generateWithWeights()`.
4. **Transform into Standard Space**: Retrieve the standardized measure $P_{\mathbf{Z}} = \text{multivariateBasis.getMeasure()}$ and map physical nodes to standard space $\mathbf{z}^{(j)} = T(\mathbf{x}^{(j)})$.
5. **Explicit Scalar Product Computation**: Evaluate polynomials on the standardized sample, perform element-wise multiplication with model outputs $g(\mathbf{x}^{(j)})$, and compute the dot product with the integration weights vector $\boldsymbol{w}$.
6. **Assemble the Result Object**: Directly instantiate `ot.FunctionalChaosResult`.

## Reference Python Implementation

```python
import openturns as ot

# Define marginals
distributionE = ot.Beta(0.9, 3.5, 65.0e9, 75.0e9)
distributionE.setDescription(["E"])
parametersF = ot.LogNormalMuSigma(300.0, 30.0, 0.0)  # Parameterized by moments
distributionF = ot.ParametrizedDistribution(parametersF)
distributionF.setDescription(["F"])
distributionL = ot.Uniform(2.50, 2.60)  # In meters
distributionL.setDescription(["L"])
distributionI = ot.Beta(2.5, 4.0, 1.3e-7, 1.7e-7)  # In m^4
distributionI.setDescription(["I"])

inputDistribution = ot.JointDistribution(
    [distributionE, distributionF, distributionL, distributionI]
)

inputDimension = inputDistribution.getDimension()
outputDimension = 2  # Dimension of the output

def function_beam(X):
    E, F, L, I = X
    Y = F * L**3 / (3.0 * E * I)
    return [Y, Y]  # Multivariate output

model = ot.PythonFunction(inputDimension, outputDimension, function_beam)
model.setInputDescription(inputDistribution.getDescription())

multivariateBasis = ot.OrthogonalProductPolynomialFactory(
    [distributionE, distributionF, distributionL, distributionI]
)

totalDegree = 2
enumerateFunction = multivariateBasis.getEnumerateFunction()
basisSize = enumerateFunction.getBasisSizeFromTotalDegree(totalDegree)
adaptiveStrategy = ot.FixedStrategy(multivariateBasis, basisSize)

marginalSize = [4] * inputDimension
experiment = ot.GaussProductExperiment(inputDistribution, marginalSize)
inputSample, weights = experiment.generateWithWeights()
sampleSize = inputSample.getSize()
outputSample = model(inputSample)

distributionStandard = multivariateBasis.getMeasure()
transformation = ot.DistributionTransformation(inputDistribution, distributionStandard)
standardSample = transformation(inputSample)
inverseTransformation = transformation.inverse()

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
```

## Key Guidelines

- Always compute orthogonal polynomial values in the **standardized space** $\boldsymbol{Z} = T(\boldsymbol{X})$. Evaluating polynomials of standard distributions on physical space samples yields incorrect coefficients.
- Ensure `enumerateFunction` indices match the order within `ot.Basis`.
- Use standard OpenTURNS methods for reading and writing datasets (e.g. `ot.Sample.ImportFromCSVFile()`).
