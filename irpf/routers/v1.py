from fastapi import APIRouter, Depends, Query
from typing import Optional
from fastapi import Body
from pydantic import BaseModel

from auth import verify_marketplace
from services.irpf_calculator import (
    simulate_autonomo, calculate_irpf, simulate_salary,
    get_ss_quota, COMMUNITIES, STATE_BRACKETS, REGIONAL_BRACKETS,
)

router = APIRouter(dependencies=[Depends(verify_marketplace)])


# ── Modelos ────────────────────────────────────────────────────────────────────

class AutonomoSimulateReq(BaseModel):
    annual_invoiced: float = 50000
    expenses: float = 0
    community: str = "MD"
    irpf_rate: int = 15

class AutonomoQuotaReq(BaseModel):
    net_annual: float = 40000

class IrpfCalcReq(BaseModel):
    gross: float = 50000
    community: str = "MD"
    deductions: float = 0

class SalaryReq(BaseModel):
    gross_salary: float = 30000
    community: str = "MD"

class QuarterlyReq(BaseModel):
    annual_invoiced: float = 50000
    expenses: float = 0
    community: str = "MD"
    irpf_rate: int = 15


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/autonomo/simulate")
def autonomo_simulate(body: Optional[AutonomoSimulateReq] = None):
    b = body or AutonomoSimulateReq()
    return simulate_autonomo(b.annual_invoiced, b.expenses, b.community, b.irpf_rate)


@router.post("/autonomo/quota")
def autonomo_quota(body: Optional[AutonomoQuotaReq] = None):
    b = body or AutonomoQuotaReq()
    result = get_ss_quota(b.net_annual)
    return {"net_annual": b.net_annual, **result}


@router.post("/autonomo/quarterly")
def autonomo_quarterly(body: Optional[QuarterlyReq] = None):
    b = body or QuarterlyReq()
    full = simulate_autonomo(b.annual_invoiced, b.expenses, b.community, b.irpf_rate)
    q_base = round(full["irpf_base"] / 4, 2)
    q_tax  = round(q_base * b.irpf_rate / 100, 2)
    return {
        "annual_irpf_base":      full["irpf_base"],
        "quarterly_base":        q_base,
        "irpf_rate":             b.irpf_rate,
        "quarterly_withholding": q_tax,
        "modelo_130":            q_tax,
        "year": 2025,
    }


@router.post("/irpf/calculate")
def irpf_calculate(body: Optional[IrpfCalcReq] = None):
    b = body or IrpfCalcReq()
    return calculate_irpf(b.gross, b.community, b.deductions)


@router.get("/irpf/rates")
def irpf_rates(community: Optional[str] = Query(None, description="Código CC.AA. (ej: MD, CT, AN)")):
    state = [
        {"from": b[0], "to": None if b[1] == float("inf") else b[1], "rate_pct": b[2]}
        for b in STATE_BRACKETS
    ]
    if community:
        brackets = REGIONAL_BRACKETS.get(community.upper(), [])
        regional = [
            {"from": b[0], "to": None if b[1] == float("inf") else b[1], "rate_pct": b[2]}
            for b in brackets
        ]
        return {"year": 2025, "community": community.upper(), "state_brackets": state, "regional_brackets": regional}

    return {"year": 2025, "state_brackets": state}


@router.post("/simulate/salary")
def salary_simulate(body: Optional[SalaryReq] = None):
    b = body or SalaryReq()
    return simulate_salary(b.gross_salary, b.community)


@router.get("/communities")
def list_communities():
    return [{"code": k, "name": v} for k, v in COMMUNITIES.items()]
