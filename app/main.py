from fastapi import FastAPI

app = FastAPI(
    title="iSUpayX Payment Gateway",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}