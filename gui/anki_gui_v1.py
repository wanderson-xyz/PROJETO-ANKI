import customtkinter as ctk
from tkinter import filedialog
import requests
import csv
import re
import unicodedata
from tkinter import messagebox
import threading

# ==================================================
# CONFIGURAÇÕES
# ==================================================

URL = "http://localhost:8765"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
# PEGAR DECKS
# ==================================================

def obter_decks():

    return anki_connect("deckNames")

# ==================================================
# CRIAR ÁRVORE
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
# LIMPAR TEXTO
# ==================================================

def limpar_texto(texto):

    texto = texto.strip()

    texto = re.sub(r"\s+", " ", texto)

    texto = re.sub(r"\$([0-9]+)\^o\$", r"\1º", texto)

    texto = texto.replace("$", "")

    return texto

# ==================================================
# GERAR TAGS
# ==================================================

def gerar_tags(deck):

    partes = deck.split("::")

    tags = ["anki_gui"]

    for parte in partes:

        texto = parte.lower()

        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ASCII", "ignore").decode("utf-8")

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
        {
            "query": query
        }
    )

    return len(resultado) > 0

# ==================================================
# ADICIONAR CARD
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

def importar_csv(deck, arquivo_csv):

    adicionados = 0
    duplicados = 0
    erros = 0

    tags = gerar_tags(deck)

    # =========================
    # LOG INICIAL
    # =========================

    adicionar_log("===================================")
    adicionar_log("INICIANDO IMPORTAÇÃO")
    adicionar_log(f"Deck: {deck}")
    adicionar_log("===================================")

    with open(arquivo_csv, "r", encoding="utf-8-sig") as arquivo:

        leitor = csv.reader(arquivo, delimiter=",")

        for linha in leitor:

            if len(linha) >= 2:

                try:

                    pergunta = limpar_texto(linha[0])
                    resposta = limpar_texto(linha[1])

                    if card_existe(deck, pergunta):

                        duplicados += 1

                        adicionar_log(
                            f"[DUPLICADO] {pergunta[:60]}"
                        )

                        continue

                    adicionar_flashcard(
                        deck,
                        pergunta,
                        resposta,
                        tags
                    )

                    adicionados += 1

                    adicionar_log(
                        f"[ADICIONADO] {pergunta[:60]}"
                    )

                except Exception as erro:

                    erros += 1

                    adicionar_log(f"[ERRO] {erro}")

    # =========================
    # LOG FINAL
    # =========================

    adicionar_log("===================================")
    adicionar_log("IMPORTAÇÃO FINALIZADA")
    adicionar_log(f"Adicionados: {adicionados}")
    adicionar_log(f"Duplicados: {duplicados}")
    adicionar_log(f"Erros: {erros}")
    adicionar_log("===================================")

    # =========================
    # POPUP
    # =========================

    messagebox.showinfo(
        "Importação concluída",
        f"Adicionados: {adicionados}\n"
        f"Duplicados: {duplicados}\n"
        f"Erros: {erros}"
    )

# ==================================================
# LOGS
# ==================================================

def adicionar_log(texto):

    log_box.insert("end", texto + "\n")

    log_box.see("end")

    # FORÇA atualização visual da GUI
    app.update_idletasks()

# ==================================================
# ATUALIZAR LISTA DE DECKS
# ==================================================

def atualizar_decks():

    try:

        decks = obter_decks()

        deck_menu.configure(values=decks)

        if len(decks) > 0:
            deck_menu.set(decks[0])

        adicionar_log("Decks carregados com sucesso.")

    except Exception as erro:

        messagebox.showerror(
            "Erro",
            f"Erro ao conectar ao Anki:\n{erro}"
        )

# ==================================================
# SELECIONAR CSV
# ==================================================

def selecionar_csv():

    arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=[("Arquivos CSV", "*.csv")]
    )

    if arquivo:

        arquivo_label.configure(text=arquivo)

        app.arquivo_csv = arquivo

        adicionar_log(f"CSV selecionado: {arquivo}")

# ==================================================
# IMPORTAR
# ==================================================

def importar_flashcards():

    if not hasattr(app, "arquivo_csv"):

        messagebox.showwarning(
            "Aviso",
            "Selecione um arquivo CSV primeiro."
        )

        return

    deck = deck_menu.get()

    adicionar_log(f"Importando para: {deck}")

    # RODA EM THREAD SEPARADA
    thread = threading.Thread(
        target=importar_csv,
        args=(deck, app.arquivo_csv)
    )

    thread.start()

# ==================================================
# JANELA PRINCIPAL
# ==================================================

app = ctk.CTk()

app.title("ANKI TJCE GUI")

app.geometry("1200x700")

# ==================================================
# TÍTULO
# ==================================================

titulo = ctk.CTkLabel(
    app,
    text="ANKI TJCE GUI",
    font=("Arial", 32, "bold")
)

titulo.pack(pady=20)

# ==================================================
# FRAME PRINCIPAL
# ==================================================

main_frame = ctk.CTkFrame(app)

main_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=20
)

# ==================================================
# SELECT DECK
# ==================================================

deck_label = ctk.CTkLabel(
    main_frame,
    text="Selecione o deck:"
)

deck_label.pack(pady=(20, 5))


deck_menu = ctk.CTkComboBox(
    main_frame,
    width=600
)

deck_menu.pack(pady=10)

# ==================================================
# BOTÃO CARREGAR
# ==================================================

botao_carregar = ctk.CTkButton(
    main_frame,
    text="Atualizar Decks",
    command=atualizar_decks
)

botao_carregar.pack(pady=10)

# ==================================================
# SELECIONAR CSV
# ==================================================

botao_csv = ctk.CTkButton(
    main_frame,
    text="Selecionar CSV",
    command=selecionar_csv
)

botao_csv.pack(pady=10)

arquivo_label = ctk.CTkLabel(
    main_frame,
    text="Nenhum arquivo selecionado"
)

arquivo_label.pack(pady=10)

# ==================================================
# IMPORTAR
# ==================================================

botao_importar = ctk.CTkButton(
    main_frame,
    text="Importar Flashcards",
    height=50,
    command=importar_flashcards
)

botao_importar.pack(pady=20)

# ==================================================
# LOGS
# ==================================================

log_label = ctk.CTkLabel(
    main_frame,
    text="Logs"
)

log_label.pack(pady=(20, 5))

log_box = ctk.CTkTextbox(
    main_frame,
    width=1000,
    height=250
)

log_box.pack(pady=10)

# ==================================================
# INICIAR
# ==================================================

atualizar_decks()

app.mainloop()
