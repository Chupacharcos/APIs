"""
Calculadora IRPF 2025 + Cuotas Autónomo 2025.
Datos: tramos estatales + autonómicos, cuotas SS por tramo de rendimiento neto.
"""

COMMUNITIES = {
    "AN": "Andalucía",
    "AR": "Aragón",
    "AS": "Principado de Asturias",
    "IB": "Islas Baleares",
    "CN": "Canarias",
    "CB": "Cantabria",
    "CM": "Castilla-La Mancha",
    "CL": "Castilla y León",
    "CT": "Cataluña",
    "EX": "Extremadura",
    "GA": "Galicia",
    "MD": "Comunidad de Madrid",
    "MU": "Región de Murcia",
    "NC": "Comunidad Foral de Navarra",
    "PV": "País Vasco",
    "RJ": "La Rioja",
    "VC": "Comunidad Valenciana",
}

# Tramos estatales IRPF 2025 (base liquidable general)
STATE_BRACKETS = [
    (0,       12_450,  9.50),
    (12_450,  20_200, 12.00),
    (20_200,  35_200, 15.00),
    (35_200,  60_000, 18.50),
    (60_000, 300_000, 22.50),
    (300_000, float("inf"), 24.50),
]

# Tramos autonómicos IRPF 2025 — principales CC.AA.
REGIONAL_BRACKETS = {
    "MD": [
        (0,      12_450,  8.50),
        (12_450, 17_707, 10.70),
        (17_707, 33_007, 12.70),
        (33_007, 53_407, 17.20),
        (53_407, float("inf"), 20.50),
    ],
    "CT": [
        (0,       12_450, 10.50),
        (12_450,  17_707, 12.00),
        (17_707,  21_000, 14.00),
        (21_000,  33_000, 15.50),
        (33_000,  53_000, 18.50),
        (53_000,  90_000, 21.50),
        (90_000, 120_000, 23.50),
        (120_000, float("inf"), 25.50),
    ],
    "AN": [
        (0,      12_450,  9.50),
        (12_450, 20_200, 12.00),
        (20_200, 35_200, 14.50),
        (35_200, 60_000, 18.50),
        (60_000, float("inf"), 22.50),
    ],
    "VC": [
        (0,      12_450, 10.00),
        (12_450, 17_707, 12.00),
        (17_707, 33_007, 14.00),
        (33_007, 66_623, 20.00),
        (66_623, 166_623, 21.50),
        (166_623, float("inf"), 22.50),
    ],
    "GA": [
        (0,      12_450,  9.00),
        (12_450, 20_200, 11.65),
        (20_200, 35_200, 14.90),
        (35_200, 60_000, 18.40),
        (60_000, float("inf"), 22.50),
    ],
    "AR": [
        (0,      12_450,  9.50),
        (12_450, 20_200, 12.00),
        (20_200, 34_000, 14.50),
        (34_000, 50_000, 17.50),
        (50_000, 70_000, 19.50),
        (70_000, float("inf"), 21.50),
    ],
}
# Resto de CC.AA. usan tramos similares a los estatales
_default_regional = [
    (0,      12_450,  9.50),
    (12_450, 20_200, 12.00),
    (20_200, 35_200, 15.00),
    (35_200, 60_000, 18.50),
    (60_000, float("inf"), 22.50),
]
for _code in COMMUNITIES:
    if _code not in REGIONAL_BRACKETS:
        REGIONAL_BRACKETS[_code] = _default_regional


# Cuotas autónomo 2025 (RDL 13/2022): (rendimiento_min, rendimiento_max, cuota_min, cuota_max)
SS_AUTONOMO_2025 = [
    (0,           8_040,  225, 293),
    (8_040,      10_800,  250, 310),
    (10_800,     12_600,  267, 320),
    (12_600,     14_400,  291, 340),
    (14_400,     17_080,  294, 360),
    (17_080,     19_200,  310, 380),
    (19_200,     21_600,  319, 390),
    (21_600,     26_400,  333, 390),
    (26_400,     30_000,  352, 420),
    (30_000,     38_880,  370, 440),
    (38_880,     50_760,  390, 460),
    (50_760,     60_000,  420, 490),
    (60_000, float("inf"), 530, 530),
]


def _calc_tax(base: float, brackets: list) -> float:
    tax = 0.0
    for low, high, rate in brackets:
        if base <= low:
            break
        taxable = min(base, high) - low
        tax += taxable * rate / 100
    return round(tax, 2)


