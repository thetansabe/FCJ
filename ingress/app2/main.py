from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from App 2"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "app2"}
