TABLE = "TRWAGMYFPDXBNJZSQVHLCKE"


def validate_nie(nie: str) -> dict:
    nie = nie.strip().upper()

    if len(nie) != 9:
        return {"valid": False, "type": "NIE", "error": "NIE debe tener 9 caracteres"}

    prefix = nie[0]
    if prefix not in "XYZ":
        return {"valid": False, "type": "NIE", "error": "El NIE debe comenzar con X, Y o Z"}

    middle = nie[1:-1]
    letter = nie[-1]

    if not middle.isdigit() or len(middle) != 7:
        return {"valid": False, "type": "NIE", "error": "Formato inválido"}

    prefix_digit = {"X": "0", "Y": "1", "Z": "2"}[prefix]
    number = int(prefix_digit + middle)
    expected = TABLE[number % 23]
    valid = letter == expected

    return {
        "valid": valid,
        "type": "NIE",
        "formatted": f"{prefix}{middle}-{letter}",
        "prefix": prefix,
        "number": middle,
        "letter": letter,
        "letter_expected": expected,
        "error": None if valid else f"Letra incorrecta. Esperada: {expected}, recibida: {letter}",
    }
