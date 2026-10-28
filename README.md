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

### Linux / macOS

```bash
git clone [https://github.com/votre-compte/openturns-agent-skills.git](https://github.com/votre-compte/openturns-agent-skills.git)
cd openturns-agent-skills
chmod +x install.sh
./install.sh

```

### Windows (PowerShell)

Open PowerShell and run:

```powershell
git clone [https://github.com/votre-compte/openturns-agent-skills.git](https://github.com/votre-compte/openturns-agent-skills.git)
cd openturns-agent-skills
.\install.ps1

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

