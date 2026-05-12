import re
import unicodedata

def limpar_texto(texto):

    texto = texto.strip()

    texto = re.sub(r"\s+", " ", texto)

    texto = re.sub(
        r"\$([0-9]+)\^o\$",
        r"\1º",
        texto
    )

    texto = texto.replace("$", "")

    return texto

def limpar_tag(texto):

    texto = texto.lower()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = texto.encode(
        "ASCII",
        "ignore"
    ).decode("utf-8")

    texto = texto.replace(" ", "_")

    return texto