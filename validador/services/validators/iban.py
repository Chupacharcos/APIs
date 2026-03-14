def validate_iban(iban: str) -> dict:
    iban = iban.strip().upper().replace(" ", "").replace("-", "")

    if not iban.startswith("ES"):
        return {"valid": False, "type": "IBAN", "error": "Solo se admiten IBANs españoles (ES)"}

    if len(iban) != 24:
        return {"valid": False, "type": "IBAN", "error": f"El IBAN español debe tener 24 caracteres (recibidos: {len(iban)})"}

    # Reordenar: mover los 4 primeros al final
    rearranged = iban[4:] + iban[:4]

    # Convertir letras a números (A=10, B=11, ...)
    numeric = ""
    for c in rearranged:
        if c.isdigit():
            numeric += c
        else:
            numeric += str(ord(c) - ord("A") + 10)

    valid = int(numeric) % 97 == 1

    bank_code   = iban[4:8]
    branch_code = iban[8:12]
    check_digits = iban[12:14]
    account     = iban[14:]

    return {
        "valid": valid,
        "type": "IBAN",
        "country": "ES",
        "formatted": f"{iban[:4]} {iban[4:8]} {iban[8:12]} {iban[12:16]} {iban[16:20]} {iban[20:]}",
        "bank_code": bank_code,
        "branch_code": branch_code,
        "check_digits": check_digits,
        "account_number": account,
        "error": None if valid else "Checksum inválido (verificación módulo 97 fallida)",
    }
