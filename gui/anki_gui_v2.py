import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
import threading

from backend.deck_manager import obter_decks
from backend.deck_manager import criar_arvore_decks
from backend.importer import importar_csv

# ==================================================
# CONFIG GUI
# ==================================================

ctk.set_appearance_mode("dark")

ctk.set_default_color_theme("blue")

# ==================================================
# ESTADO GLOBAL
# ==================================================

arquivo_csv = None

arvore_decks = {}

# ==================================================
# INICIAR APP
# ==================================================

def iniciar_app():

    global app
    global concurso_combo
    global disciplina_combo
    global assunto_combo
    global subassunto_combo
    global progressbar
    global progresso_label
    global status_label
    global log_box
    global arquivo_label
    global botao_importar

    # ==================================================
    # APP
    # ==================================================

    app = ctk.CTk()

    app.title("ANKI IMPORTER V2")

    app.geometry("1400x900")

    # ==================================================
    # FUNÇÕES AUXILIARES
    # ==================================================

    def adicionar_log(texto):

        log_box.insert("end", texto + "\n")

        log_box.see("end")

        app.update_idletasks()

    def atualizar_status(texto):

        status_label.configure(
            text=f"STATUS: {texto}"
        )

    def atualizar_progresso(valor):

        progressbar.set(valor / 100)

        progresso_label.configure(
            text=f"{valor:.1f}%"
        )

    # ==================================================
    # CARREGAR DECKS
    # ==================================================

    def carregar_decks():

        global arvore_decks

        decks = obter_decks()

        arvore_decks = criar_arvore_decks(decks)

        concursos = list(arvore_decks.keys())

        concurso_combo.configure(
            values=concursos
        )

        if concursos:

            concurso_combo.set(
                concursos[0]
            )

            atualizar_disciplinas(
                concursos[0]
            )

    # ==================================================
    # CONCURSO
    # ==================================================

    def atualizar_disciplinas(concurso):

        disciplinas = list(
            arvore_decks[concurso].keys()
        )

        disciplina_combo.configure(
            values=disciplinas
        )

        if disciplinas:

            disciplina_combo.set(
                disciplinas[0]
            )

            atualizar_assuntos(
                disciplinas[0]
            )

    # ==================================================
    # DISCIPLINA
    # ==================================================

    def atualizar_assuntos(disciplina):

        concurso = concurso_combo.get()

        assuntos = list(
            arvore_decks[concurso][disciplina].keys()
        )

        assunto_combo.configure(
            values=assuntos
        )

        if assuntos:

            assunto_combo.set(
                assuntos[0]
            )

            atualizar_subassuntos(
                assuntos[0]
            )

    # ==================================================
    # ASSUNTO
    # ==================================================

    def atualizar_subassuntos(assunto):

        concurso = concurso_combo.get()

        disciplina = disciplina_combo.get()

        subassuntos = list(
            arvore_decks
            [concurso]
            [disciplina]
            [assunto]
            .keys()
        )

        if len(subassuntos) == 0:

            subassuntos = ["SEM SUBASSUNTO"]

        subassunto_combo.configure(
            values=subassuntos
        )

        subassunto_combo.set(
            subassuntos[0]
        )

    # ==================================================
    # MONTAR DECK FINAL
    # ==================================================

    def obter_deck_final():

        concurso = concurso_combo.get()

        disciplina = disciplina_combo.get()

        assunto = assunto_combo.get()

        subassunto = subassunto_combo.get()

        if subassunto == "SEM SUBASSUNTO":

            return (
                f"{concurso}::"
                f"{disciplina}::"
                f"{assunto}"
            )

        return (
            f"{concurso}::"
            f"{disciplina}::"
            f"{assunto}::"
            f"{subassunto}"
        )
    
    def reset_ui():

        log_box.delete("1.0", "end")

        progressbar.set(0)
        progresso_label.configure(text="0%")

        atualizar_status("AGUARDANDO")

        arquivo_label.configure(text="Nenhum CSV selecionado")

    # ==================================================
    # CSV
    # ==================================================

    def selecionar_csv():

        global arquivo_csv

        arquivo = filedialog.askopenfilename(

            title="Selecione CSV",

            filetypes=[
                ("Arquivos CSV", "*.csv")
            ]
        )

        if arquivo:

            arquivo_csv = arquivo

            arquivo_label.configure(
                text=arquivo
            )

            adicionar_log(
                f"CSV selecionado: {arquivo}"
            )

    # ==================================================
    # CALLBACK IMPORTAÇÃO
    # ==================================================

    def callback_importacao(
        progresso,
        status,
        pergunta
    ):

        atualizar_progresso(
            progresso
        )

        adicionar_log(
            f"[{status.upper()}] "
            f"{pergunta[:80]}"
        )

    # ==================================================
    # THREAD IMPORTAÇÃO
    # ==================================================

    def iniciar_importacao():

        global arquivo_csv

        if not arquivo_csv:

            messagebox.showwarning(
                "Aviso",
                "Selecione um CSV."
            )

            return

        botao_importar.configure(
            state="disabled"
        )

        atualizar_status(
            "IMPORTANDO..."
        )

        progressbar.set(0)

        deck = obter_deck_final()

        adicionar_log(
            "================================="
        )

        adicionar_log(
            "IMPORTANDO PARA:"
        )

        adicionar_log(deck)

        adicionar_log(
            "================================="
        )

        thread = threading.Thread(
            target=executar_importacao,
            args=(deck,)
        )

        thread.daemon = True

        thread.start()

    # ==================================================
    # EXECUTAR IMPORTAÇÃO
    # ==================================================

    def executar_importacao(deck):

        global arquivo_csv

        resultado = importar_csv(
            deck,
            arquivo_csv,
            callback_importacao
        )

        adicionar_log(
            "================================="
        )

        adicionar_log(
            "IMPORTAÇÃO FINALIZADA"
        )

        adicionar_log(
            f"Adicionados: "
            f"{resultado['adicionados']}"
        )

        adicionar_log(
            f"Duplicados: "
            f"{resultado['duplicados']}"
        )

        adicionar_log(
            f"Erros: "
            f"{resultado['erros']}"
        )

        adicionar_log(
            "================================="
        )

        atualizar_status(
            "FINALIZADO"
        )

        botao_importar.configure(
            state="normal"
        )
        concurso_combo.configure(state="normal")
        disciplina_combo.configure(state="normal")
        assunto_combo.configure(state="normal")
        subassunto_combo.configure(state="normal")

    # ==================================================
    # GRID
    # ==================================================

    app.grid_rowconfigure(
        1,
        weight=1
    )

    app.grid_columnconfigure(
        1,
        weight=1
    )

    # ==================================================
    # TÍTULO
    # ==================================================

    titulo = ctk.CTkLabel(

        app,

        text="ANKI IMPORTER V2",

        font=(
            "Arial",
            34,
            "bold"
        )
    )

    titulo.grid(
        row=0,
        column=0,
        columnspan=2,
        pady=20
    )

    # ==================================================
    # SIDEBAR
    # ==================================================

    sidebar = ctk.CTkFrame(
        app,
        width=300
    )

    sidebar.grid(
        row=1,
        column=0,
        sticky="ns",
        padx=20,
        pady=20
    )

    # ==================================================
    # CONCURSO
    # ==================================================

    ctk.CTkLabel(
        sidebar,
        text="CONCURSO"
    ).pack(pady=(20, 5))

    concurso_combo = ctk.CTkComboBox(
        sidebar,
        command=atualizar_disciplinas
    )

    concurso_combo.pack(
        padx=20,
        pady=5
    )

    # ==================================================
    # DISCIPLINA
    # ==================================================

    ctk.CTkLabel(
        sidebar,
        text="DISCIPLINA"
    ).pack(pady=(20, 5))

    disciplina_combo = ctk.CTkComboBox(
        sidebar,
        command=atualizar_assuntos
    )

    disciplina_combo.pack(
        padx=20,
        pady=5
    )

    # ==================================================
    # ASSUNTO
    # ==================================================

    ctk.CTkLabel(
        sidebar,
        text="ASSUNTO"
    ).pack(pady=(20, 5))

    assunto_combo = ctk.CTkComboBox(
        sidebar,
        command=atualizar_subassuntos
    )

    assunto_combo.pack(
        padx=20,
        pady=5
    )

    # ==================================================
    # SUBASSUNTO
    # ==================================================

    ctk.CTkLabel(
        sidebar,
        text="SUBASSUNTO"
    ).pack(pady=(20, 5))

    subassunto_combo = ctk.CTkComboBox(
        sidebar
    )

    subassunto_combo.pack(
        padx=20,
        pady=5
    )

    # ==================================================
    # ÁREA CENTRAL
    # ==================================================

    main_frame = ctk.CTkFrame(app)

    main_frame.grid(
        row=1,
        column=1,
        sticky="nsew",
        padx=20,
        pady=20
    )

    # ==================================================
    # BOTÃO CSV
    # ==================================================

    botao_csv = ctk.CTkButton(

        main_frame,

        text="Selecionar CSV",

        height=50,

        command=selecionar_csv
    )

    botao_csv.pack(
        pady=(30, 10)
    )

    botao_reset = ctk.CTkButton(
        main_frame,
        text="RESETAR",
        fg_color="red",
        command=reset_ui
    )

    botao_reset.pack(pady=10)

    arquivo_label = ctk.CTkLabel(

        main_frame,

        text="Nenhum CSV selecionado"
    )

    arquivo_label.pack()

    # ==================================================
    # BOTÃO IMPORTAR
    # ==================================================

    botao_importar = ctk.CTkButton(

        main_frame,

        text="IMPORTAR FLASHCARDS",

        height=60,

        font=(
            "Arial",
            18,
            "bold"
        ),

        command=iniciar_importacao
    )

    botao_importar.pack(
        pady=30
    )

    # ==================================================
    # STATUS
    # ==================================================

    status_label = ctk.CTkLabel(

        main_frame,

        text="STATUS: AGUARDANDO",

        font=(
            "Arial",
            18,
            "bold"
        )
    )

    status_label.pack(
        pady=10
    )

    # ==================================================
    # PROGRESSO
    # ==================================================

    progressbar = ctk.CTkProgressBar(
        main_frame,
        width=700
    )

    progressbar.pack(
        pady=20
    )

    progressbar.set(0)

    progresso_label = ctk.CTkLabel(

        main_frame,

        text="0%"
    )

    progresso_label.pack()

    # ==================================================
    # LOGS
    # ==================================================

    log_box = ctk.CTkTextbox(
        main_frame,
        width=1000,
        height=350
    )

    log_box.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    # ==================================================
    # INICIAR
    # ==================================================

    carregar_decks()

    app.mainloop()