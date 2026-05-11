import requests
import csv

URL = "http://localhost:8765"

# =========================
# PEGAR DECKS
# =========================

def obter_decks():

    payload = {
        "action": "deckNames",
        "version": 6
    }

    response = requests.post(URL, json=payload)

    resultado = response.json()

    return resultado["result"]

# =========================
# ORGANIZAR DECKS
# =========================

def organizar_decks(decks):

    estrutura = {}

    for deck in decks:

        partes = deck.split("::")

        # Queremos:
        # TJCE::Disciplina::Assunto

        if len(partes) == 3:

            concurso = partes[0]
            disciplina = partes[1]
            assunto = partes[2]

            if disciplina not in estrutura:
                estrutura[disciplina] = []

            estrutura[disciplina].append(assunto)

    return estrutura

# =========================
# MENU DISCIPLINAS
# =========================

def escolher_disciplina(estrutura):

    disciplinas = list(estrutura.keys())

    print("\n=== DISCIPLINAS ===\n")

    for i, disciplina in enumerate(disciplinas, start=1):
        print(f"{i} - {disciplina}")

    escolha = int(input("\nEscolha a disciplina: "))

    return disciplinas[escolha - 1]

# =========================
# MENU ASSUNTOS
# =========================

def escolher_assunto(estrutura, disciplina):

    assuntos = estrutura[disciplina]

    print(f"\n=== ASSUNTOS DE {disciplina} ===\n")

    for i, assunto in enumerate(assuntos, start=1):
        print(f"{i} - {assunto}")

    escolha = int(input("\nEscolha o assunto: "))

    return assuntos[escolha - 1]

# =========================
# CRIAR FLASHCARD
# =========================

def adicionar_flashcard(deck, pergunta, resposta):

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck,
                "modelName": "Basic",
                "fields": {
                    "Front": pergunta,
                    "Back": resposta
                },
                "tags": [
                    "tjce"
                ]
            }
        }
    }

    response = requests.post(URL, json=payload)

    return response.json()

# =========================
# IMPORTAR TXT
# =========================

def importar_txt(deck):

    arquivo_txt = "flashcards.csv"

    contador = 0

    with open(arquivo_txt, "r", encoding="utf-8-sig") as arquivo:

        leitor = csv.reader(arquivo, delimiter=",")

        for linha in leitor:

            if len(linha) >= 2:

                pergunta = linha[0]
                resposta = linha[1]

                adicionar_flashcard(deck, pergunta, resposta)

                contador += 1

                print(f"Card {contador} criado.")

    print(f"\n{contador} flashcards importados com sucesso!")

# =========================
# EXECUÇÃO
# =========================

try:

    decks = obter_decks()

    estrutura = organizar_decks(decks)

    disciplina = escolher_disciplina(estrutura)

    assunto = escolher_assunto(estrutura, disciplina)

    deck_final = f"TJCE::{disciplina}::{assunto}"

    print("\n==========================")
    print("DECK ESCOLHIDO:")
    print(deck_final)
    print("==========================")

    importar_txt(deck_final)

except Exception as erro:

    print("\nERRO:")
    print(erro)

    print("\nVerifique:")
    print("- Se o Anki está aberto")
    print("- Se o arquivo flashcards.txt existe")