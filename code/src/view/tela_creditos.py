from tkinter import *
from PIL import Image, ImageTk

class TelaCreditos:
    def __init__(self, root: Tk, show_screen):
        self.root = root
        self.show_screen = show_screen

        # Frame principal
        self.frame = Frame(self.root)
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

        # Título
        self.canvas.create_text(
            540,  # x = width/2
            100,  # y position for title
            text="Créditos",
            fill="white",
            font=('Aclonica', 36, 'bold')
        )

        # Créditos do jogo original
        self.canvas.create_text(
            540,
            250,
            text="Splendor\n\n"
            "Criado por Marc André\n"
            "Distribuído por Space Cowboys\n"
            "© 2014 Space Cowboys. Todos os direitos reservados.",
            fill="white",
            font=('Aclonica', 16),
            justify="center"
        )

        # Créditos da versão digital
        self.canvas.create_text(
            540,
            450,
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
        self.canvas.create_text(
            50, 30,
            text="Voltar",
            fill="white",
            font=('Aclonica', 14),
            tags="voltar"
        )

        # Bind events
        self.canvas.tag_bind("voltar", "<Button-1>", lambda e: self.voltar())
        self.canvas.tag_bind("voltar", "<Enter>", 
            lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("voltar", "<Leave>", 
            lambda e: self.canvas.config(cursor=""))

    def voltar(self):
        """Handle return to initial screen"""
        print("Returning to initial screen...")  # Debug print
        self.show_screen("inicial")