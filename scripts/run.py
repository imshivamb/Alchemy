import uvicorn
import subprocess
import sys
from multiprocessing import Process

def run_django():
    subprocess.run([
        sys.executable, 
        "backend/django_app/manage.py", 
        "runserver", 
        "8000"
    ])

def run_fastapi():
    uvicorn.run(
        "backend.fastapi_app.main:app", 
        host="0.0.0.0", 
        port=8001, 
        reload=True
    )

if __name__ == "__main__":
    django_process = Process(target=run_django)
    fastapi_process = Process(target=run_fastapi)
    
    django_process.start()
    fastapi_process.start()
    
    django_process.join()
    fastapi_process.join()