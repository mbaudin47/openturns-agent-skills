
name: openturns-pce-least-squares
description: Generates or refactors custom OpenTURNS Python code to construct Polynomial Chaos Expansions (PCE) using direct least-squares estimation (LeastSquaresMethod) without relying on FunctionalChaosAlgorithm. Use when explicit control over the basis construction, design matrix, or low-level coefficient fitting is required, or when wrapping the results back into a FunctionalChaosResult object.

# OpenTURNS Polynomial Chaos Expansion via Least-Squares

This skill guides the implementation of low-level Polynomial Chaos Expansions (PCE) using OpenTURNS with least-squares regression via `LeastSquaresMethod`, bypassing `FunctionalChaosAlgorithm` to provide full transparency and control over the design matrix, basis functions, and coefficient evaluation.

## When to Use

- When explicit, step-by-step control over basis creation and linear regression is needed.
- When teaching or demonstrating low-level PCE estimation without "black-box" wrappers.
- When creating an explicit `FunctionalChaosResult`.

## Workflow & Steps

1. **Define Input Distribution & Physical Model**: Create the input distribution and model $Y = g(\boldsymbol{X})$.
2. **Setup Orthogonal Basis & Standard Measure**:
	   - Instantiate `ot.OrthogonalProductPolynomialFactory`.
	   - Obtain the standardized measure via `multivariateBasis.getMeasure()`.
	   - Create the transformation `ot.DistributionTransformation(inputDistribution, standardizedMeasure)` to map input samples $\boldsymbol{X} \to \boldsymbol{Z}$.
3. **Build the Basis Set**:
	   - Determine `basisSize` using `enumerateFunction.getBasisSizeFromTotalDegree(totalDegree)`.
	   - Iterate and construct basis functions into an `ot.Basis()`.
4. **Solve Least-Squares via `LeastSquaresMethod`**:
	* Standardize input training samples: `standard_input = transformation(input_sample)`.
	* Construct basis functions `functions = [multivariateBasis.build(i) for i in indices]` and build `ot.DesignProxy(standard_input, functions)`.
	* Instantiate the least-squares solver using `ot.LeastSquaresMethod.Build("SVD", designProxy, indices)`.
	* Solve for each output marginal with `leastSquaresMethod.solve(output_sample.getMarginal(j).asPoint())` and assemble the result into `coefficients`.
5. **Reconstruct `FunctionalChaosResult`**:
    - Instantiate `ot.FunctionalChaosResult` directly by passing `input_sample`, `output_sample`, `inputDistribution`, `transformation`, `transformation.inverse()`, `multivariateBasis`, `indices`, `coefficients`, and `functions`.

```python

import openturns as ot

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

inputDimension = inputDistribution.getDimension()
outputDimension = 2  # dimension of the output

def function_beam(X):

    return [Y, Y]  # Create a multivariate output

model = ot.PythonFunction(inputDimension, outputDimension, function_beam)
model.setInputDescription(inputDistribution.getDescription())

# Create the orthogonal basis
enumerateFunction = ot.LinearEnumerateFunction(inputDimension)
multivariateBasis = ot.OrthogonalProductPolynomialFactory(
    [ot.LegendreFactory()] * inputDimension, enumerateFunction

# Create the input/output database

input_sample = inputDistribution.getSample(size)
output_sample = model(input_sample)
totalDegree = 3
strataIndex = enumerateFunction.getMaximumDegreeStrataIndex(totalDegree)
maximumBasisSize = enumerateFunction.getStrataCumulatedCardinal(strataIndex)
transformation = ot.DistributionTransformation(inputDistribution, multivariateBasis.getMeasure())

# Create a polynomial chaos expansion, step-by-step
standard_input = transformation(input_sample)
indices = ot.Indices(maximumBasisSize)
indices.fill()
functions = [multivariateBasis.build(i) for i in indices]
designProxy = ot.DesignProxy(standard_input, functions)
leastSquaresMethod="SVD"
leastSquaresMethod = ot.LeastSquaresMethod.Build(
    leastSquaresMethod, designProxy, indices

outputDimension = output_sample.getDimension()
coefficients = ot.Sample(maximumBasisSize, outputDimension)
for j in range(outputDimension):
    coeffsJ = leastSquaresMethod.solve(output_sample.getMarginal(j).asPoint())
    for i in range(maximumBasisSize):
        coefficients[i, j] = coeffsJ[i]

# Create the result

pceResult = ot.FunctionalChaosResult(
    input_sample,  # 1

    inputDistribution,  # 3
    transformation,  # 4
    transformation.inverse(),  # 5
    multivariateBasis,  # 6
    indices,  # 7
    coefficients,  # 8
    functions,  # 9
```

## Key Guidelines

- Always perform regression in the **standardized space** $\boldsymbol{Z} = T(\boldsymbol{X})$. Using physical space samples with orthogonal polynomials of standardized distributions leads to incorrect coefficient estimations.
- Ensure `enumerateFunction` index matches order within `ot.Basis`.
- Use standard OpenTURNS methods for reading/writing datasets (e.g. `Sample.ImportFromCSVFile()`).

#skill
