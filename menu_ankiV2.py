import requests
import csv
import re
import unicodedata

URL = "http://localhost:8765"

# ==================================================
# FUNÇÃO GERAL PARA COMUNICAR COM O ANKI
# ==================================================

def anki_connect(action, params=None):

    if params is None:
        params = {}

    payload = {
        "action": action,
        "version": 6,
        "params": params
    }

    response = requests.post(URL, json=payload).json()

    return response["result"]

# ==================================================
# PEGAR TODOS OS DECKS
# ==================================================

def obter_decks():

    return anki_connect("deckNames")

# ==================================================
# ORGANIZAR ESTRUTURA
# ==================================================

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

# ==================================================
# MENU PRINCIPAL
# ==================================================

def menu_principal():

    print("\n==============================")
    print("        ANKI TJCE V2")
    print("==============================")
    print("1 - Importar flashcards")
    print("2 - Ver estatísticas")
    print("3 - Sair")

    escolha = input("\nEscolha uma opção: ")

    return escolha

# ==================================================
# MENU DISCIPLINAS
# ==================================================

def escolher_disciplina(estrutura):

    disciplinas = list(estrutura.keys())

    print("\n=== DISCIPLINAS ===\n")

    for i, disciplina in enumerate(disciplinas, start=1):
        print(f"{i} - {disciplina}")

    escolha = int(input("\nEscolha a disciplina: "))

    return disciplinas[escolha - 1]

# ==================================================
# MENU ASSUNTOS
# ==================================================

def escolher_assunto(estrutura, disciplina):

    assuntos = estrutura[disciplina]

    print(f"\n=== ASSUNTOS DE {disciplina} ===\n")

    for i, assunto in enumerate(assuntos, start=1):
        print(f"{i} - {assunto}")

    escolha = int(input("\nEscolha o assunto: "))

    return assuntos[escolha - 1]

# ==================================================
# LIMPAR TEXTO
# ==================================================

def limpar_texto(texto):

    texto = texto.strip()

    # Corrigir símbolos LaTeX comuns
    texto = texto.replace("$5^o$", "5º")
    texto = texto.replace("$2^o$", "2º")
    texto = texto.replace("$3^o$", "3º")

    # Corrigir padrões tipo §$2^o$
    texto = re.sub(r"\$([0-9]+)\^o\$", r"\1º", texto)

    return texto

# ==================================================
# GERAR TAGS AUTOMÁTICAS
# ==================================================

def gerar_tags(disciplina, assunto):

    def limpar_tag(texto):

        texto = texto.lower()

        # Remove acentos
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ASCII", "ignore").decode("utf-8")

        # Remove números e hífens iniciais
        texto = re.sub(r"^\d+\s*-\s*", "", texto)

        # Espaços viram _
        texto = texto.replace(" ", "_")

        return texto

    return [
        "tjce",
        limpar_tag(disciplina),
        limpar_tag(assunto)
    ]

# ==================================================
# VERIFICAR DUPLICIDADE
# ==================================================

def card_existe(deck, pergunta):

    query = f'deck:"{deck}" Front:"{pergunta}"'

    resultado = anki_connect(
        "findNotes",
        {
            "query": query
        }
    )

    return len(resultado) > 0

# ==================================================
# ADICIONAR FLASHCARD
# ==================================================

def adicionar_flashcard(deck, pergunta, resposta, tags):

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

    return anki_connect("addNote", payload)

# ==================================================
# IMPORTAR CSV
# ==================================================

def importar_csv(deck, disciplina, assunto):

    arquivo_csv = "flashcards.csv"

    adicionados = 0
    duplicados = 0
    erros = 0
    total = 0

    tags = gerar_tags(disciplina, assunto)

    with open(arquivo_csv, "r", encoding="utf-8-sig") as arquivo:

        leitor = csv.reader(arquivo, delimiter=",")

        for linha in leitor:

            if len(linha) >= 2:

                total += 1

                try:

                    pergunta = limpar_texto(linha[0])
                    resposta = limpar_texto(linha[1])

                    if card_existe(deck, pergunta):

                        duplicados += 1

                        print(f"[DUPLICADO] {pergunta[:60]}")

                        continue

                    adicionar_flashcard(
                        deck,
                        pergunta,
                        resposta,
                        tags
                    )

                    adicionados += 1

                    print(f"[ADICIONADO] Card {adicionados}")

                except Exception as erro:

                    erros += 1

                    print(f"[ERRO] {erro}")

    print("\n===================================")
    print("IMPORTAÇÃO FINALIZADA")
    print("===================================")

    print(f"Total no CSV: {total}")
    print(f"Adicionados: {adicionados}")
    print(f"Duplicados: {duplicados}")
    print(f"Erros: {erros}")

# ==================================================
# ESTATÍSTICAS
# ==================================================

def mostrar_estatisticas(estrutura):

    print("\n===================================")
    print("ESTATÍSTICAS")
    print("===================================")

    for disciplina in estrutura:

        deck_pai = f"TJCE::{disciplina}"

        # =====================================
        # TOTAL DE CARDS
        # =====================================

        cards = anki_connect(
            "findCards",
            {
                "query": f'deck:"{deck_pai}"'
            }
        )

        total_cards = len(cards)

        # =====================================
        # TOTAL DE ASSUNTOS
        # =====================================

        total_assuntos = len(estrutura[disciplina])

        # =====================================
        # REVISÕES PENDENTES
        # =====================================

        revisoes = anki_connect(
            "getDeckStats",
            {
                "decks": [deck_pai]
            }
        )

        revisoes_pendentes = 0

        try:

            revisoes_pendentes = revisoes[deck_pai]["review_count"]

        except:

            revisoes_pendentes = 0

        # =====================================
        # EXIBIÇÃO
        # =====================================

        print(f"\n{disciplina}")
        print(f"- {total_cards} cards")
        print(f"- {total_assuntos} assuntos")
        print(f"- {revisoes_pendentes} revisões pendentes")

# ==================================================
# IMPORTAR FLASHCARDS
# ==================================================

def importar_flashcards(estrutura):

    disciplina = escolher_disciplina(estrutura)

    assunto = escolher_assunto(estrutura, disciplina)

    deck_final = f"TJCE::{disciplina}::{assunto}"

    print("\n===================================")
    print("DECK ESCOLHIDO")
    print("===================================")
    print(deck_final)

    importar_csv(deck_final, disciplina, assunto)

# ==================================================
# EXECUÇÃO
# ==================================================

try:

    decks = obter_decks()

    estrutura = organizar_decks(decks)

    while True:

        escolha = menu_principal()

        if escolha == "1":

            importar_flashcards(estrutura)

        elif escolha == "2":

            mostrar_estatisticas(estrutura)

        elif escolha == "3":

            print("\nEncerrando aplicação...")
            break

        else:

            print("\nOpção inválida.")

except Exception as erro:

    print("\n===================================")
    print("ERRO")
    print("===================================")

    print(erro)

    print("\nVerifique:")
    print("- Se o Anki está aberto")
    print("- Se o AnkiConnect está instalado")
    print("- Se o arquivo flashcards.csv existe")