def get_ss_quota(net_annual: float) -> dict:
    for low, high, q_min, q_max in SS_AUTONOMO_2025:
        if net_annual <= high:
            return {"min": q_min, "max": q_max, "recommended": q_min}
    last = SS_AUTONOMO_2025[-1]
    return {"min": last[2], "max": last[3], "recommended": last[2]}


def simulate_autonomo(annual_invoiced: float, expenses: float = 0, community: str = "MD", irpf_rate: int = 15) -> dict:
    iva_to_declare  = round(annual_invoiced * 0.21, 2)
    net_before_ss   = round(annual_invoiced - expenses, 2)

    ss_info         = get_ss_quota(net_before_ss)
    ss_monthly      = ss_info["recommended"]
    ss_annual       = round(ss_monthly * 12, 2)

    irpf_base       = round(net_before_ss - ss_annual, 2)

    regional = REGIONAL_BRACKETS.get(community, _default_regional)
    state_tax    = _calc_tax(irpf_base, STATE_BRACKETS)
    regional_tax = _calc_tax(irpf_base, regional)
    irpf_total   = round(state_tax + regional_tax, 2)

    effective_rate = round((irpf_total / irpf_base * 100) if irpf_base > 0 else 0, 2)
    net_final      = round(irpf_base - irpf_total, 2)
    quarterly_wh   = round(irpf_base / 4 * irpf_rate / 100, 2)

    return {
        "gross_invoiced":       annual_invoiced,
        "iva_to_declare":       iva_to_declare,
        "deductible_expenses":  expenses,
        "net_before_ss":        net_before_ss,
        "ss_quota_monthly":     ss_monthly,
        "ss_quota_annual":      ss_annual,
        "irpf_base":            irpf_base,
        "state_tax":            state_tax,
        "regional_tax":         regional_tax,
        "irpf_total":           irpf_total,
        "irpf_effective_rate_pct": effective_rate,
        "net_final":            net_final,
        "monthly_net":          round(net_final / 12, 2),
        "quarterly_withholding_modelo130": quarterly_wh,
        "community":            COMMUNITIES.get(community, community),
        "year": 2025,
    }


def calculate_irpf(gross: float, community: str = "MD", deductions: float = 0) -> dict:
    taxable_base = round(gross - deductions, 2)
    regional     = REGIONAL_BRACKETS.get(community, _default_regional)
    state_tax    = _calc_tax(taxable_base, STATE_BRACKETS)
    regional_tax = _calc_tax(taxable_base, regional)
    total        = round(state_tax + regional_tax, 2)
    effective    = round((total / taxable_base * 100) if taxable_base > 0 else 0, 2)

    brackets_detail = []
    for low, high, rate in STATE_BRACKETS:
        if taxable_base <= low:
            break
        taxable = round(min(taxable_base, high) - low, 2)
        amount  = round(taxable * rate / 100, 2)
        if amount > 0:
            brackets_detail.append({
                "from": low, "to": None if high == float("inf") else high,
                "rate_pct": rate, "taxable": taxable, "tax": amount,
            })

    return {
        "gross":           gross,
        "deductions":      deductions,
        "taxable_base":    taxable_base,
        "state_tax":       state_tax,
        "regional_tax":    regional_tax,
        "total_tax":       total,
        "effective_rate_pct": effective,
        "net":             round(taxable_base - total, 2),
        "brackets_detail": brackets_detail,
        "community":       COMMUNITIES.get(community, community),
        "year": 2025,
    }


def simulate_salary(gross_salary: float, community: str = "MD") -> dict:
    worker_ss    = round(gross_salary * 0.0635, 2)   # contingencias + desempleo + formación
    employer_ss  = round(gross_salary * 0.2990, 2)   # ~30% coste empresa

    taxable_base = round(gross_salary - worker_ss, 2)
    regional     = REGIONAL_BRACKETS.get(community, _default_regional)
    irpf_total   = round(_calc_tax(taxable_base, STATE_BRACKETS) + _calc_tax(taxable_base, regional), 2)
    effective    = round((irpf_total / taxable_base * 100) if taxable_base > 0 else 0, 2)
    net_salary   = round(taxable_base - irpf_total, 2)

    return {
        "gross_salary":        gross_salary,
        "worker_ss":           worker_ss,
        "employer_ss":         employer_ss,
        "employer_total_cost": round(gross_salary + employer_ss, 2),
        "taxable_base":        taxable_base,
        "irpf_total":          irpf_total,
        "effective_rate_pct":  effective,
        "net_salary":          net_salary,
        "monthly_net":         round(net_salary / 12, 2),
        "community":           COMMUNITIES.get(community, community),
        "year": 2025,
    }
