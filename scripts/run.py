# scripts/run.py
import uvicorn
import subprocess
import sys
from multiprocessing import Process
import os

# Get the project root directory and set paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

def run_django():
    subprocess.run([
        sys.executable, 
        os.path.join(BACKEND_DIR, "django_app", "manage.py"),
        "runserver", 
        "8000"
    ])

def run_fastapi():
    # Add both backend and fastapi_app to Python path
    if BACKEND_DIR not in sys.path:
        sys.path.insert(0, BACKEND_DIR)
    
    uvicorn.run(
        "fastapi_app.main:app",
        host="0.0.0.0", 
        port=8001, 
        reload=True,
        reload_dirs=[os.path.join(BACKEND_DIR, "fastapi_app")]
    )

if __name__ == "__main__":
    django_process = Process(target=run_django)
    fastapi_process = Process(target=run_fastapi)
    
    try:
        django_process.start()
        fastapi_process.start()
        
        django_process.join()
        fastapi_process.join()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        django_process.terminate()
        fastapi_process.terminate()
        django_process.join()
        fastapi_process.join()
        print("Servers shut down successfully")