# openturns-agent-skills

A collection of custom skills for CLI assistants (Gemini CLI, etc.) focused on **OpenTURNS**, Uncertainty Quantification (UQ), and scientific computing.

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
git clone https://github.com/votre-compte/openturns-agent-skills.git
cd openturns-agent-skills
chmod +x install.sh
./install.sh
```

### Windows (PowerShell)

Open PowerShell and run:

```powershell
git clone https://github.com/votre-compte/openturns-agent-skills.git
cd openturns-agent-skills
.\install.ps1

```

### Global installation

To link your openturns-agent-skills repository directly to the global configuration directory of Gemini CLI, update the commands as follows:

```bash
mkdir -p ~/.config/gemini
ln -s ~/path/to/openturns-agent-skills/skills ~/.config/gemini/skills
```

---

## 🔄 Usage & Workflow

* **Instant Updates**: Any skill added or modified inside the `skills/` folder is immediately available across all your local projects.
* **Synchronization**:
```bash
git add .
git commit -m "feat: add new OpenTURNS skill"
git push

```



---

## 📝 License

Distributed under the LGPL license.

