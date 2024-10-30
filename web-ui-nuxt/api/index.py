from fastapi import FastAPI

app = FastAPI()

@app.get("/api")
def hello_world():
    return {"message": "Hello World", "api": "Python"}

@app.get("/api/test")
def test():
    return {"message": "Test"}