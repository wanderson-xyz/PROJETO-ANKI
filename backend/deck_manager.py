from backend.anki_connect import anki_connect

def obter_decks():

    return anki_connect("deckNames")

def criar_arvore_decks(decks):

    arvore = {}

    for deck in decks:

        partes = deck.split("::")

        atual = arvore

        for parte in partes:

            if parte not in atual:
                atual[parte] = {}

            atual = atual[parte]

    return arvore