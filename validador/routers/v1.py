from fastapi import APIRouter, Depends, Query
from typing import List
from pydantic import BaseModel

from auth import verify_marketplace
from services.validators.nif import validate_nif
from services.validators.nie import validate_nie
from services.validators.cif import validate_cif
from services.validators.iban import validate_iban
from services.validators.postal import validate_postal, PROVINCES, CCAA

router = APIRouter(dependencies=[Depends(verify_marketplace)])


@router.get("/validate/nif")
def endpoint_nif(nif: str = Query(..., description="NIF español (ej: 12345678Z)")):
    return validate_nif(nif)


@router.get("/validate/nie")
def endpoint_nie(nie: str = Query(..., description="NIE español (ej: X2482300W)")):
    return validate_nie(nie)


@router.get("/validate/cif")
def endpoint_cif(cif: str = Query(..., description="CIF español (ej: B12345678)")):
    return validate_cif(cif)


@router.get("/validate/iban")
def endpoint_iban(iban: str = Query(..., description="IBAN español (ej: ES9121000418450200051332)")):
    return validate_iban(iban)


@router.get("/validate/postal")
def endpoint_postal(postal: str = Query(..., description="Código postal (ej: 28001)")):
    return validate_postal(postal)


@router.get("/lookup/province")
def lookup_province(code: str = Query(..., description="Código de provincia de 2 dígitos (ej: 28)")):
    code = code.zfill(2)
    if code not in PROVINCES:
        return {"valid": False, "error": f"Código de provincia {code} no encontrado"}
    return {
        "valid": True,
        "code": code,
        "province": PROVINCES[code],
        "ccaa": CCAA.get(code, "Desconocida"),
    }


class BatchItem(BaseModel):
    type: str   # nif | nie | cif | iban | postal
    value: str


class BatchRequest(BaseModel):
    items: List[BatchItem]


@router.post("/validate/batch")
def validate_batch(body: BatchRequest):
    validators = {
        "nif": validate_nif,
        "nie": validate_nie,
        "cif": validate_cif,
        "iban": validate_iban,
        "postal": validate_postal,
    }

    items = body.items[:100]
    results = []
    valid_count = 0

    for item in items:
        fn = validators.get(item.type.lower())
        if fn is None:
            result = {
                "input": item.value,
                "type": item.type,
                "valid": False,
                "error": f"Tipo desconocido: {item.type}. Usa: nif, nie, cif, iban, postal",
            }
        else:
            result = fn(item.value)
            result["input"] = item.value

        if result.get("valid"):
            valid_count += 1
        results.append(result)

    return {
        "processed": len(results),
        "valid_count": valid_count,
        "invalid_count": len(results) - valid_count,
        "results": results,
    }
