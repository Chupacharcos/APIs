from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import v1

app = FastAPI(
    title="Spain IRPF & Tax Calculator",
    description="Calculate Spanish IRPF, autonomo SS quotas and quarterly payments. Updated for 2025.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1.router, prefix="/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "spain-irpf-calculator", "version": "1.0.0"}
