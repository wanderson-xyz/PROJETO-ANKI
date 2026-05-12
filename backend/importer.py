import csv

from backend.anki_connect import anki_connect
from backend.utils import limpar_texto
from backend.utils import limpar_tag

def gerar_tags(deck):

    partes = deck.split("::")

    tags = []

    for parte in partes:

        tags.append(
            limpar_tag(parte)
        )

    return tags

def card_existe(deck, pergunta):

    query = f'deck:"{deck}" Front:"{pergunta}"'

    resultado = anki_connect(
        "findNotes",
        {
            "query": query
        }
    )

    return len(resultado) > 0

def adicionar_flashcard(
    deck,
    pergunta,
    resposta,
    tags
):

    payload = {
        "note": {
            "deckName": deck,
            "modelName": "Basic",
            "fields": {
                "Front": pergunta,
                "Back": resposta
            },
            "tags": tags
        }
    }

    return anki_connect(
        "addNote",
        payload
    )

def importar_csv(
    deck,
    arquivo_csv,
    callback=None
):

    adicionados = 0
    duplicados = 0
    erros = 0

    tags = gerar_tags(deck)

    with open(
        arquivo_csv,
        "r",
        encoding="utf-8-sig"
    ) as arquivo:

        leitor = csv.reader(
            arquivo,
            delimiter=","
        )

        linhas = list(leitor)

        total = len(linhas)

        for i, linha in enumerate(linhas):

            if len(linha) >= 2:

                try:

                    pergunta = limpar_texto(
                        linha[0]
                    )

                    resposta = limpar_texto(
                        linha[1]
                    )

                    if card_existe(deck, pergunta):

                        duplicados += 1

                        status = "duplicado"

                    else:

                        adicionar_flashcard(
                            deck,
                            pergunta,
                            resposta,
                            tags
                        )

                        adicionados += 1

                        status = "adicionado"

                    progresso = (
                        (i + 1) / total
                    ) * 100

                    if callback:

                        callback(
                            progresso,
                            status,
                            pergunta
                        )

                except Exception:

                    erros += 1

    return {
        "adicionados": adicionados,
        "duplicados": duplicados,
        "erros": erros
    }