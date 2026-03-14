from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import v1

app = FastAPI(
    title="Spanish Invoice PDF Generator",
    description="Generate legally compliant Spanish invoices as PDF. IVA, IRPF, all AEAT required fields (RD 1619/2012).",
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
    return {"status": "ok", "service": "spanish-invoice-generator", "version": "1.0.0"}
