#!/bin/bash

echo "Installing Talos..."

# Install Ollama silently
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &
sleep 3

# Pull Gemma 4 model
ollama pull gemma4

# Install Python dependencies
pip3 install customtkinter ollama chromadb --break-system-packages

echo "Talos installation complete."
