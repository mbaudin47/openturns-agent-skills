
name: openturns-integration-pce
description: Generates custom Python code using OpenTURNS to compute Polynomial Chaos Expansion (PCE) coefficients via integration and quadrature without relying on FunctionalChaosAlgorithm. Use when asked for explicit, step-by-step implementation of PCE coefficient estimation by numerical integration or opening the PCE black box in OpenTURNS.

title: Développement en polynômes du chaos par intégration numérique avec OpenTURNS

* openturns
* polynomes-de-chaos
* quadrature

# Développement en polynômes du chaos par intégration numérique dans OpenTURNS

Ce document synthétise la théorie, la structure sous-jacente des objets OpenTURNS et l'implémentation explicite de l'estimation des coefficients d'un développement en polynômes du chaos (PCE) par intégration numérique (quadrature), sans recourir à la classe haut niveau `ot.FunctionalChaosAlgorithm`.

## When to Use

- When explicit, step-by-step control over basis creation and integration is needed.
- When teaching or demonstrating low-level PCE estimation without "black-box" wrappers.
- When creating an explicit `FunctionalChaosResult`.

## Architecture et démarche sous OpenTURNS

Pour ouvrir la boîte noire d'OpenTURNS et construire manuellement le résultat `ot.FunctionalChaosResult`, la démarche suit six étapes :

1. **Définition de la distribution et de la fonction** : Construction de la distribution conjointe $P_{\mathbf{X}}$ et de la fonction $g$.
2. **Construction de la base multivariée** : Instanciation de `ot.OrthogonalProductPolynomialFactory` et détermination du nombre de polynômes $K$ associés au degré total $p$ via l'ensemble d'énumération.
3. **Génération du plan d'expériences d'intégration** : Génération des nœuds et poids de quadrature via `experiment.generateWithWeights()`.
4. **Passage dans l'espace standard** : Récupération de la mesure standard $P_{\mathbf{Z}} = \text{multivariateBasis.getMeasure()}$ et transformation des nœuds physiques $\mathbf{z}^{(j)} = T(\mathbf{x}^{(j)})$.
5. **Calcul explicite des produits scalaires** : Évaluation des polynômes sur l'échantillon standardisé, produit terme à terme avec les réponses du modèle $g(\mathbf{x}^{(j)})$, puis produit scalaire avec le vecteur des poids $w$.
6. **Assemblage de l'objet résultat** : Instanciation directe de `ot.FunctionalChaosResult`.

## Implémentation Python de référence

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

multivariateBasis = ot.OrthogonalProductPolynomialFactory(
    [distributionE, distributionF, distributionL, distributionI]

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
```

## Key Guidelines

- Always perform regression in the **standardized space** $\boldsymbol{Z} = T(\boldsymbol{X})$. Using physical space samples with orthogonal polynomials of standardized distributions leads to incorrect coefficient estimations.
- Ensure `enumerateFunction` index matches order within `ot.Basis`.
- Use standard OpenTURNS methods for reading/writing datasets (e.g. `Sample.ImportFromCSVFile()`).

#skill 
