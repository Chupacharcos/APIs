from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel

from auth import verify_marketplace
from services.invoice_generator import generate_invoice_pdf, calculate_totals

router = APIRouter(dependencies=[Depends(verify_marketplace)])


# ── Modelos ────────────────────────────────────────────────────────────────────

class InvoiceMeta(BaseModel):
    series: str = "A"
    number: int = 1
    date: str = ""
    due_date: Optional[str] = None
    currency: str = "EUR"

class Party(BaseModel):
    name: str = "Empresa Ejemplo SL"
    nif: Optional[str] = "B12345674"
    address: Optional[str] = "Calle Mayor 1, 28001 Madrid"
    city: Optional[str] = None
    postal_code: Optional[str] = None
    province: Optional[str] = None
    email: Optional[str] = None

class InvoiceLine(BaseModel):
    description: str = "Servicio de consultoría"
    quantity: float = 1
    unit_price: float = 500.0
    iva_rate: float = 21   # 0, 4, 10, 21
    discount: float = 0    # %

class Taxes(BaseModel):
    irpf_rate: float = 0   # 0, 7, 15

class InvoiceOptions(BaseModel):
    notes: Optional[str] = None
    watermark: bool = False

_default_issuer = Party()
_default_client = Party(name="Cliente SA", nif="A87654321", address="Avenida del Puerto 5, 46001 Valencia")
_default_line = InvoiceLine()

class InvoiceRequest(BaseModel):
    invoice: InvoiceMeta = InvoiceMeta()
    issuer: Party = _default_issuer
    client: Party = _default_client
    lines: List[InvoiceLine] = [_default_line]
    taxes: Taxes = Taxes()
    options: InvoiceOptions = InvoiceOptions()

class BatchInvoiceRequest(BaseModel):
    invoices: List[InvoiceRequest]


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/invoice/generate")
def generate(body: Optional[InvoiceRequest] = None):
    data = (body or InvoiceRequest()).model_dump()
    return generate_invoice_pdf(data)


@router.post("/invoice/validate")
def validate(body: Optional[InvoiceRequest] = None):
    b = body or InvoiceRequest()
    data = b.model_dump()
    totals = calculate_totals(data)
    return {"valid": True, "invoice_number": f"{b.invoice.series}-{str(b.invoice.number).zfill(4)}", **totals}


@router.post("/invoice/batch")
def batch(body: Optional[BatchInvoiceRequest] = None):
    results = []
    for inv_data in (body.invoices if body else [InvoiceRequest()])[:10]:
        try:
            result = generate_invoice_pdf(inv_data.model_dump())
            results.append(result)
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    return {"count": len(results), "invoices": results}


@router.get("/invoice/templates")
def templates():
    return {
        "templates": [
            {
                "id": "freelance",
                "name": "Autónomo / Freelance",
                "description": "Con IRPF 15%, IVA 21%",
                "defaults": {"irpf_rate": 15, "iva_rate": 21},
            },
            {
                "id": "empresa",
                "name": "Empresa a Empresa (B2B)",
                "description": "Sin IRPF, IVA 21%",
                "defaults": {"irpf_rate": 0, "iva_rate": 21},
            },
            {
                "id": "nuevo_autonomo",
                "name": "Nuevo autónomo (primeros 3 años)",
                "description": "IRPF reducido 7%, IVA 21%",
                "defaults": {"irpf_rate": 7, "iva_rate": 21},
            },
        ]
    }
