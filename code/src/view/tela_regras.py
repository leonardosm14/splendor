from tkinter import *
from PIL import Image, ImageTk

class TelaRegras:
    def __init__(self, root: Tk, show_screen):
        self.root = root
        self.show_screen = show_screen  # Save the show_screen function

        # Frame principal
        self.frame = Frame(self.root)
        self.frame.pack(expand=True, fill='both')

        # Canvas para todas as imagens
        self.canvas = Canvas(
            self.frame,
            width=1080,
            height=720,
            highlightthickness=0,
            bg='#352314'  # New background color
        )
        self.canvas.pack()

        # Título
        self.canvas.create_text(
            540,  # x = width/2
            100,  # y position for title
            text="Regras do Jogo",
            fill="white",
            font=('Aclonica-Regular', 36, 'bold')
        )

        # Texto das regras
        texto_regras = (
            "O jogo segue um formato baseado em turnos, com os jogadores "
            "realizando uma de quatro ações em seu turno:\n\n"
            "• Pegar três fichas de gema de cores diferentes\n\n"
            "• Pegar duas fichas de gema da mesma cor\n  (se houver pelo menos "
            "quatro fichas disponíveis)\n\n"
            "• Reservar uma carta de desenvolvimento e pegar uma ficha de ouro\n\n"
            "• Comprar uma carta de desenvolvimento virada para cima do centro\n  "
            "da mesa ou de uma previamente reservada\n\n"
            "Os jogadores devem gerenciar sua contagem de fichas, devolvendo\n"
            "as fichas excedentes para manter um máximo de dez."
        )

        self.canvas.create_text(
            540,  # x = width/2
            360,  # y = height/2
            text=texto_regras,
            fill="white",
            font=('Aclonica-Regular', 14),
            justify="center",
            width=800
        )

        # Botão Voltar (modified)
        self.canvas.create_text(
            50, 30,
            text="Voltar",
            fill="white",
            font=('Aclonica-Regular', 14),
            tags="voltar"
        )

        # Bind events (modified)
        self.canvas.tag_bind("voltar", "<Button-1>", lambda e: self.voltar())
        self.canvas.tag_bind("voltar", "<Enter>", 
            lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind("voltar", "<Leave>", 
            lambda e: self.canvas.config(cursor=""))

    def voltar(self):
        """Handle return to initial screen"""
        print("Returning to initial screen...")  # Debug print
        if self.show_screen:
            self.show_screen("inicial")
        else:
            print("Error: show_screen not properly initialized")