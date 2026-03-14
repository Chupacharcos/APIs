PROVINCES = {
    "01": "Álava",           "02": "Albacete",       "03": "Alicante",
    "04": "Almería",         "05": "Ávila",           "06": "Badajoz",
    "07": "Islas Baleares",  "08": "Barcelona",       "09": "Burgos",
    "10": "Cáceres",         "11": "Cádiz",           "12": "Castellón",
    "13": "Ciudad Real",     "14": "Córdoba",         "15": "A Coruña",
    "16": "Cuenca",          "17": "Girona",          "18": "Granada",
    "19": "Guadalajara",     "20": "Gipuzkoa",        "21": "Huelva",
    "22": "Huesca",          "23": "Jaén",            "24": "León",
    "25": "Lleida",          "26": "La Rioja",        "27": "Lugo",
    "28": "Madrid",          "29": "Málaga",          "30": "Murcia",
    "31": "Navarra",         "32": "Ourense",         "33": "Asturias",
    "34": "Palencia",        "35": "Las Palmas",      "36": "Pontevedra",
    "37": "Salamanca",       "38": "Sta. Cruz Tenerife", "39": "Cantabria",
    "40": "Segovia",         "41": "Sevilla",         "42": "Soria",
    "43": "Tarragona",       "44": "Teruel",          "45": "Toledo",
    "46": "Valencia",        "47": "Valladolid",      "48": "Bizkaia",
    "49": "Zamora",          "50": "Zaragoza",        "51": "Ceuta",
    "52": "Melilla",
}

CCAA = {
    "01": "País Vasco",          "02": "Castilla-La Mancha",   "03": "Com. Valenciana",
    "04": "Andalucía",           "05": "Castilla y León",      "06": "Extremadura",
    "07": "Islas Baleares",      "08": "Cataluña",             "09": "Castilla y León",
    "10": "Extremadura",         "11": "Andalucía",            "12": "Com. Valenciana",
    "13": "Castilla-La Mancha",  "14": "Andalucía",            "15": "Galicia",
    "16": "Castilla-La Mancha",  "17": "Cataluña",             "18": "Andalucía",
    "19": "Castilla-La Mancha",  "20": "País Vasco",           "21": "Andalucía",
    "22": "Aragón",              "23": "Andalucía",            "24": "Castilla y León",
    "25": "Cataluña",            "26": "La Rioja",             "27": "Galicia",
    "28": "Comunidad de Madrid", "29": "Andalucía",            "30": "Región de Murcia",
    "31": "Navarra",             "32": "Galicia",              "33": "Principado de Asturias",
    "34": "Castilla y León",     "35": "Canarias",             "36": "Galicia",
    "37": "Castilla y León",     "38": "Canarias",             "39": "Cantabria",
    "40": "Castilla y León",     "41": "Andalucía",            "42": "Castilla y León",
    "43": "Cataluña",            "44": "Aragón",               "45": "Castilla-La Mancha",
    "46": "Com. Valenciana",     "47": "Castilla y León",      "48": "País Vasco",
    "49": "Castilla y León",     "50": "Aragón",               "51": "Ceuta",
    "52": "Melilla",
}


def validate_postal(postal: str) -> dict:
    postal = postal.strip()

    if not postal.isdigit():
        return {"valid": False, "type": "POSTAL", "error": "El código postal debe ser numérico"}

    if len(postal) != 5:
        return {"valid": False, "type": "POSTAL", "error": f"El código postal español tiene 5 dígitos (recibidos: {len(postal)})"}

    province_code = postal[:2]

    if province_code not in PROVINCES:
        return {"valid": False, "type": "POSTAL", "error": f"Código de provincia inválido: {province_code}"}

    return {
        "valid": True,
        "type": "POSTAL",
        "postal_code": postal,
        "province_code": province_code,
        "province": PROVINCES[province_code],
        "ccaa": CCAA.get(province_code, "Desconocida"),
        "error": None,
    }
