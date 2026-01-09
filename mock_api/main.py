# Mock API Service

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

def main():
    print("Hello from mock-api!")


if __name__ == "__main__":
    main()
