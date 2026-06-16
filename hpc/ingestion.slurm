#!/bin/bash
#SBATCH --job-name=caselawgpt-ingest
#SBATCH --partition=short          # CPU partition, adjust to your cluster's name
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/ingest-%j.out
#SBATCH --error=logs/ingest-%j.err

set -e
mkdir -p logs

module load python/3.11             # adjust to your cluster's module name

source "$HOME/caselawgpt-env/bin/activate"

export CL_TOKEN=a2860c163191bec342ee49976aa8c9511fdfa1d7

echo "Downloading cases..."
python scripts/download_courtlistener.py \
    --n-cases 300 \
    --start-date 2010-01-01

echo "Running ingestion pipeline..."
python generate-data.py

echo "Done. Data files are in data/"
ls -lh data/
ls -lh data/vectorstore/
