from tkinter import *
from PIL import Image, ImageTk

class TelaCreditos:
    def __init__(self, root: Tk, show_screen, destino_voltar="inicial"):
        self.show_screen = show_screen
        self.destino_voltar = destino_voltar  # Novo parâmetro

        # Frame principal
        self.frame = Frame(root)
        self.frame.pack(expand=True, fill='both')

        # Canvas
        self.canvas = Canvas(
            self.frame,
            width=1080,
            height=720,
            highlightthickness=0,
            bg='#352314'
        )
        self.canvas.pack()

        # Título "Créditos"
        self.canvas.create_text(
            540,
            60,
            text="Créditos",
            fill="white",
            font=('Aclonica', 32, 'bold')
        )

        # Logo do Splendor
        logo = Image.open("resources/extra/logo.png")
        logo = logo.resize((int(logo.width * 0.75), int(logo.height * 0.75)))
        self.logo_photo = ImageTk.PhotoImage(logo)
        self.canvas.create_image(
            540,
            180,
            image=self.logo_photo
        )

        # Créditos do jogo original
        self.canvas.create_text(
            540,
            300,
            text="Criado por Marc André\n"
                 "Distribuído por Space Cowboys\n"
                 "© 2014 Space Cowboys. Todos os direitos reservados.",
            fill="white",
            font=('Aclonica', 16),
            justify="center"
        )

        # Créditos da versão digital
        self.canvas.create_text(
            540,
            480,
            text="Esta versão digital é uma inspiração acadêmica criada por:\n\n"
                 "Gabriel Rodrigo da Gama\n"
                 "Leonardo de Sousa Marques\n"
                 "Thayse Estevo Teixeira\n\n"
                 "Jogo criado para a disciplina INE5417 - Engenharia de Software I\n"
                 "Universidade Federal de Santa Catarina (UFSC)",
            fill="white",
            font=('Aclonica', 14),
            justify="center"
        )

        # Botão Voltar
        self.botao_voltar_img = Image.open("resources/botoes/botao-voltar.png")
        self.botao_voltar_img = self.botao_voltar_img.resize((150, 70))
        self.botao_voltar_tk = ImageTk.PhotoImage(self.botao_voltar_img)

        self.botao_voltar = self.canvas.create_image(
            100, 50,
            image=self.botao_voltar_tk,
            anchor="center",
            tags="voltar"
        )

        # Bind eventos
        self.canvas.tag_bind("voltar", "<Button-1>", lambda e: self.voltar())
        self.canvas.tag_bind("voltar", "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("voltar", "<Leave>", lambda e: self.canvas.config(cursor=""))

    def voltar(self):
        print(f"Returning to screen: {self.destino_voltar}")
        if self.show_screen:
            self.show_screen(self.destino_voltar)
        else:
            print("Error: show_screen not properly initialized")