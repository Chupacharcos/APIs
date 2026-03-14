TABLE = "TRWAGMYFPDXBNJZSQVHLCKE"


def validate_nif(nif: str) -> dict:
    nif = nif.strip().upper()

    if len(nif) != 9:
        return {"valid": False, "type": "NIF", "error": "NIF debe tener 9 caracteres"}

    number_part = nif[:-1]
    letter = nif[-1]

    if not number_part.isdigit():
        return {"valid": False, "type": "NIF", "error": "Formato inválido: los 8 primeros caracteres deben ser dígitos"}

    expected = TABLE[int(number_part) % 23]
    valid = letter == expected

    return {
        "valid": valid,
        "type": "NIF",
        "formatted": f"{number_part}-{letter}",
        "number": number_part,
        "letter": letter,
        "letter_expected": expected,
        "error": None if valid else f"Letra incorrecta. Esperada: {expected}, recibida: {letter}",
    }
