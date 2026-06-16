#!/bin/bash
#SBATCH --job-name=caselawgpt-app
#SBATCH --partition=gpu            # GPU partition, adjust to your cluster's name
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --gres=gpu:1               # 1 GPU for Ollama
#SBATCH --time=08:00:00            # 8-hour session — resubmit if needed
#SBATCH --output=logs/app-%j.out
#SBATCH --error=logs/app-%j.err

set -e
mkdir -p logs

module load python/3.11            # adjust to your cluster's module name
module load cuda/12.1              # adjust to available CUDA version

source "$HOME/caselawgpt-env/bin/activate"
export PATH="$HOME/.ollama-bin:$PATH"

# Start Ollama server in background
echo "Starting Ollama..."
ollama serve &
OLLAMA_PID=$!
sleep 5

# Pull model if not already cached
ollama pull qwen2.5:14b

# Install and start ngrok to expose the app publicly
# Get a free ngrok token at: https://dashboard.ngrok.com
NGROK_TOKEN="YOUR_NGROK_AUTHTOKEN_HERE"
if ! command -v ngrok &> /dev/null; then
    curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /tmp/ngrok.asc
    pip install pyngrok
fi
python -c "
from pyngrok import ngrok, conf
conf.get_default().auth_token = '$NGROK_TOKEN'
tunnel = ngrok.connect(8501)
print(f'PUBLIC URL: {tunnel.public_url}')
" &
NGROK_PID=$!
sleep 3

# Start Streamlit
echo "Starting Streamlit..."
streamlit run app.py \
    --server.port 8501 \
    --server.headless true \
    --server.address 0.0.0.0

# Cleanup on exit
kill $OLLAMA_PID $NGROK_PID 2>/dev/null || true
