#!/bin/bash
# One-time HPC setup. Run this once from the login node after cloning the repo.
# Usage: bash hpc/setup.sh

set -e

echo "=== Setting up CaseLawGPT on HPC ==="

# 1. Install Ollama in user space (no sudo needed)
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | OLLAMA_INSTALL_DIR="$HOME/.ollama-bin" sh
export PATH="$HOME/.ollama-bin:$PATH"
echo 'export PATH="$HOME/.ollama-bin:$PATH"' >> ~/.bashrc

# 2. Create Python virtual environment
echo "Creating Python venv..."
module load python/3.11  # adjust to your HPC's available Python module
python -m venv "$HOME/caselawgpt-env"
source "$HOME/caselawgpt-env/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete. Next steps:"
echo "  1. Get a free CourtListener API token: https://www.courtlistener.com/sign-in/"
echo "  2. Submit the ingestion job:  sbatch hpc/ingestion.slurm"
echo "  3. Once ingestion finishes:   sbatch hpc/app.slurm"
