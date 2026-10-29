---
name: openturns-splitters
description: Utiliser les classes KFoldSplitter et LeaveOneOutSplitter d'OpenTURNS pour la validation croisée et le découpage d'échantillons en sous-ensembles d'entraînement et de test.
---

# Validation croisée avec KFoldSplitter et LeaveOneOutSplitter dans OpenTURNS

Ce guide décrit l'utilisation des classes `KFoldSplitter` et `LeaveOneOutSplitter` du module `openturns` pour réaliser le découpage d'échantillons (`ot.Sample`) en sous-ensembles d'entraînement et de test dans le cadre d'une validation croisée.

## Principe général

Les classes héritant de la méthode de découpage d'OpenTURNS fournissent des itérateurs. À chaque itération de la boucle Python, l'itérateur renvoie un tuple `(indicesTrain, indicesTest)` sous la forme de deux objets `ot.Indices`. Ces objets permettent de découper directement un échantillon de données `ot.Sample` grâce à l'opérateur de crochet `sample[indices]`.

---

## 1. KFoldSplitter

La classe `ot.KFoldSplitter` divise un jeu de données de taille $N$ en $K$ plis (folds). Chaque pli est utilisé une fois comme jeu de test, tandis que les $K-1$ autres plis constituent le jeu d'entraînement.

### Syntaxe et méthodes principales
* **Constructeur :** `ot.KFoldSplitter(N, k)`
  * `N` (int) : Taille de l'ensemble d'indices (généralement `sample.getSize()`).
  * `k` (int) : Nombre de plis.
* **Méthodes :**
  * `setRandomize(randomize)` (bool) : Active ou désactive le mélange aléatoire des plis.
  * `getSize()` : Renvoie le nombre de découpages générés (égal à $K$).
  * `getN()` : Renvoie la taille $N$ de l'ensemble.

### Exemple basique

```python
import openturns as ot

# Création d'un échantillon
sample = ot.Normal().getSample(100)
k = 5

splitter = ot.KFoldSplitter(sample.getSize(), k)

for indicesTrain, indicesTest in splitter:
    sampleTrain = sample[indicesTrain]
    sampleTest = sample[indicesTest]
    # Traitement sur les échantillons d'entraînement et de test
```

### Calcul du score $R^2$ par validation croisée K-Fold

```python
import openturns as ot

def compute_r2_kfold(x_sample, y_sample, model_builder_fn, k=5):
    """
    Calcule le score R2 moyen par validation croisée K-Fold.

    Parameters
    ----------
    x_sample : ot.Sample
        Variables d'entrée.
    y_sample : ot.Sample
        Variables de sortie.
    model_builder_fn : callable
        Fonction prenant (x_train, y_train) et retournant un ot.Function (métamodèle).
    k : int
        Nombre de plis.

    Returns
    -------
    ot.Point
        Score R2 moyen pour chaque dimension de sortie.
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

La classe `ot.LeaveOneOutSplitter` génère $N$ découpages. À chaque étape, une seule observation est conservée pour le test, et les $N-1$ autres observations servent à l'entraînement.

### Syntaxe et méthodes principales
* **Constructeur :** `ot.LeaveOneOutSplitter(N)`
  * `N` (int) : Taille de l'ensemble d'indices (`sample.getSize()`).
* **Méthodes :**
  * `getSize()` : Renvoie le nombre de jeux générés (égal à $N$).
  * `getN()` : Renvoie la taille $N$.

### Exemple basique

```python
import openturns as ot

sample = ot.Normal().getSample(20)
splitter = ot.LeaveOneOutSplitter(sample.getSize())

for indicesTrain, indicesTest in splitter:
    sampleTrain = sample[indicesTrain]
    sampleTest = sample[indicesTest]  # Échantillon de taille 1
```

### Calcul de l'erreur quadratique moyenne Leave-One-Out (MSE LOO)

```python
import openturns as ot

def compute_mse_loo(x_sample, y_sample, model_builder_fn):
    """
    Calcule l'erreur quadratique moyenne Leave-One-Out (MSE LOO).
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

## Recommandations d'utilisation

1. **Reproductibilité :** Pour `KFoldSplitter`, l'option de mélange aléatoire dépend par défaut de la clé `KFoldSplitter-Randomize` dans `ot.ResourceMap`. Il convient de fixer la graine du générateur via `ot.RandomGenerator.SetSeed(...)` pour assurer la répétabilité des résultats.
2. **Indexation directe :** L'extraction des sous-échantillons à partir des objets `ot.Indices` s'effectue directement avec la syntaxe `sample[indices]`, sans nécessiter de conversion intermédiaire en liste Python.
3. **Optimisation pour les moindres carrés :** Lorsque le modèle est une régression par moindres carrés (par exemple un polynôme du chaos), l'évaluation numérique brute répétée par `LeaveOneOutSplitter` peut être avantageusement remplacée par la formule analytique basée sur la diagonale de la matrice chapeau (`lsqMethod.getHDiag()` sur un objet `ot.QRMethod`).
