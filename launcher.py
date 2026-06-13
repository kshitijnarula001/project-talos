import subprocess
import sys
import os

def check_ollama():
    try:
        subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            check=True
        )
        return True
    except Exception:
        return False

def check_model():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        return "gemma4" in result.stdout
    except Exception:
        return False

def setup():
    # Start ollama if not running
    if not check_ollama():
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        import time
        time.sleep(3)

    # Pull model if missing
    if not check_model():
        subprocess.run(
            ["ollama", "pull", "gemma4"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

if __name__ == "__main__":
    setup()
    # Launch main app
    sys.path.insert(0, os.path.dirname(__file__))
    from interface.app import TalosApp
    app = TalosApp()
    app.mainloop()