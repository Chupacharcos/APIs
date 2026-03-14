ENTITY_TYPES = {
    "A": "Sociedad Anónima",
    "B": "Sociedad de Responsabilidad Limitada",
    "C": "Sociedad Colectiva",
    "D": "Sociedad Comanditaria",
    "E": "Comunidad de Bienes",
    "F": "Sociedad Cooperativa",
    "G": "Asociación o Fundación",
    "H": "Comunidad de Propietarios",
    "J": "Sociedad Civil",
    "K": "Español menor de edad sin DNI",
    "L": "Español residente en el extranjero",
    "M": "Extranjero residente en España",
    "N": "Entidad Extranjera",
    "P": "Corporación Local",
    "Q": "Organismo Público",
    "R": "Congregaciones Religiosas",
    "S": "Órgano de la Administración del Estado",
    "U": "Unión Temporal de Empresas",
    "V": "Otros",
    "W": "Establecimiento permanente de entidad no residente",
}

LETTER_CONTROL = "JABCDEFGHI"


def validate_cif(cif: str) -> dict:
    cif = cif.strip().upper()

    if len(cif) != 9:
        return {"valid": False, "type": "CIF", "error": "CIF debe tener 9 caracteres"}

    entity_letter = cif[0]
    number_part = cif[1:-1]
    control = cif[-1]

    if entity_letter not in ENTITY_TYPES:
        return {"valid": False, "type": "CIF", "error": f"Letra de entidad inválida: {entity_letter}"}

    if not number_part.isdigit() or len(number_part) != 7:
        return {"valid": False, "type": "CIF", "error": "Formato inválido: se esperan 7 dígitos centrales"}

    # Suma posiciones impares (1-indexado: 1,3,5,7 → índices 0,2,4,6)
    odd_sum = 0
    for i in [0, 2, 4, 6]:
        d = int(number_part[i]) * 2
        odd_sum += d // 10 + d % 10

    # Suma posiciones pares (1-indexado: 2,4,6 → índices 1,3,5)
    even_sum = sum(int(number_part[i]) for i in [1, 3, 5])

    total = odd_sum + even_sum
    check_digit = (10 - (total % 10)) % 10
    check_letter = LETTER_CONTROL[check_digit]

    # Tipos que usan letra / dígito / cualquiera
    letter_types = set("KPQRSW")
    digit_types = set("ABEH")

    if entity_letter in letter_types:
        valid = control == check_letter
        expected = check_letter
    elif entity_letter in digit_types:
        valid = control == str(check_digit)
        expected = str(check_digit)
    else:
        valid = control in (str(check_digit), check_letter)
        expected = f"{check_digit} o {check_letter}"

    return {
        "valid": valid,
        "type": "CIF",
        "entity_type": ENTITY_TYPES[entity_letter],
        "entity_letter": entity_letter,
        "formatted": f"{entity_letter}{number_part}-{control}",
        "control_expected": expected,
        "control_given": control,
        "error": None if valid else f"Dígito/letra de control incorrecto. Esperado: {expected}",
    }
