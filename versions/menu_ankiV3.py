import requests
import csv
import re
import unicodedata
import os

URL = "http://localhost:8765"

# ==================================================
# CONEXÃO COM ANKI
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
# CRIAR ÁRVORE HIERÁRQUICA
# ==================================================

def criar_arvore(decks):

    arvore = {}

    for deck in decks:

        partes = deck.split("::")

        atual = arvore

        for parte in partes:

            if parte not in atual:
                atual[parte] = {}

            atual = atual[parte]

    return arvore

# ==================================================
# LISTAR CSVs AUTOMATICAMENTE
# ==================================================

def listar_csvs():

    pasta_atual = os.path.dirname(os.path.abspath(__file__))

    arquivos = os.listdir(pasta_atual)

    csvs = [f for f in arquivos if f.endswith(".csv")]

    return csvs, pasta_atual

# ==================================================
# ESCOLHER CSV
# ==================================================

def escolher_csv():

    csvs, pasta = listar_csvs()

    if not csvs:

        print("\nNenhum CSV encontrado na pasta do script.")
        return None

    print("\n===================================")
    print("CSV DISPONÍVEIS")
    print("===================================\n")

    for i, arquivo in enumerate(csvs, start=1):
        print(f"{i} - {arquivo}")

    escolha = input("\nEscolha o CSV: ")

    try:

        arquivo = csvs[int(escolha) - 1]

        return os.path.join(pasta, arquivo)

    except:

        print("\nOpção inválida.")
        return None

# ==================================================
# MENU DE NAVEGAÇÃO
# ==================================================

def navegar_arvore(arvore):

    caminho = []
    atual = arvore

    while True:

        opcoes = list(atual.keys())

        if len(opcoes) == 0:
            break

        print("\n===================================")

        if len(caminho) == 0:
            print("RAIZ")
        else:
            print(" > ".join(caminho))

        print("===================================\n")

        for i, opcao in enumerate(opcoes, start=1):
            print(f"{i} - {opcao}")

        print("\n0 - Selecionar este deck")

        escolha = input("\nEscolha uma opção: ")

        if escolha == "0":

            if len(caminho) == 0:
                print("\nVocê não pode selecionar a raiz.")
                continue

            return "::".join(caminho)

        try:

            escolha = int(escolha)

            selecionado = opcoes[escolha - 1]

            caminho.append(selecionado)

            atual = atual[selecionado]

        except:

            print("\nOpção inválida.")

# ==================================================
# LIMPAR TEXTO
# ==================================================

def limpar_texto(texto):

    texto = texto.strip()

    texto = re.sub(r"\s+", " ", texto)

    texto = re.sub(r"\$([0-9]+)\^o\$", r"\1º", texto)

    texto = texto.replace("$", "")

    texto = texto.replace("–", "-")
    texto = texto.replace("—", "-")

    texto = re.sub(r"\s+([.,;:!?])", r"\1", texto)

    return texto

# ==================================================
# GERAR TAGS
# ==================================================

def gerar_tags(deck):

    partes = deck.split("::")

    tags = ["tjce"]

    for parte in partes:

        texto = parte.lower()

        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ASCII", "ignore").decode("utf-8")

        texto = re.sub(r"^\d+\s*-\s*", "", texto)

        texto = texto.replace(" ", "_")

        tags.append(texto)

    return tags

# ==================================================
# DUPLICIDADE
# ==================================================

def card_existe(deck, pergunta):

    query = f'deck:"{deck}" Front:"{pergunta}"'

    resultado = anki_connect(
        "findNotes",
        {"query": query}
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
# IMPORTAR CSV (DINÂMICO)
# ==================================================

def importar_csv(deck, arquivo_csv):

    adicionados = 0
    duplicados = 0
    erros = 0
    total = 0

    tags = gerar_tags(deck)

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

                    adicionar_flashcard(deck, pergunta, resposta, tags)

                    adicionados += 1
                    print(f"[ADICIONADO] {adicionados}")

                except Exception as erro:

                    erros += 1
                    print(f"[ERRO] {erro}")

    print("\n===================================")
    print("IMPORTAÇÃO FINALIZADA")
    print("===================================")

    print(f"Total: {total}")
    print(f"Adicionados: {adicionados}")
    print(f"Duplicados: {duplicados}")
    print(f"Erros: {erros}")

# ==================================================
# ESTATÍSTICAS
# ==================================================

def mostrar_estatisticas(decks):

    print("\n===================================")
    print("ESTATÍSTICAS")
    print("===================================")

    disciplinas = {}

    for deck in decks:

        partes = deck.split("::")

        if partes[0] != "TJCE":
            continue

        if len(partes) >= 2:

            disciplina = partes[1]

            if disciplina not in disciplinas:
                disciplinas[disciplina] = {"assuntos": set()}

            if len(partes) == 3:
                disciplinas[disciplina]["assuntos"].add(partes[2])

    for disciplina in disciplinas:

        deck_pai = f"TJCE::{disciplina}"

        cards = anki_connect(
            "findCards",
            {"query": f'deck:"{deck_pai}"'}
        )

        total_cards = len(cards)

        total_assuntos = len(disciplinas[disciplina]["assuntos"])

        stats = anki_connect(
            "getDeckStats",
            {"decks": [deck_pai]}
        )

        revisoes = 0

        try:
            revisoes = stats[deck_pai]["review_count"]
        except:
            revisoes = 0

        print(f"\n{disciplina}")
        print(f"- {total_cards} cards")
        print(f"- {total_assuntos} assuntos")
        print(f"- {revisoes} revisões pendentes")

# ==================================================
# MENU
# ==================================================

def menu_principal():

    print("\n===================================")
    print("ANKI TJCE V3.1")
    print("===================================")
    print("1 - Importar flashcards")
    print("2 - Ver estatísticas")
    print("3 - Sair")

    return input("\nEscolha uma opção: ")

# ==================================================
# EXECUÇÃO
# ==================================================

try:

    decks = obter_decks()
    arvore = criar_arvore(decks)

    while True:

        escolha = menu_principal()

        if escolha == "1":

            deck_escolhido = navegar_arvore(arvore)

            if not deck_escolhido:
                continue

            print("\nDECK:", deck_escolhido)

            arquivo_csv = escolher_csv()

            if arquivo_csv:
                importar_csv(deck_escolhido, arquivo_csv)

        elif escolha == "2":
            mostrar_estatisticas(decks)

        elif escolha == "3":
            print("\nEncerrando...")
            break

        else:
            print("\nOpção inválida.")

except Exception as erro:

    print("\nERRO:")
    print(erro)