from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import v1

app = FastAPI(
    title="Spain Tax ID Validator",
    description="Validate Spanish NIF, NIE, CIF, IBAN and Postal Codes in real time.",
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
    return {"status": "ok", "service": "spain-tax-validator", "version": "1.0.0"}


