# openturns-agent-skills

[![OpenTURNS Version](https://img.shields.io/badge/OpenTURNS-1.27-blue.svg)](https://openturns.github.io/)

A collection of custom skills for CLI assistants (Gemini CLI, etc.) focused on **OpenTURNS (target version: 1.27)**, Uncertainty Quantification (UQ), and scientific computing.

---

## 🎯 Target Version

All skills and companion scripts in this repository are developed, tested, and validated against **OpenTURNS 1.27**.

When newer features or syntax changes are discussed (such as upcoming OpenTURNS 1.28+ APIs), skills provide version-safe fallback patterns to guarantee execution under OpenTURNS 1.27.

---

## 📦 Available Skills

| Skill | Description |
|---|---|
| **[`openturns-graphics`](skills/openturns-graphics/)** | Create, style, and export OpenTURNS graphics: curves, clouds, area filling (`Polygon.FillBetween`), 2D contours and level lines, multidimensional cross-cuts (`drawCrossCuts`), pairs plots (`DrawPairs`, `DrawPairsXY`), parallel coordinates, `GridLayout` overlap management, and Matplotlib integration. |
| **[`openturns-python-guide`](skills/openturns-python-guide/)** | Core data structures, model definitions, uncertainty quantification workflows, and best practices for OpenTURNS in Python. |
| **[`openturns-point-sample`](skills/openturns-point-sample/)** | Manipulate `Point` and `Sample` objects: creation, row/column slicing, boolean filtering, indexing, and seamless NumPy conversions. |
| **[`openturns-graph-bounds`](skills/openturns-graph-bounds/)** | Configure axis limits (`setXMin`, `setXMax`, `setYMin`, `setYMax`) and bounding boxes on OpenTURNS `Graph` objects. |
| **[`openturns-kriging`](skills/openturns-kriging/)** | Gaussian Process Regression / Kriging surrogate models: covariance kernels, trend basis, hyperparameter optimization, conditional variance, and validation ($R^2$). |
| **[`openturns-calibration`](skills/openturns-calibration/)** | Model parameter calibration and inverse problems: non-linear least squares, Gaussian MAP calibration, and Bayesian MCMC sampling (`RandomWalkMetropolisHastings`). |
| **[`openturns-reliability`](skills/openturns-reliability/)** | Rare event failure probability estimation: FORM, SORM, Subset Sampling, and Monte Carlo simulation algorithms. |
| **[`openturns-sensitivity-analysis`](skills/openturns-sensitivity-analysis/)** | Global sensitivity analysis: first-order, second-order, and total Sobol' indices (Saltelli, Martinez, Jansen, Mauntz-Kucherenko, PCE-based Sobol). |
| **[`openturns-functional-chaos`](skills/openturns-functional-chaos/)** | Polynomial Chaos Expansion (PCE) surrogate modeling using the high-level `FunctionalChaosAlgorithm`. |
| **[`openturns-pce-least-squares`](skills/openturns-pce-least-squares/)** | Low-level construction of Polynomial Chaos Expansion coefficients via direct least-squares methods (`LeastSquaresMethod`). |
| **[`openturns-pce-integration`](skills/openturns-pce-integration/)** | Low-level estimation of Polynomial Chaos Expansion coefficients via numerical integration and quadrature schemes. |
| **[`openturns-splitters`](skills/openturns-splitters/)** | Cross-validation and dataset splitting utilities using `KFoldSplitter` and `LeaveOneOutSplitter`. |
| **[`openturns-benchmark`](skills/openturns-benchmark/)** | Benchmarking CPU elapsed time vs sample size with logarithmic scaling, maximum execution time criteria, and native performance plots. |

---

## 🛠️ Repository Structure

```text
openturns-agent-skills/
├── skills/
│   ├── openturns-point-sample/
│   │   └── SKILL.md
│   ├── openturns-graph-bounds/
│   │   └── SKILL.md
│   └── ...
├── install.sh
├── install.ps1
├── CHANGELOG.md
└── README.md
```

---

## 🚀 Installation

The setup script creates a symbolic link from the `skills/` directory in this repository to your CLI assistant's global configuration directory.

### Manual installation

To use these skills in any OpenTURNS project, create a symbolic link named skills inside the project's .agents folder that points to the skills/ directory of this repository.

```
cd /path/to/uq_project_that_uses_OpenTURNS
mkdir -p .agents
cd .agents
ln -s /path/to/openturns-agent-skills/skills skills
```

This creates a symbolic link the uq_project_that_uses_OpenTURNS/.agents/skills to the openturns-agent-skills/skills directory.

### Linux / macOS

```bash
git clone https://github.com/mbaudin47/openturns-agent-skills.git
cd openturns-agent-skills
chmod +x install.sh
./install.sh
```

### Windows (PowerShell)

Open PowerShell and run:

```powershell
git clone https://github.com/mbaudin47/openturns-agent-skills.git
cd openturns-agent-skills
.\install.ps1

```

### Global installation

Depending on your agent CLI and operating environment, global skills can be linked to either `~/.config/gemini/skills` or `~/.agents/skills`:

#### Target 1: Gemini CLI configuration (`~/.config/gemini/skills`)
This is the default target configured by `install.sh`:

```bash
mkdir -p ~/.config/gemini
ln -s "$(pwd)/skills" ~/.config/gemini/skills
```

#### Target 2: Agent Specification directory (`~/.agents/skills`)
Several AI agent environments inspect `~/.agents/skills/` globally:

```bash
# Link the entire skills directory
mkdir -p ~/.agents
ln -s "$(pwd)/skills" ~/.agents/skills

# Or link specific skills into an existing ~/.agents/skills/ directory
ln -s "$(pwd)/skills/openturns-graphics" ~/.agents/skills/openturns-graphics
```

---

## 🔄 Usage & Workflow

* **Instant Updates**: Any skill added or modified inside the `skills/` folder is immediately available across all your local projects via the symbolic links.
* **CLI Commands**:
  * `/skills list`: displays all detected skills and their descriptions.
  * `/skills reload`: reloads skills in the current interactive session after adding or modifying a skill.
* **Synchronization**:
```bash
git add .
git commit -m "feat: add new OpenTURNS skill"
git push
```



---

## 📝 License

Distributed under the LGPL license.

