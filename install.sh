#!/usr/bin/env bash

# Chemin vers le dossier de configuration global Gemini CLI
GEMINI_SKILLS_DIR="$HOME/.config/gemini/skills"

# Création du dossier parent si nécessaire
mkdir -p "$HOME/.config/gemini"

# Suppression du dossier ou lien existant si présent
if [ -e "$GEMINI_SKILLS_DIR" ] || [ -L "$GEMINI_SKILLS_DIR" ]; then
  rm -rf "$GEMINI_SKILLS_DIR"
fi

# Création du lien symbolique
ln -s "$(pwd)/skills" "$GEMINI_SKILLS_DIR"

echo "Lien symbolique créé avec succès : $GEMINI_SKILLS_DIR -> $(pwd)/skills"