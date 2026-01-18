from fastapi import FastAPI

app = FastAPI(title="Mexa.Digital Core")

@app.get("/health")
def health():
    return {"ok": True}
