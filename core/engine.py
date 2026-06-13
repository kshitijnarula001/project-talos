import subprocess
import requests
import time
import os
import sys

OLLAMA_PATH = "/usr/local/bin/ollama"
MODEL = "gemma4"

def is_ollama_running():
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=2
        )
        return response.status_code == 200
    except:
        return False

def start_ollama():
    if not is_ollama_running():
        print("Starting Talos engine...")
        subprocess.Popen(
            [OLLAMA_PATH, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait for it to start
        attempts = 0
        while not is_ollama_running() and attempts < 10:
            time.sleep(1)
            attempts += 1
        
        if not is_ollama_running():
            print("Engine failed to start.")
            sys.exit(1)

def is_model_available():
    try:
        response = requests.get(
            "http://localhost:11434/api/tags"
        )
        models = response.json().get("models", [])
        return any(MODEL in m["name"] for m in models)
    except:
        return False

def pull_model():
    if not is_model_available():
        print(f"Loading Talos brain...")
        subprocess.run(
            [OLLAMA_PATH, "pull", MODEL],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

def initialize():
    start_ollama()
    pull_model()
    print("Talos engine ready.")

if __name__ == "__main__":
    initialize()
