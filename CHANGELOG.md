# Changelog

All notable changes to the `openturns-agent-skills` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- **`openturns-graphics`**: Created a comprehensive OpenTURNS graphics skill:
  - Basic drawables: `ot.Graph`, `ot.Curve`, `ot.Cloud`, and `ot.Polygon.FillBetween` for shading areas under curves.
  - 2D contour plots and level lines: `Function.draw()`, `Distribution.drawPDF()`, explicit `ot.Contour`, filled areas, iso-lines, and superposition patterns.
  - Colormap, colorbar, and normalization: `setColorMap`, `setColorBarPosition`, and `setColorMapNorm` with `"log"` and `"rank"` scales.
  - Multidimensional function cross-cuts: `Function.drawCrossCuts()` with shared color scale, single global colorbar, and triangular grid tick label cleanup.
  - Statistical visual tests: `ot.VisualTest.DrawPairs`, `DrawPairsMarginals`, `DrawPairsXY`, and `DrawParallelCoordinates`.
  - Layout management: `ot.GridLayout` sub-graph indexing and `subplots_adjust(hspace=..., wspace=...)` margin adjustments.
  - Viewer customization: `otv.View` integration with `figure_kw`, `legend_kw`, direct Matplotlib axes access, and tight bounding box exports (`bbox_inches="tight"`).
  - Companion test script: `skills/openturns-graphics/scripts/plot_graphics.py`.
- **Target Versioning (OpenTURNS 1.27)**:
  - Added OpenTURNS 1.27 badge and dedicated `🎯 Target Version` section to `README.md`.
  - Added target version callouts in `openturns-python-guide` and `openturns-graphics`.
  - Added `Target Version: OpenTURNS 1.27` docstring headers to all Python demonstration scripts.
- **Documentation**:
  - Added complete 13-skill catalog table to `README.md` with links to individual skill directories.
  - Documented global installation targets (`~/.config/gemini/skills` for Gemini CLI and `~/.agents/skills` for agent specifications).
  - Added CLI management command references (`/skills list`, `/skills reload`).

### Changed
- **Internationalization (100% English)**:
  - Translated `skills/openturns-splitters/SKILL.md` entirely into English.
  - Translated `skills/openturns-pce-integration/SKILL.md` (and normalized skill name to `openturns-pce-integration`).
  - Translated French comments in `PCE_from_Integration.py` and `PCE_from_Least_Squares.py`.
- **Compatibility with OpenTURNS 1.27**:
  - `skills/openturns-graph-bounds/SKILL.md`: Added OpenTURNS 1.27 bounding box syntax (`ot.Interval` via `setBoundingBox()` and `otv.View` axes limits) alongside OpenTURNS 1.28+ individual axis setters (`setXMin`, `setXMax`).
  - `skills/openturns-benchmark/scripts/benchmark_PCE_cross_validation.py`: Guarded experimental `FunctionalChaosValidation` to support execution on OpenTURNS 1.27.

### Fixed
- Fixed missing YAML frontmatter delimiters (`---`) in `skills/openturns-pce-least-squares/SKILL.md`.
- Fixed repository clone URL in `README.md` (`https://github.com/mbaudin47/openturns-agent-skills.git`).
- Verified that all 13 skills pass `validate_skill.cjs` and all 12 companion scripts execute cleanly under OpenTURNS 1.27.

---

## [2026-11-18]

### Added
- **`openturns-calibration`**: Parameter calibration and inverse problems (`NonLinearLeastSquaresCalibration`, `GaussianNonLinearCalibration`, `RandomWalkMetropolisHastings`).
- **`openturns-kriging`**: Gaussian process surrogate models, Matérn covariance kernels, trend bases, and validation ($R^2$).
- **`openturns-reliability`**: Structural reliability and failure probability estimation (FORM, SORM, Subset Sampling, Monte Carlo).
- **`openturns-sensitivity-analysis`**: Global sensitivity analysis and Sobol' indices (Saltelli, Martinez, Jansen, Mauntz-Kucherenko, PCE-based Sobol).

---

## [2026-10-30]

### Added
- **`openturns-benchmark`**: Benchmarking CPU elapsed time vs sample size using logarithmic scaling and execution time stopping criteria.

---

## [2026-10-29]

### Added
- **`openturns-splitters`**: Sample partitioning for cross-validation (`KFoldSplitter`, `LeaveOneOutSplitter`).

---

## [2026-10-28]

### Added
- **`openturns-functional-chaos`**: Polynomial Chaos Expansion surrogate modeling via `FunctionalChaosAlgorithm`.
- **`openturns-pce-least-squares`**: Low-level PCE coefficient fitting via `LeastSquaresMethod`.
- **`openturns-pce-integration`**: Low-level PCE coefficient fitting via numerical integration and quadrature.
- **`openturns-point-sample`**: Data manipulation with `ot.Point` and `ot.Sample`.
- **`openturns-graph-bounds`**: Axis limits and bounding box configuration.
- **`openturns-python-guide`**: Developer handbook for idiomatic OpenTURNS in Python.
- Initial repository setup with `install.sh`, `install.ps1`, and project structure.
